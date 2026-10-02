"""
Main API Router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, grid, sensors, faults, recovery, ai, analytics, websocket

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(grid.router)
api_router.include_router(sensors.router)
api_router.include_router(faults.router)
api_router.include_router(recovery.router)
api_router.include_router(ai.router)
api_router.include_router(analytics.router)
api_router.include_router(websocket.router)
