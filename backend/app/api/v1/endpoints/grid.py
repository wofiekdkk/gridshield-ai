"""
Grid Endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.services.grid_service import grid_service
from app.models.db_models import GridState, GridComponent

router = APIRouter(prefix="/grid", tags=["Grid"])


@router.get("/state")
def get_grid_state():
    return grid_service.get_state()


@router.get("/components")
def get_components():
    return grid_service.get_components()


@router.post("/simulate")
def run_simulation():
    return grid_service.run_simulation()


@router.get("/history")
def get_history(db: Session = Depends(get_db), limit: int = 50):
    states = db.query(GridState).order_by(GridState.timestamp.desc()).limit(limit).all()
    return [{
        "id": s.id,
        "timestamp": s.timestamp,
        "total_generation": s.total_generation,
        "total_load": s.total_load,
        "max_line_loading": s.max_line_loading,
        "overall_status": s.overall_status,
    } for s in states]
