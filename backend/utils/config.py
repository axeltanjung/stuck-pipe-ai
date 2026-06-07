from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "StuckPipeAI"
    app_env: str = "development"
    debug: bool = True
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    database_url: str = "sqlite:///./data/stuckpipe.db"
    mlflow_tracking_uri: str = "http://localhost:5000"
    model_path: str = "./data/models"
    default_model: str = "xgboost"
    prediction_threshold: float = 0.5
    alert_refresh_interval: int = 30

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
