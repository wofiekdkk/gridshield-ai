"""
Faults API Endpoints - Fault Injection Pipeline
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.database.session import get_db
from app.schemas.schemas import FaultInjectionRequest
from app.services.fault_service import fault_service
from app.services.ai_service import ai_service
from app.services.recovery_service import recovery_service
from app.websockets.manager import manager
from app.core.logger import logger

router = APIRouter(prefix="/faults", tags=["Faults"])


@router.get("")
def list_faults(active_only: bool = False, db = Depends(get_db)):
    if active_only:
        return [dict(f) for f in fault_service.get_active_faults(db)]
    return [dict(f) for f in fault_service.get_all_faults(db)]


@router.get("/{fault_id}")
def get_fault(fault_id: str, db = Depends(get_db)):
    f = fault_service.get_fault(db, fault_id)
    if not f:
        raise HTTPException(status_code=404, detail="Fault not found")
    return dict(f)


@router.post("/inject")
async def inject_fault(request: FaultInjectionRequest, db = Depends(get_db)):
    try:
        fault = fault_service.inject_fault(db, request)
        fid = fault.get("fault_id")

        features = {
            "voltage": 180.0 if "VOLTAGE" in request.fault_type else 230.0,
            "current": 220.0 if "OVERLOAD" in request.fault_type else 100.0,
            "frequency": 49.3 if "FREQUENCY" in request.fault_type else 50.0,
            "temperature": 90.0 if "TRANSFORMER" in request.fault_type else 42.0,
            "load_percentage": 110.0 if "OVERLOAD" in request.fault_type else 72.0,
            "active_power": 95.0,
            "reactive_power": 20.0,
            "power_factor": 0.92,
        }

        # 1. Anomaly Detection
        anomaly = ai_service.detect_anomaly(features)
        await manager.broadcast("anomaly_detected", {"fault_id": fid, **anomaly})

        # 2. Classification
        classification = ai_service.classify_fault(features, fault_hint=request.fault_type)
        ai_service.save_prediction(db, fid, "classifier", classification)
        await manager.broadcast("fault_classified", {"fault_id": fid, **classification})

        # 3. Localization
        localization = ai_service.localize_fault(request.component_id)
        ai_service.save_localization(db, fid, localization)
        await manager.broadcast("fault_localized", {"fault_id": fid, **localization})

        # 4. Cascade Prediction
        cascade = ai_service.predict_cascade_risk(request.component_id, request.severity)
        await manager.broadcast("cascade_predicted", {"fault_id": fid, **cascade})

        # 5. Update Status
        fault_service.update_fault_status(
            db, fid, "LOCALIZED",
            confidence=classification.get("confidence", 0.947),
            cascade_risk=cascade.get("cascade_risk", 0.82),
        )

        # 6. Generate Recovery Plans
        plans = recovery_service.generate_plans(db, fault)
        await manager.broadcast("recovery_plans_generated", {
            "fault_id": fid,
            "plan_count": len(plans),
            "plans": [
                {
                    "plan_id": p.get("plan_id"),
                    "feasible": p.get("feasible"),
                    "restored_load": p.get("restored_load"),
                    "cascade_risk": p.get("cascade_risk"),
                    "objective_score": p.get("objective_score"),
                }
                for p in plans
            ],
        })

        await manager.broadcast("fault_detected", {
            "fault_id": fid,
            "component_id": fault.get("component_id"),
            "fault_type": fault.get("fault_type"),
            "severity": fault.get("severity"),
            "confidence": fault.get("confidence"),
            "cascade_risk": fault.get("cascade_risk"),
            "status": "LOCALIZED",
        })

        return {
            "fault_id": fid,
            "component_id": fault.get("component_id"),
            "fault_type": fault.get("fault_type"),
            "severity": fault.get("severity"),
            "confidence": fault.get("confidence"),
            "cascade_risk": fault.get("cascade_risk"),
            "status": "LOCALIZED",
            "start_time": fault.get("start_time"),
            "plans_generated": len(plans),
        }
    except Exception as e:
        logger.error(f"Fault injection pipeline failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_faults(db = Depends(get_db)):
    fault_service.reset_all_faults(db)
    await manager.broadcast("grid_reset", {"message": "All faults cleared"})
    return {"success": True, "message": "All faults reset"}
