from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Precision Marketing Intelligence Platform",
    description="AI + BI platform that helps companies optimize marketing campaigns with predictive insights and interactive dashboards",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    print("🚀 Starting Precision Marketing Intelligence Platform...")
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
