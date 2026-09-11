"""
Freshness Manager
PRD Section 9 - Data Freshness Management

Responsibilities:
- Track data age for each source/dataset
- Classify freshness (FRESH, STALE, EXPIRED)
- Trigger refresh when needed
- Enforce freshness policies
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, List
from enum import Enum

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sources import SourceRegistry
from app.models.datasets import Dataset
from app.core.config import settings


class FreshnessStatus(str, Enum):
    """Data freshness classification"""
    FRESH = "fresh"  # Within acceptable age
    STALE = "stale"  # Aging but usable
    EXPIRED = "expired"  # Too old, must refresh
    UNKNOWN = "unknown"  # No timestamp available


class FreshnessPolicy:
    """
    Freshness thresholds per data type
    PRD Section 9.2
    """
    
    # Critical (e.g., live obs, NRT satellite)
    CRITICAL_FRESH_SECONDS = settings.FRESHNESS_CRITICAL  # 5 min
    CRITICAL_STALE_SECONDS = settings.FRESHNESS_CRITICAL * 2  # 10 min
    
    # High priority (e.g., forecasts, warnings)
    HIGH_FRESH_SECONDS = settings.FRESHNESS_HIGH  # 15 min
    HIGH_STALE_SECONDS = settings.FRESHNESS_HIGH * 2  # 30 min
    
    # Medium (e.g., daily aggregates)
    MEDIUM_FRESH_SECONDS = settings.FRESHNESS_MEDIUM  # 1 hour
    MEDIUM_STALE_SECONDS = settings.FRESHNESS_MEDIUM * 4  # 4 hours
    
    # Low (e.g., climatology, baselines)
    LOW_FRESH_SECONDS = settings.FRESHNESS_LOW  # 24 hours
    LOW_STALE_SECONDS = settings.FRESHNESS_LOW * 7  # 7 days
    
    @classmethod
    def get_thresholds(cls, priority: str) -> Dict[str, int]:
        """Get fresh/stale thresholds for priority level"""
        priority_map = {
            "critical": (cls.CRITICAL_FRESH_SECONDS, cls.CRITICAL_STALE_SECONDS),
            "high": (cls.HIGH_FRESH_SECONDS, cls.HIGH_STALE_SECONDS),
            "medium": (cls.MEDIUM_FRESH_SECONDS, cls.MEDIUM_STALE_SECONDS),
            "low": (cls.LOW_FRESH_SECONDS, cls.LOW_STALE_SECONDS),
        }
        
        fresh, stale = priority_map.get(priority, (3600, 7200))
        return {"fresh_seconds": fresh, "stale_seconds": stale}


class FreshnessManager:
    """
    Manage data freshness across all sources
    PRD Section 9
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def check_freshness(
        self,
        source_id: str,
        dataset_id: Optional[str] = None,
        priority: str = "medium",
    ) -> FreshnessStatus:
        """
        Check freshness status for a source/dataset
        
        Args:
            source_id: Source identifier
            dataset_id: Optional dataset identifier
            priority: Freshness priority (critical/high/medium/low)
        
        Returns:
            FreshnessStatus classification
        """
        
        # Get last update timestamp
        last_updated = await self._get_last_update(source_id, dataset_id)
        
        if last_updated is None:
            logger.warning(f"No timestamp for {source_id}/{dataset_id}")
            return FreshnessStatus.UNKNOWN
        
        # Calculate age
        age_seconds = (datetime.utcnow() - last_updated).total_seconds()
        
        # Get thresholds
        thresholds = FreshnessPolicy.get_thresholds(priority)
        
        # Classify
        if age_seconds <= thresholds["fresh_seconds"]:
            return FreshnessStatus.FRESH
        elif age_seconds <= thresholds["stale_seconds"]:
            return FreshnessStatus.STALE
        else:
            return FreshnessStatus.EXPIRED
    
    async def _get_last_update(
        self,
        source_id: str,
        dataset_id: Optional[str] = None,
    ) -> Optional[datetime]:
        """
        Get last update timestamp from database
        
        Priority:
        1. Dataset-level last_ingested_at (if dataset_id provided)
        2. Source-level last_poll_at
        """
        
        if dataset_id:
            # Check dataset-level timestamp
            stmt = select(Dataset.last_ingested_at).where(
                Dataset.source_id == source_id,
                Dataset.dataset_id == dataset_id,
            )
            result = await self.db.execute(stmt)
            timestamp = result.scalar_one_or_none()
            
            if timestamp:
                return timestamp
        
        # Fall back to source-level timestamp
        stmt = select(DataSource.last_poll_at).where(
            DataSource.source_id == source_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def mark_refreshed(
        self,
        source_id: str,
        dataset_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ):
        """
        Update last refresh timestamp
        
        Args:
            source_id: Source identifier
            dataset_id: Optional dataset identifier
            timestamp: Timestamp (defaults to now)
        """
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        if dataset_id:
            # Update dataset-level timestamp
            stmt = (
                select(Dataset)
                .where(
                    Dataset.source_id == source_id,
                    Dataset.dataset_id == dataset_id,
                )
            )
            result = await self.db.execute(stmt)
            dataset = result.scalar_one_or_none()
            
            if dataset:
                dataset.last_ingested_at = timestamp
                await self.db.commit()
                logger.info(f"Marked {source_id}/{dataset_id} refreshed at {timestamp}")
        
        # Always update source-level timestamp
        stmt = select(DataSource).where(DataSource.source_id == source_id)
        result = await self.db.execute(stmt)
        source = result.scalar_one_or_none()
        
        if source:
            source.last_poll_at = timestamp
            await self.db.commit()
            logger.info(f"Marked source {source_id} refreshed at {timestamp}")
    
    async def get_stale_sources(
        self,
        priority: str = "high",
    ) -> List[Dict[str, str]]:
        """
        Find sources that need refresh
        
        Args:
            priority: Minimum priority level to check
        
        Returns:
            List of source/dataset pairs needing refresh
        """
        
        stale_list = []
        
        # Query all active sources
        stmt = select(DataSource).where(DataSource.is_active == True)
        result = await self.db.execute(stmt)
        sources = result.scalars().all()
        
        for source in sources:
            # Check source-level freshness
            freshness = await self.check_freshness(
                source_id=source.source_id,
                priority=priority,
            )
            
            if freshness in (FreshnessStatus.STALE, FreshnessStatus.EXPIRED):
                stale_list.append({
                    "source_id": source.source_id,
                    "dataset_id": None,
                    "freshness": freshness.value,
                    "last_updated": source.last_poll_at.isoformat() if source.last_poll_at else None,
                })
        
        return stale_list
    
    async def requires_refresh(
        self,
        source_id: str,
        dataset_id: Optional[str] = None,
        priority: str = "medium",
    ) -> bool:
        """
        Check if source/dataset requires immediate refresh
        
        Returns:
            True if EXPIRED or UNKNOWN
        """
        
        freshness = await self.check_freshness(source_id, dataset_id, priority)
        return freshness in (FreshnessStatus.EXPIRED, FreshnessStatus.UNKNOWN)
    
    async def get_freshness_report(self) -> Dict[str, Dict]:
        """
        Generate freshness report for all sources
        PRD Section 9.3 - Monitoring
        """
        
        report = {}
        
        # Query all sources
        stmt = select(DataSource)
        result = await self.db.execute(stmt)
        sources = result.scalars().all()
        
        for source in sources:
            # Check freshness at different priority levels
            critical = await self.check_freshness(source.source_id, priority="critical")
            high = await self.check_freshness(source.source_id, priority="high")
            medium = await self.check_freshness(source.source_id, priority="medium")
            
            # Calculate age
            age_seconds = None
            if source.last_poll_at:
                age_seconds = (datetime.utcnow() - source.last_poll_at).total_seconds()
            
            report[source.source_id] = {
                "source_name": source.name,
                "is_active": source.is_active,
                "last_poll_at": source.last_poll_at.isoformat() if source.last_poll_at else None,
                "age_seconds": age_seconds,
                "freshness": {
                    "critical": critical.value,
                    "high": high.value,
                    "medium": medium.value,
                },
                "requires_refresh": await self.requires_refresh(source.source_id),
            }
        
        return report
    
    async def enforce_freshness(
        self,
        source_id: str,
        dataset_id: Optional[str] = None,
        priority: str = "high",
    ):
        """
        Enforce freshness policy - trigger refresh if needed
        PRD Section 9.4 - Active enforcement
        
        This method should be called before serving data to ensure freshness.
        If data is EXPIRED, it triggers a background refresh task.
        """
        
        if await self.requires_refresh(source_id, dataset_id, priority):
            logger.warning(
                f"Data EXPIRED for {source_id}/{dataset_id}, triggering refresh"
            )
            
            # TODO: Trigger Celery task to refresh source
            # from app.workers.tasks import refresh_source_task
            # refresh_source_task.delay(source_id, dataset_id)
            
            raise DataExpiredException(
                f"Data for {source_id}/{dataset_id} is expired and requires refresh"
            )


class DataExpiredException(Exception):
    """Raised when data is too old and requires refresh"""
    pass
