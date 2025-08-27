from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from app.routers import auth, users, campaigns, analytics, ml_predictions, powerbi, alerts
from app.core.config import settings
from app.core.database import engine, Base
from app.core.security import get_current_user

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Precision Marketing Intelligence Platform...")
    yield
    # Shutdown
    print("🛑 Shutting down Precision Marketing Intelligence Platform...")

# Initialize FastAPI app
app = FastAPI(
    title="Precision Marketing Intelligence Platform",
    description="AI + BI platform that helps companies optimize marketing campaigns with predictive insights and interactive dashboards",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(ml_predictions.router, prefix="/api/ml", tags=["ML Predictions"])
app.include_router(powerbi.router, prefix="/api/powerbi", tags=["Power BI"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])

@app.get("/")
async def root():
    return {
        "message": "Precision Marketing Intelligence Platform",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Precision Marketing Intelligence Platform",
        "timestamp": "2025-08-27T10:00:00Z"
    }

@app.get("/api/features")
async def get_features():
    """Get platform features for the frontend"""
    return {
        "features": [
            {
                "id": "dashboard",
                "name": "Interactive Dashboard",
                "description": "Power BI + Web Integration for real-time insights",
                "icon": "dashboard",
                "enabled": True
            },
            {
                "id": "ai_predictions",
                "name": "AI/ML Predictions",
                "description": "Conversion likelihood, churn risk assessment",
                "icon": "psychology",
                "enabled": True
            },
            {
                "id": "collaboration",
                "name": "Collaboration & Reporting",
                "description": "Share dashboards, generate automated reports",
                "icon": "group_work",
                "enabled": True
            },
            {
                "id": "alerts",
                "name": "Real-Time Alerts",
                "description": "Proactive notifications for CTR drops, rising costs",
                "icon": "notifications_active",
                "enabled": True
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
