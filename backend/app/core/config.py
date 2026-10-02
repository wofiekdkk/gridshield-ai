"""
Backend Configuration Settings with Fallback for Offline Environments
"""
import os
from typing import List

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback if pydantic_settings is not installed (uses standard Pydantic)
    try:
        from pydantic import BaseModel as BaseSettings  # type: ignore
    except ImportError:
        class BaseSettings:  # type: ignore
            def __init__(self, **kwargs):
                pass

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "GridShield AI Backend"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./gridshield.db"
    DATABASE_ECHO: bool = False

    # Security
    SECRET_KEY: str = "gridshield-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # MQTT
    MQTT_BROKER: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""

    # AI Models
    MODEL_DIR: str = "D:/gridshield-ai/ml/models"
    ANOMALY_MODEL_PATH: str = "D:/gridshield-ai/ml/models/anomaly_detector.pkl"
    CLASSIFIER_MODEL_PATH: str = "D:/gridshield-ai/ml/models/fault_classifier.pkl"

    # Simulation
    SIMULATION_INTERVAL: float = 2.0
    SENSOR_PUBLISH_INTERVAL: float = 1.0

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "D:/gridshield-ai/backend/logs/backend.log"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
