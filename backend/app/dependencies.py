"""
Dependency Injection
FastAPI dependency providers for services, database, agents, etc.
"""

from typing import AsyncGenerator
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from minio import Minio
from loguru import logger

from app.core.database import get_db
from app.core.config import settings
from app.services.gateway import DataGateway
from app.services.freshness import FreshnessManager
from app.agents.base import AgentOrchestrator
from app.agents.conversation import ConversationAgent
from app.agents.planner import PlannerAgent
from app.agents.pfz_intelligence import PFZIntelligenceAgent
from app.agents.ocean_intelligence import OceanIntelligenceAgent
from app.agents.weather_intelligence import WeatherIntelligenceAgent

# Security
security = HTTPBearer(auto_error=False)


# ===== Redis Connection =====

@lru_cache()
def get_redis_client() -> Redis:
    """Get Redis client (singleton)"""
    redis_client = Redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    logger.info("Redis client initialized")
    return redis_client


async def get_redis() -> AsyncGenerator[Redis, None]:
    """Dependency for Redis connection"""
    redis = get_redis_client()
    try:
        yield redis
    finally:
        # Connection pooling handles cleanup
        pass


# ===== MinIO/S3 Client =====

@lru_cache()
def get_minio_client() -> Minio:
    """Get MinIO client (singleton)"""
    
    # Parse endpoint to remove protocol
    endpoint = settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
    
    client = Minio(
        endpoint=endpoint,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False,  # Use True for HTTPS in production
    )
    
    logger.info(f"MinIO client initialized: {endpoint}")
    return client


def get_minio() -> Minio:
    """Dependency for MinIO client"""
    return get_minio_client()


# ===== LLM Client =====

@lru_cache()
def get_llm_client():
    """
    Get LLM client based on provider configuration
    
    Supports:
    - Groq (fast, affordable)
    - OpenAI
    - Anthropic
    """
    
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "groq":
        from groq import AsyncGroq
        client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        logger.info("Groq client initialized")
        return client
    
    elif provider == "openai":
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("OpenAI client initialized")
        return client
    
    elif provider == "anthropic":
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=settings.OPENAI_API_KEY)
        logger.info("Anthropic client initialized")
        return client
    
    else:
        logger.warning(f"Unknown LLM provider: {provider}, defaulting to Groq")
        from groq import AsyncGroq
        return AsyncGroq(api_key=settings.GROQ_API_KEY)


# ===== Data Gateway =====

_gateway_instance = None


async def get_gateway(
    redis: Redis = Depends(get_redis),
    minio: Minio = Depends(get_minio),
) -> DataGateway:
    """
    Dependency for Data Gateway
    
    Gateway is a singleton that manages all source adapters
    """
    global _gateway_instance
    
    if _gateway_instance is None:
        logger.info("Initializing Data Gateway")
        _gateway_instance = DataGateway(redis, minio)
        
        # Register all adapters
        await _initialize_adapters(_gateway_instance)
    
    return _gateway_instance


async def _initialize_adapters(gateway: DataGateway):
    """Register all source adapters with the gateway"""
    
    from app.connectors.incois_erddap import INCOISERDDAPAdapter
    from app.connectors.imd_weather import IMDWeatherAdapter
    from app.connectors.copernicus_marine import CopernicusMarineAdapter
    from app.connectors.mosdac import MOSDACAdapter
    
    # Register adapters
    adapters = [
        INCOISERDDAPAdapter(),
        IMDWeatherAdapter(),
        CopernicusMarineAdapter(),
        MOSDACAdapter(),
    ]
    
    for adapter in adapters:
        gateway.register_adapter(adapter)
    
    logger.info(f"Registered {len(adapters)} source adapters")


# ===== Freshness Manager =====

async def get_freshness_manager(
    db: AsyncSession = Depends(get_db),
) -> FreshnessManager:
    """Dependency for Freshness Manager"""
    return FreshnessManager(db)


# ===== Agent Orchestrator =====

_orchestrator_instance = None


async def get_agent_orchestrator(
    gateway: DataGateway = Depends(get_gateway),
) -> AgentOrchestrator:
    """
    Dependency for Agent Orchestrator
    
    Orchestrator is a singleton that manages all agents
    """
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        logger.info("Initializing Agent Orchestrator")
        
        llm_client = get_llm_client()
        _orchestrator_instance = AgentOrchestrator(llm_client)
        
        # Register all agents
        _orchestrator_instance.register_agent(ConversationAgent(llm_client))
        _orchestrator_instance.register_agent(PlannerAgent(llm_client))
        _orchestrator_instance.register_agent(PFZIntelligenceAgent(llm_client, gateway))
        _orchestrator_instance.register_agent(OceanIntelligenceAgent(llm_client, gateway))
        _orchestrator_instance.register_agent(WeatherIntelligenceAgent(llm_client, gateway))
        
        logger.info("Agent Orchestrator initialized with 5 agents")
    
    return _orchestrator_instance


# ===== Authentication =====

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """
    Dependency for authenticated user
    
    Validates JWT token and returns user
    """
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # TODO: Implement JWT validation
    # from app.core.security import verify_token
    # payload = verify_token(token)
    # user_id = payload.get("sub")
    
    # TODO: Fetch user from database
    # from app.models.users import User
    # stmt = select(User).where(User.id == user_id)
    # result = await db.execute(stmt)
    # user = result.scalar_one_or_none()
    
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid authentication credentials",
    #     )
    
    # return user
    
    # Placeholder - return mock user for development
    logger.warning("Using mock authentication - implement JWT validation")
    return {"id": 1, "email": "dev@orca.local", "role": "admin"}


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
):
    """Dependency for active user (not disabled)"""
    
    # TODO: Check if user is active
    # if not current_user.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Inactive user",
    #     )
    
    return current_user


# ===== Optional Authentication =====

async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Optional authentication - returns user if authenticated, None otherwise
    
    Useful for endpoints that work with or without authentication
    """
    
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# ===== Admin Check =====

async def require_admin(
    current_user: dict = Depends(get_current_active_user),
):
    """Dependency to require admin role"""
    
    # TODO: Check user role
    # if current_user.role != "admin":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin access required",
    #     )
    
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return current_user


# ===== Rate Limiting =====

async def check_rate_limit(
    redis: Redis = Depends(get_redis),
    user: dict = Depends(get_optional_user),
):
    """
    Check API rate limit
    
    Different limits for:
    - Anonymous users
    - Authenticated users
    - Premium users
    """
    
    # Determine rate limit based on user
    if not user:
        # Anonymous: 10 requests per minute
        key = "ratelimit:anon"
        limit = 10
    elif user.get("role") == "premium":
        # Premium: 1000 requests per minute
        key = f"ratelimit:user:{user['id']}"
        limit = 1000
    else:
        # Regular: 100 requests per minute
        key = f"ratelimit:user:{user['id']}"
        limit = 100
    
    # Check limit using Redis
    try:
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, 60)  # 1 minute window
        
        if count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )
    
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        # Fail open - allow request if Redis is down
        pass
