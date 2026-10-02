"""
Recovery Service - Plan Generation & Execution
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.db_models import RecoveryPlan, RecoveryAction, FaultEvent, SystemEvent
from app.core.logger import logger


class RecoveryService:
    def generate_plans(self, db, fault) -> List[Any]:
        fid = fault.get("fault_id") if isinstance(fault, dict) else getattr(fault, "fault_id", "F-001")
        cid = fault.get("component_id") if isinstance(fault, dict) else getattr(fault, "component_id", "LINE_7")
        base = f"RP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        plan_a = RecoveryPlan(
            plan_id=f"{base}-A",
            fault_id=fid,
            actions=[
                {"action": "ISOLATE", "component": cid},
                {"action": "REROUTE", "component": "LINE_3", "via": "LINE_4"},
                {"action": "RESTORE_LOAD", "amount": 95},
            ],
            restored_load=95.0,
            cascade_risk=0.74,
            max_line_loading=1.08,
            constraint_violations=["LINE_3_OVERLOAD"],
            feasible=False,
            objective_score=0.42,
            selected=False,
            created_at=datetime.utcnow().isoformat(),
        )

        plan_b = RecoveryPlan(
            plan_id=f"{base}-B",
            fault_id=fid,
            actions=[
                {"action": "ISOLATE", "component": cid},
                {"action": "REROUTE", "component": "LINE_5", "via": "LINE_6"},
                {"action": "SHED_NONCRITICAL", "amount": 8},
                {"action": "RESTORE_CRITICAL", "amount": 30},
            ],
            restored_load=87.0,
            cascade_risk=0.08,
            max_line_loading=0.91,
            constraint_violations=[],
            feasible=True,
            objective_score=0.91,
            selected=False,
            created_at=datetime.utcnow().isoformat(),
        )

        plan_c = RecoveryPlan(
            plan_id=f"{base}-C",
            fault_id=fid,
            actions=[
                {"action": "ISOLATE", "component": cid},
                {"action": "SHED_NONCRITICAL", "amount": 20},
                {"action": "RESTORE_CRITICAL", "amount": 30},
            ],
            restored_load=72.0,
            cascade_risk=0.03,
            max_line_loading=0.78,
            constraint_violations=[],
            feasible=True,
            objective_score=0.78,
            selected=False,
            created_at=datetime.utcnow().isoformat(),
        )

        plans = [plan_a, plan_b, plan_c]
        for p in plans:
            db.add(p)
        db.commit()

        logger.info(f"Generated 3 recovery plans for fault {fid}")
        return plans

    def select_best_plan(self, plans: List[Any]) -> Optional[Any]:
        feasible = [p for p in plans if p.get("feasible", False)]
        if not feasible:
            return None
        return max(feasible, key=lambda p: float(p.get("objective_score", 0.0) or 0.0))

    def execute_plan(self, db, plan_id: str) -> Dict[str, Any]:
        plan = db.query(RecoveryPlan).filter(RecoveryPlan.plan_id == plan_id).first()
        if not plan:
            return {"success": False, "error": "Plan not found"}
        if not plan.get("feasible", False):
            return {"success": False, "error": "Plan is not feasible"}

        plan["selected"] = True

        for action in (plan.get("actions") or []):
            ra = RecoveryAction(
                fault_id=plan.get("fault_id"),
                plan_id=plan.get("plan_id"),
                action_type=action.get("action", "UNKNOWN"),
                component=action.get("component", ""),
                previous_state="ACTIVE",
                new_state="RECONFIGURED",
                result="SUCCESS",
                executed_at=datetime.utcnow().isoformat(),
            )
            db.add(ra)

        fid = plan.get("fault_id")
        fault = db.query(FaultEvent).filter(FaultEvent.fault_id == fid).first()
        if fault:
            fault["status"] = "RECOVERED"
            fault["end_time"] = datetime.utcnow().isoformat()

        event = SystemEvent(
            event_type="RECOVERY_EXECUTED",
            severity="INFO",
            source="RecoveryService",
            message=f"Recovery plan {plan_id} executed successfully",
            details={"restored_load": plan.get("restored_load"), "cascade_risk": plan.get("cascade_risk")},
            timestamp=datetime.utcnow().isoformat(),
        )
        db.add(event)
        db.commit()

        logger.info(f"Executed recovery plan {plan_id}")
        return {
            "success": True,
            "plan_id": plan_id,
            "actions_executed": len(plan.get("actions", [])),
            "restored_load": plan.get("restored_load"),
            "cascade_risk": plan.get("cascade_risk"),
        }

    def get_plans_for_fault(self, db, fault_id: str) -> List[Any]:
        return db.query(RecoveryPlan).filter(RecoveryPlan.fault_id == fault_id).all()


recovery_service = RecoveryService()
