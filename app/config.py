import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # Celery Configuration
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
