"""
Sensors Endpoints
"""
from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime
from app.database.session import get_db
from app.models.db_models import SensorReading, Sensor
from app.schemas.schemas import SensorReadingCreate
from app.websockets.manager import manager
import asyncio

router = APIRouter(prefix="/sensors", tags=["Sensors"])


@router.get("")
def list_latest_readings(limit: int = 100, db = Depends(get_db)):
    readings = db.query(SensorReading).limit(limit).all()
    return [dict(r) for r in readings]


@router.get("/{sensor_id}/readings")
def get_sensor_readings(sensor_id: str, limit: int = 100, db = Depends(get_db)):
    readings = db.query(SensorReading).filter(SensorReading.sensor_id == sensor_id).limit(limit).all()
    return [dict(r) for r in readings]


@router.post("/ingest")
async def ingest_reading(reading: SensorReadingCreate, db = Depends(get_db)):
    data = reading.model_dump(exclude_none=True)
    if not data.get("timestamp"):
        data["timestamp"] = datetime.utcnow().isoformat()
    
    row = SensorReading(**data)
    db.add(row)
    db.commit()

    asyncio.create_task(manager.broadcast("sensor_update", {
        "sensor_id": row.get("sensor_id"),
        "component_id": row.get("component_id"),
        "voltage": row.get("voltage"),
        "current": row.get("current"),
        "frequency": row.get("frequency"),
        "temperature": row.get("temperature"),
        "load_percentage": row.get("load_percentage"),
        "status": row.get("status", "NORMAL"),
        "timestamp": str(row.get("timestamp")),
    }))
    return dict(row)


@router.get("/list")
def list_sensors(db = Depends(get_db)):
    return [dict(s) for s in db.query(Sensor).all()]
