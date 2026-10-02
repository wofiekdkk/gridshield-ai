"""
Recovery Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.database.session import get_db
from app.schemas.schemas import RecoveryExecuteRequest
from app.services.recovery_service import recovery_service
from app.models.db_models import RecoveryPlan
from app.websockets.manager import manager

router = APIRouter(prefix="/recovery", tags=["Recovery"])


@router.get("/plans")
def list_plans(fault_id: str = None, db = Depends(get_db)):
    q = db.query(RecoveryPlan)
    if fault_id:
        q = q.filter(RecoveryPlan.fault_id == fault_id)
    return [dict(p) for p in q.all()]


@router.get("/plans/{plan_id}")
def get_plan(plan_id: str, db = Depends(get_db)):
    p = db.query(RecoveryPlan).filter(RecoveryPlan.plan_id == plan_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Plan not found")
    return dict(p)


@router.post("/execute")
async def execute_plan(request: RecoveryExecuteRequest, db = Depends(get_db)):
    result = recovery_service.execute_plan(db, request.plan_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Execution failed"))
    await manager.broadcast("recovery_executed", result)
    await manager.broadcast("grid_state_changed", {
        "status": "RECOVERED",
        "restored_load": result.get("restored_load"),
    })
    return result


@router.post("/auto-recover/{fault_id}")
async def auto_recover(fault_id: str, db = Depends(get_db)):
    plans = recovery_service.get_plans_for_fault(db, fault_id)
    if not plans:
        raise HTTPException(status_code=404, detail="No plans found")
    best = recovery_service.select_best_plan(plans)
    if not best:
        raise HTTPException(status_code=400, detail="No feasible plan")
    plan_id = best.get("plan_id") if isinstance(best, dict) else best.plan_id
    result = recovery_service.execute_plan(db, plan_id)
    await manager.broadcast("recovery_executed", result)
    return result
