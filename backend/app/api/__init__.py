"""
ORCA API Router
Aggregates all API endpoints
"""

from fastapi import APIRouter

# Import endpoint router
from app.api.endpoints import router

api_router = APIRouter()

# Include endpoint modules
api_router.include_router(router, tags=["ORCA API"])

