"""
Data Gateway Service
PRD Section 4.1 - Gateway Layer with:
- Rate limiting (Redis token bucket)
- Circuit breakers
- Retry with exponential backoff
- Provenance capture to MinIO
- Freshness validation
"""

import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

import httpx
from loguru import logger
from redis.asyncio import Redis
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.connectors.base import (
    SourceAdapter,
    Payload,
    HealthStatus,
    SpatialQuery,
    SubsetQuery,
    CapabilityNotSupported,
)
from app.core.config import settings


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    PRD Section 4.1 - Failure isolation
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        success_threshold: int = 2,
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
    
    def call(self, func):
        """Decorator for circuit breaker"""
        async def wrapper(*args, **kwargs):
            if self.state == CircuitState.OPEN:
                # Check if timeout has elapsed
                if (
                    self.last_failure_time
                    and datetime.utcnow() - self.last_failure_time
                    > timedelta(seconds=self.timeout_seconds)
                ):
                    logger.info(f"Circuit breaker transitioning to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitBreakerOpen(
                        f"Circuit breaker OPEN for {self.timeout_seconds}s"
                    )
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            
            except Exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                logger.info("Circuit breaker transitioning to CLOSED")
                self.state = CircuitState.CLOSED
                self.success_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitState.HALF_OPEN:
            logger.warning("Circuit breaker reopening due to failure")
            self.state = CircuitState.OPEN
            self.success_count = 0
        
        elif self.failure_count >= self.failure_threshold:
            logger.error(
                f"Circuit breaker OPEN after {self.failure_count} failures"
            )
            self.state = CircuitState.OPEN


class RateLimiter:
    """
    Token bucket rate limiter using Redis
    PRD Section 4.1 - Rate limiting
    """
    
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def check_limit(
        self,
        key: str,
        max_tokens: int,
        refill_rate: float,
        tokens_requested: int = 1,
    ) -> bool:
        """
        Check if request is allowed under rate limit
        
        Args:
            key: Rate limit key (e.g., "source:incois_erddap")
            max_tokens: Bucket capacity
            refill_rate: Tokens per second
            tokens_requested: Tokens needed for this request
        
        Returns:
            True if allowed, False if rate limited
        """
        
        now = datetime.utcnow().timestamp()
        
        # Redis Lua script for atomic token bucket
        lua_script = """
        local key = KEYS[1]
        local max_tokens = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local tokens_requested = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or max_tokens
        local last_refill = tonumber(bucket[2]) or now
        
        -- Refill tokens based on elapsed time
        local elapsed = now - last_refill
        tokens = math.min(max_tokens, tokens + (elapsed * refill_rate))
        
        -- Check if we have enough tokens
        if tokens >= tokens_requested then
            tokens = tokens - tokens_requested
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 300)  -- 5 minute TTL
            return 1
        else
            return 0
        end
        """
        
        try:
            result = await self.redis.eval(
                lua_script,
                1,
                key,
                max_tokens,
                refill_rate,
                tokens_requested,
                now,
            )
            return bool(result)
        
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # Fail open - allow request if Redis is down
            return True


