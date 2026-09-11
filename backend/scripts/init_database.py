"""
Database Initialization Script
Creates PostGIS extensions, all tables, and seeds initial data.
Works with the Docker PostGIS container on port 5433.
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from loguru import logger

from app.core.config import settings


async def init_database():
    """Initialize database with PostGIS extensions and all tables."""
    from sqlalchemy.ext.asyncio import create_async_engine

    db_url = settings.DATABASE_URL
    logger.info(f"Connecting to: {db_url.split('@')[-1]}")

    engine = create_async_engine(db_url, echo=False)

    async with engine.begin() as conn:
        # 1. Enable PostGIS extensions
        logger.info("Enabling PostGIS extensions...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
        logger.info("✅ PostGIS extensions enabled")

        # 2. Import all models so Base.metadata knows about them
        logger.info("Importing models...")
        from app.models.base import Base
        from app.models import (
            User, Conversation, Message,
            SourceRegistry, SourceCredentialsMetadata, SourceHealth,
            Dataset, DatasetVariable,
            DataObservation,
            Forecast,
            Warning,
            PFZZone,
            MarineBoundary, ProtectedArea, Bathymetry,
            Recommendation, Route, Evidence,
            AuditLog,
        )
        logger.info("✅ Models imported")

        # 3. Create all tables
        logger.info("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ All tables created")

    # 4. Seed data sources
    logger.info("Seeding data sources...")
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    from app.models.sources import SourceRegistry as SR

    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    sources = [
        {
            "source_id": "incois_erddap",
            "provider": "INCOIS",
            "name": "INCOIS ERDDAP Server",
            "interface_type": "erddap",
            "base_url": "https://erddap.incois.gov.in/erddap/",
            "auth_type": "none",
            "endpoint_verified": True,
            "status": "active",
            "variables": ["CHL", "KD490", "TSM", "SST"],
            "coverage": "Indian Ocean region",
        },
        {
            "source_id": "imd_weather",
            "provider": "India Meteorological Department",
            "name": "IMD Weather API",
            "interface_type": "rest_api",
            "base_url": "https://api.imd.gov.in/api/v1",
            "auth_type": "api_key",
            "endpoint_verified": False,
            "status": "active",
            "variables": ["air_temperature", "wind_speed", "wind_direction", "wave_height", "precipitation"],
            "coverage": "India and Indian Ocean",
        },
        {
            "source_id": "open_meteo_marine",
            "provider": "Open-Meteo",
            "name": "Open-Meteo Marine API",
            "interface_type": "rest_api",
            "base_url": "https://marine-api.open-meteo.com/v1/marine",
            "auth_type": "none",
            "endpoint_verified": True,
            "status": "active",
            "variables": ["wave_height", "wave_direction", "wave_period", "swell_wave_height"],
            "coverage": "Global ocean",
        },
        {
            "source_id": "open_meteo_weather",
            "provider": "Open-Meteo",
            "name": "Open-Meteo Weather API",
            "interface_type": "rest_api",
            "base_url": "https://api.open-meteo.com/v1/forecast",
            "auth_type": "none",
            "endpoint_verified": True,
            "status": "active",
            "variables": ["temperature_2m", "wind_speed_10m", "wind_direction_10m", "relative_humidity_2m"],
            "coverage": "Global",
        },
        {
            "source_id": "copernicus_marine",
            "provider": "Copernicus Marine Service",
            "name": "Copernicus Marine Service",
            "interface_type": "sdk",
            "base_url": "https://data.marine.copernicus.eu/",
            "auth_type": "account",
            "endpoint_verified": True,
            "status": "active" if settings.COPERNICUSMARINE_SERVICE_USERNAME else "inactive",
            "variables": ["sst", "salinity", "current_u", "current_v", "wave_height", "chlorophyll"],
            "coverage": "Global ocean",
        },
    ]

    async with SessionLocal() as session:
        for src in sources:
            existing = await session.execute(
                text("SELECT source_id FROM source_registry WHERE source_id = :sid"),
                {"sid": src["source_id"]}
            )
            if existing.scalar_one_or_none():
                logger.info(f"  Already exists: {src['source_id']}")
                continue
            session.add(SR(**src))
            logger.info(f"  ✅ Added: {src['source_id']}")
        await session.commit()

    # 5. Seed Mumbai fishing ports
    logger.info("Seeding Mumbai fishing ports...")
    ports_sql = """
    INSERT INTO fishing_ports (name, lat, lon, region, geom)
    VALUES (:name, :lat, :lon, :region, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
    ON CONFLICT (name) DO NOTHING
    """

    # First create the fishing_ports table if it doesn't exist
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fishing_ports (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                lat DOUBLE PRECISION NOT NULL,
                lon DOUBLE PRECISION NOT NULL,
                region TEXT,
                geom geometry(Point, 4326)
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fishing_ports_geom ON fishing_ports USING GIST(geom)"))

    mumbai_ports = [
        {"name": "Sassoon Dock & Jetty", "lat": 18.9067, "lon": 72.8333, "region": "Colaba"},
        {"name": "Gateway of India", "lat": 18.9220, "lon": 72.8347, "region": "Colaba"},
        {"name": "Bhaucha Dhakka / Ferry Wharf", "lat": 18.9560, "lon": 72.8505, "region": "Mazgaon"},
        {"name": "Marine Drive Promenade", "lat": 18.9432, "lon": 72.8235, "region": "Girgaon"},
        {"name": "Lotus Jetty & Worli Fort", "lat": 19.0000, "lon": 72.8167, "region": "Worli"},
        {"name": "Bandra-Worli Sea Link Coastline", "lat": 19.0365, "lon": 72.8174, "region": "Bandra"},
        {"name": "Mahim Creek & Causeway", "lat": 19.0410, "lon": 72.8400, "region": "Mahim"},
        {"name": "Juhu Fishing Pier", "lat": 19.0988, "lon": 72.8267, "region": "Juhu"},
        {"name": "Bhati Dock — Madh Island", "lat": 19.1508, "lon": 72.7929, "region": "Madh Island"},
    ]

    async with SessionLocal() as session:
        for port in mumbai_ports:
            await session.execute(text(ports_sql), port)
            logger.info(f"  ✅ Port: {port['name']}")
        await session.commit()

    # 6. Seed mock PFZ zones for Mumbai demo
    logger.info("Seeding PFZ zones...")
    productive_zones = [
        {"lat": 18.8, "lon": 72.5, "sector": "Offshore Mumbai South", "score": 0.85},
        {"lat": 19.2, "lon": 72.4, "sector": "Offshore Mumbai North", "score": 0.78},
        {"lat": 18.5, "lon": 72.0, "sector": "Deep Sea Arabian", "score": 0.90},
    ]

    import uuid
    from datetime import timedelta
    pfz_sql = """
    INSERT INTO pfz_zones (id, source_id, sector, geom, issued_at, valid_until, retrieved_at, attributes)
    VALUES (:id, :source_id, :sector, ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, 4326), :now, :valid_until, :now, :attrs)
    """
    
    now = datetime.utcnow()
    valid_until = now + timedelta(days=3)

    async with SessionLocal() as session:
        for pz in productive_zones:
            half = 0.2
            await session.execute(text(pfz_sql), {
                "id": str(uuid.uuid4()),
                "source_id": "incois_erddap_mock",
                "sector": pz["sector"],
                "xmin": pz["lon"] - half,
                "ymin": pz["lat"] - half,
                "xmax": pz["lon"] + half,
                "ymax": pz["lat"] + half,
                "now": now,
                "valid_until": valid_until,
                "attrs": json.dumps({"confidence_score": pz["score"]})
            })
            logger.info(f"  ✅ PFZ: {pz['sector']}")
        await session.commit()

    await engine.dispose()
    logger.info("🎉 Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_database())
