"""
Fault Service - Fault Injection & State Tracking
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.db_models import FaultEvent, SystemEvent
from app.schemas.schemas import FaultInjectionRequest
from app.core.logger import logger


class FaultService:
    def __init__(self):
        self.active_faults: Dict[str, Dict[str, Any]] = {}

    def inject_fault(self, db, request: FaultInjectionRequest) -> FaultEvent:
        now_str = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        rand_hex = uuid.uuid4().hex[:6]
        fault_id = f"F-{now_str}-{rand_hex}"

        fault = FaultEvent(
            fault_id=fault_id,
            component_id=request.component_id,
            fault_type=request.fault_type,
            severity=float(request.severity),
            confidence=0.947,
            cascade_risk=0.82,
            status="DETECTED",
            start_time=datetime.utcnow().isoformat(),
            details={"duration": request.duration, "injected": True},
        )
        db.add(fault)

        event = SystemEvent(
            event_type="FAULT_INJECTED",
            severity="WARNING",
            source="FaultService",
            message=f"Fault {request.fault_type} injected at {request.component_id}",
            details={"fault_id": fault_id, "severity": request.severity},
            timestamp=datetime.utcnow().isoformat(),
        )
        db.add(event)
        db.commit()

        self.active_faults[fault_id] = {
            "fault_id": fault_id,
            "component_id": request.component_id,
            "fault_type": request.fault_type,
            "severity": request.severity,
            "start_time": datetime.utcnow().isoformat(),
        }
        logger.info(f"Fault registered: {fault_id} on {request.component_id}")
        return fault

    def get_active_faults(self, db) -> List[Any]:
        all_faults = db.query(FaultEvent).all()
        return [f for f in all_faults if f.get("status") not in ("RECOVERED", "FAILED")]

    def get_all_faults(self, db, limit: int = 100) -> List[Any]:
        return db.query(FaultEvent).limit(limit).all()

    def get_fault(self, db, fault_id: str) -> Optional[Any]:
        return db.query(FaultEvent).filter(FaultEvent.fault_id == fault_id).first()

    def update_fault_status(self, db, fault_id: str, status: str,
                             confidence: Optional[float] = None,
                             cascade_risk: Optional[float] = None):
        fault = self.get_fault(db, fault_id)
        if not fault:
            return None
        fault["status"] = str(status.value if hasattr(status, "value") else status)
        if confidence is not None:
            fault["confidence"] = float(confidence)
        if cascade_risk is not None:
            fault["cascade_risk"] = float(cascade_risk)
        if fault["status"] in ("RECOVERED", "FAILED"):
            fault["end_time"] = datetime.utcnow().isoformat()
            self.active_faults.pop(fault_id, None)
        db.commit()
        return fault

    def reset_all_faults(self, db):
        faults = db.query(FaultEvent).all()
        for f in faults:
            f["status"] = "RECOVERED"
            f["end_time"] = datetime.utcnow().isoformat()
        self.active_faults.clear()
        db.commit()
        logger.info("All grid faults reset to RECOVERED.")


fault_service = FaultService()