class ProvenanceCapture:
    """
    Capture and store raw responses for provenance
    PRD Section 4.1 - Provenance to MinIO
    """
    
    def __init__(self, minio_client):
        self.minio = minio_client
    
    async def capture(
        self,
        source_id: str,
        query: Dict[str, Any],
        response: Any,
        retrieved_at: datetime,
    ) -> str:
        """
        Store raw response in MinIO
        
        Returns:
            S3 URL to stored object, or None if MinIO is unavailable
        """
        
        if self.minio is None:
            logger.debug(f"Provenance capture skipped (MinIO not configured): {source_id}")
            return None
        
        # Generate unique key
        query_hash = hashlib.sha256(
            json.dumps(query, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]
        
        timestamp = retrieved_at.strftime("%Y%m%d_%H%M%S")
        key = f"provenance/{source_id}/{timestamp}_{query_hash}.json"
        
        # Prepare payload
        payload = {
            "source_id": source_id,
            "query": query,
            "response": response,
            "retrieved_at": retrieved_at.isoformat(),
        }
        
        try:
            # Store in MinIO
            self.minio.put_object(
                settings.MINIO_BUCKET_RAW,
                key,
                json.dumps(payload, default=str).encode(),
                len(json.dumps(payload, default=str)),
                content_type="application/json",
            )
            
            url = f"s3://{settings.MINIO_BUCKET_RAW}/{key}"
            logger.debug(f"Provenance captured: {url}")
            return url
        
        except Exception as e:
            logger.error(f"Provenance capture failed: {e}")
            return None


class DataGateway:
    """
    Central gateway for all source adapters
    PRD Section 4.1 - Gateway Layer
    
    Provides:
    - Adapter registry
    - Rate limiting
    - Circuit breakers
    - Retry logic
    - Provenance capture
    - Health monitoring
    """
    
    def __init__(self, redis: Redis, minio_client):
        self.redis = redis
        self.rate_limiter = RateLimiter(redis)
        self.provenance = ProvenanceCapture(minio_client)
        
        # Registry of adapters
        self.adapters: Dict[str, SourceAdapter] = {}
        
        # Circuit breakers per source
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Source-specific rate limits (per second)
        self.rate_limits = {
            "incois_erddap": {"max_tokens": 30, "refill_rate": 1.0},
            "imd_weather": {"max_tokens": 60, "refill_rate": 2.0},
            "copernicus_marine": {"max_tokens": 10, "refill_rate": 0.5},
            "mosdac": {"max_tokens": 20, "refill_rate": 1.0},
            "global_fishing_watch": {"max_tokens": 100, "refill_rate": 3.0},
            "obis": {"max_tokens": 60, "refill_rate": 2.0},
        }
    
    def register_adapter(self, adapter: SourceAdapter):
        """Register a source adapter"""
        metadata = adapter.get_metadata()
        source_id = metadata.source_id
        
        self.adapters[source_id] = adapter
        self.circuit_breakers[source_id] = CircuitBreaker()
        
        logger.info(
            f"Registered adapter: {source_id} "
            f"(mode={metadata.interface_type}, verified={metadata.endpoint_verified})"
        )
    
    async def health_check(self, source_id: str) -> HealthStatus:
        """
        Health check with circuit breaker
        PRD Section 4.1 - Health monitoring
        """
        
        adapter = self._get_adapter(source_id)
        circuit = self.circuit_breakers[source_id]
        
        @circuit.call
        async def _check():
            return await adapter.health_check()
        
        try:
            return await _check()
        except CircuitBreakerOpen as e:
            return HealthStatus(
                ok=False,
                latency_ms=0,
                error_code="CIRCUIT_OPEN",
                detail=str(e),
            )
    
    async def get_latest(
        self,
        source_id: str,
        query: SpatialQuery,
        capture_provenance: bool = True,
    ) -> Payload:
        """
        Get latest data with full gateway protections
        PRD Section 4.1 - Gateway pattern
        """
        
        adapter = self._get_adapter(source_id)
        
        # Rate limiting
        await self._check_rate_limit(source_id)
        
        # Circuit breaker + retry logic
        @retry(
            stop=stop_after_attempt(settings.MAX_WORKERS),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        )
        @self.circuit_breakers[source_id].call
        async def _fetch():
            return await adapter.get_latest(query)
        
        try:
            retrieved_at = datetime.utcnow()
            payload = await _fetch()
            
            # Provenance capture
            if capture_provenance:
                provenance_url = await self.provenance.capture(
                    source_id=source_id,
                    query={"type": "get_latest", "params": query.__dict__},
                    response=payload.__dict__,
                    retrieved_at=retrieved_at,
                )
                payload.provenance_url = provenance_url
            
            return payload
        
        except CapabilityNotSupported:
            logger.error(f"Source {source_id} does not support get_latest")
            raise
        
        except CircuitBreakerOpen as e:
            logger.error(f"Circuit breaker open for {source_id}: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Gateway error fetching from {source_id}: {e}")
            raise
    
    async def get_subset(
        self,
        source_id: str,
        query: SubsetQuery,
        capture_provenance: bool = True,
    ) -> List[Payload]:
        """
        Get subset data with full gateway protections
        """
        
        adapter = self._get_adapter(source_id)
        
        # Rate limiting
        await self._check_rate_limit(source_id)
        
        # Circuit breaker + retry logic
        @retry(
            stop=stop_after_attempt(settings.MAX_WORKERS),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        )
        @self.circuit_breakers[source_id].call
        async def _fetch():
            return await adapter.get_subset(query)
        
        try:
            retrieved_at = datetime.utcnow()
            payloads = await _fetch()
            
            # Provenance capture
            if capture_provenance and payloads:
                provenance_url = await self.provenance.capture(
                    source_id=source_id,
                    query={"type": "get_subset", "params": query.__dict__},
                    response=[p.__dict__ for p in payloads],
                    retrieved_at=retrieved_at,
                )
                for payload in payloads:
                    payload.provenance_url = provenance_url
            
            return payloads
        
        except CapabilityNotSupported:
            logger.error(f"Source {source_id} does not support get_subset")
            raise
        
        except CircuitBreakerOpen as e:
            logger.error(f"Circuit breaker open for {source_id}: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Gateway error fetching from {source_id}: {e}")
            raise
    
    def _get_adapter(self, source_id: str) -> SourceAdapter:
        """Get adapter by ID"""
        if source_id not in self.adapters:
            raise ValueError(f"Unknown source: {source_id}")
        return self.adapters[source_id]
    
    async def _check_rate_limit(self, source_id: str):
        """Check rate limit for source"""
        limits = self.rate_limits.get(source_id, {"max_tokens": 60, "refill_rate": 2.0})
        
        allowed = await self.rate_limiter.check_limit(
            key=f"ratelimit:{source_id}",
            max_tokens=limits["max_tokens"],
            refill_rate=limits["refill_rate"],
            tokens_requested=1,
        )
        
        if not allowed:
            raise RateLimitExceeded(f"Rate limit exceeded for {source_id}")
    
    async def get_all_health_status(self) -> Dict[str, HealthStatus]:
        """Check health of all registered sources"""
        results = {}
        
        tasks = [
            self.health_check(source_id)
            for source_id in self.adapters.keys()
        ]
        
        health_statuses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for source_id, status in zip(self.adapters.keys(), health_statuses):
            if isinstance(status, Exception):
                results[source_id] = HealthStatus(
                    ok=False,
                    latency_ms=0,
                    error_code="ERROR",
                    detail=str(status),
                )
            else:
                results[source_id] = status
        
        return results


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open"""
    pass


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""
    pass
