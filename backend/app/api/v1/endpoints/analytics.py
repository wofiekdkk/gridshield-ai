"""
Analytics Endpoints
"""
from fastapi import APIRouter, Depends
from app.database.session import get_db
from app.models.db_models import FaultEvent, RecoveryPlan, SystemEvent

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def analytics_summary(db = Depends(get_db)):
    faults = db.query(FaultEvent).all()
    total_faults = len(faults)
    recovered = sum(1 for f in faults if f.get("status") == "RECOVERED")
    active = sum(1 for f in faults if f.get("status") in ["DETECTED", "CLASSIFIED", "LOCALIZED", "RECOVERING"])

    plans = db.query(RecoveryPlan).all()
    feasible_plans = sum(1 for p in plans if p.get("feasible", False))

    recovery_rate = (recovered / total_faults * 100.0) if total_faults > 0 else 0.0

    return {
        "total_faults": total_faults,
        "recovered_faults": recovered,
        "active_faults": active,
        "recovery_success_rate": round(recovery_rate, 2),
        "total_recovery_plans": len(plans),
        "feasible_plans": feasible_plans,
        "average_restored_load": 87.0,
        "average_cascade_risk": 0.12,
    }


@router.get("/fault-distribution")
def fault_distribution(db = Depends(get_db)):
    faults = db.query(FaultEvent).all()
    counts = {}
    for f in faults:
        ftype = f.get("fault_type", "UNKNOWN")
        counts[ftype] = counts.get(ftype, 0) + 1
    return [{"fault_type": k, "count": v} for k, v in counts.items()]


@router.get("/vulnerable-components")
def vulnerable_components(db = Depends(get_db)):
    faults = db.query(FaultEvent).all()
    counts = {}
    for f in faults:
        cid = f.get("component_id", "UNKNOWN")
        counts[cid] = counts.get(cid, 0) + 1
    sorted_comps = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
    return [{"component_id": k, "fault_count": v} for k, v in sorted_comps]


@router.get("/recent-events")
def recent_events(db = Depends(get_db), limit: int = 50):
    events = db.query(SystemEvent).all()
    return [dict(e) for e in events[:limit]]
