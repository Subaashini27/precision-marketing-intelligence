from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Precision Marketing Intelligence API",
    description="Fresh start API for marketing analytics platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "🚀 PMI API is running!", "status": "success", "version": "1.0.0"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is operational"}

# Mock analytics data
@app.get("/api/analytics")
async def get_analytics():
    return {
        "revenue": "$2.4M",
        "campaigns": 156,
        "conversion_rate": "89%",
        "leads": "24.5K",
        "trend": "up",
        "last_updated": "2025-09-01"
    }

# Mock campaigns data
@app.get("/api/campaigns")
async def get_campaigns():
    return {
        "active_campaigns": [
            {"id": 1, "name": "Summer Sale 2025", "status": "active", "budget": "$50,000", "roi": "245%"},
            {"id": 2, "name": "Product Launch", "status": "active", "budget": "$75,000", "roi": "312%"},
            {"id": 3, "name": "Brand Awareness", "status": "paused", "budget": "$30,000", "roi": "189%"}
        ],
        "total_campaigns": 156
    }

# Mock ML predictions
@app.get("/api/predictions")
async def get_predictions():
    return {
        "next_month_revenue": "$2.8M",
        "recommended_budget": "$120,000",
        "best_performing_channel": "Social Media",
        "predicted_conversion_rate": "92%",
        "confidence": "87%"
    }

if __name__ == "__main__":
    print("🚀 Starting PMI API Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
