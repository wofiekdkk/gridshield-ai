"""
AI Endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database.session import get_db
from app.models.db_models import AIPrediction, FaultLocalization
from app.services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/predictions")
def get_predictions(db: Session = Depends(get_db), limit: int = 50):
    return db.query(AIPrediction).order_by(AIPrediction.timestamp.desc()).limit(limit).all()


@router.get("/localizations")
def get_localizations(db: Session = Depends(get_db), limit: int = 50):
    return db.query(FaultLocalization).order_by(FaultLocalization.timestamp.desc()).limit(limit).all()


@router.post("/predict/anomaly")
def predict_anomaly(features: Dict[str, float]):
    return ai_service.detect_anomaly(features)


@router.post("/predict/classify")
def predict_classify(features: Dict[str, float]):
    return ai_service.classify_fault(features)
