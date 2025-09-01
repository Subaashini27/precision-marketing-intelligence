from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import asyncio
import logging

# Import our email service
try:
    from app.services.email_service import email_service
except ImportError:
    email_service = None
    logging.warning("Email service not available - notifications will be web-only")

router = APIRouter()

class UserPreferences(BaseModel):
    """User notification preferences"""
    email: Optional[EmailStr] = None
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False

class AlertMessage(BaseModel):
    type: str
    title: str
    message: str
    severity: str = "info"
    metadata: Dict[str, Any] = {}
    send_email: bool = True
    email_recipients: Optional[List[EmailStr]] = None

active_connections: List[WebSocket] = []
user_preferences: Dict[str, UserPreferences] = {}

# Sample user data with email preferences
default_users = {
    "admin": UserPreferences(
        email="admin@company.com",
        email_notifications=True,
        push_notifications=True,
        sms_notifications=False
    ),
    "manager": UserPreferences(
        email="manager@company.com", 
        email_notifications=True,
        push_notifications=True,
        sms_notifications=True
    )
}
user_preferences.update(default_users)


async def send_email_notification(alert: AlertMessage):
    """Send email notification for alerts"""
    if not email_service or not alert.send_email:
        return False
    
    try:
        # Determine recipients
        recipients = []
        
        if alert.email_recipients:
            recipients.extend(alert.email_recipients)
        else:
            # Send to all users with email notifications enabled
            for user_id, prefs in user_preferences.items():
                if prefs.email_notifications and prefs.email:
                    recipients.append(prefs.email)
        
        if not recipients:
            logging.info("No email recipients configured for alert")
            return False
        
        # Extract metrics and recommendations from metadata
        metrics = alert.metadata.get('metrics', [])
        recommendations = alert.metadata.get('recommendations', [])
        
        # Send the email
        success = await email_service.send_alert_email(
            recipients=recipients,
            alert_type=alert.type,
            title=alert.title,
            message=alert.message,
            severity=alert.severity,
            metrics=metrics,
            recommendations=recommendations
        )
        
        if success:
            logging.info(f"Alert email sent successfully to {len(recipients)} recipients")
        else:
            logging.error("Failed to send alert email")
            
        return success
        
    except Exception as e:
        logging.error(f"Error sending email notification: {str(e)}")
        return False


async def broadcast(message: Dict[str, Any]):
    living_connections: List[WebSocket] = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
            living_connections.append(connection)
        except Exception:
            # Drop dead connection
            pass
    active_connections.clear()
    active_connections.extend(living_connections)


@router.websocket("/ws/alerts")
async def alerts_ws(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        await websocket.send_json({
            "type": "heartbeat",
            "message": "connected",
            "timestamp": datetime.utcnow().isoformat()
        })
        while True:
            # Keep connection alive; optionally receive pings from client
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)


@router.post("/publish")
async def publish_alert(alert: AlertMessage):
    payload = {
        "type": alert.type,
        "title": alert.title,
        "message": alert.message,
        "severity": alert.severity,
        "metadata": alert.metadata,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Send web notifications
    await broadcast(payload)
    
    # Send email notifications if enabled
    email_sent = False
    if alert.send_email:
        email_sent = await send_email_notification(alert)
    
    return {
        "delivered": len(active_connections),
        "email_sent": email_sent,
        "email_recipients": len(alert.email_recipients) if alert.email_recipients else len([u for u in user_preferences.values() if u.email_notifications])
    }


@router.post("/user-preferences/{user_id}")
async def update_user_preferences(user_id: str, preferences: UserPreferences):
    """Update user notification preferences"""
    user_preferences[user_id] = preferences
    return {"message": f"Preferences updated for user {user_id}", "preferences": preferences}


@router.get("/user-preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get user notification preferences"""
    if user_id not in user_preferences:
        # Return default preferences
        return UserPreferences()
    return user_preferences[user_id]


@router.post("/test-email")
async def test_email_notification(
    recipients: List[EmailStr],
    test_type: str = "alert"
):
    """Send test email notification"""
    if not email_service:
        raise HTTPException(status_code=503, detail="Email service not configured")
    
    try:
        if test_type == "alert":
            success = await email_service.send_alert_email(
                recipients=recipients,
                alert_type="test",
                title="Test Marketing Alert",
                message="This is a test email notification from your Precision Marketing Intelligence Platform. If you receive this, your email notifications are working correctly!",
                severity="low",
                metrics=[
                    {"name": "Test Revenue", "value": "rm12,500", "change": "+5.2%"},
                    {"name": "Test Conversion Rate", "value": "4.8%", "change": "+0.3%"}
                ],
                recommendations=[
                    "This is a test recommendation",
                    "Email notifications are working properly",
                    "You can now receive real-time alerts"
                ]
            )
        elif test_type == "campaign":
            success = await email_service.send_campaign_update_email(
                recipients=recipients,
                campaign_data={
                    "campaign_name": "Test Campaign",
                    "budget": "25,000",
                    "spent": "12,500",
                    "impressions": "45,230",
                    "clicks": "1,890",
                    "ctr": "4.2",
                    "cpc": "6.61",
                    "conversion_rate": "3.8",
                    "roas": "2.1"
                }
            )
        elif test_type == "report":
            success = await email_service.send_weekly_report_email(
                recipients=recipients,
                report_data={
                    "week_start": "2024-01-01",
                    "week_end": "2024-01-07",
                    "total_revenue": "48,500",
                    "revenue_change": "+12.5%",
                    "revenue_trend": "up",
                    "total_conversions": "245",
                    "conversion_change": "+8.3%",
                    "conversion_trend": "up",
                    "website_visitors": "12,458",
                    "visitor_change": "+15.2%",
                    "visitor_trend": "up",
                    "active_campaigns": "12",
                    "campaign_change": "+2",
                    "campaign_trend": "up",
                    "top_campaigns": [
                        {"name": "Summer Sale", "revenue": "18,500", "performance": "85"},
                        {"name": "Product Launch", "revenue": "15,200", "performance": "78"},
                        {"name": "Brand Awareness", "revenue": "14,800", "performance": "72"}
                    ],
                    "ai_insights": [
                        "Increase Facebook ad spend by 20% for optimal ROI",
                        "Focus on mobile users - 65% higher conversion rate",
                        "Weekend campaigns show 32% better performance",
                        "Email campaigns have the highest customer lifetime value"
                    ]
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid test type")
        
        if success:
            return {"message": f"Test {test_type} email sent successfully", "recipients": len(recipients)}
        else:
            raise HTTPException(status_code=500, detail="Failed to send test email")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending test email: {str(e)}")


@router.post("/configure-email")
async def configure_email_provider(
    provider: str,
    email: str,
    password: str,
    smtp_server: Optional[str] = None,
    smtp_port: Optional[int] = None
):
    """Configure email provider settings"""
    if not email_service:
        raise HTTPException(status_code=503, detail="Email service not available")
    
    try:
        if provider.lower() == "gmail":
            from app.services.email_service import setup_gmail
            setup_gmail(email, password)
        elif provider.lower() == "outlook":
            from app.services.email_service import setup_outlook
            setup_outlook(email, password)
        elif provider.lower() == "custom" and smtp_server:
            from app.services.email_service import setup_custom_smtp
            setup_custom_smtp(email, password, smtp_server, smtp_port or 587)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider or missing SMTP settings")
        
        return {"message": f"Email provider '{provider}' configured successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configuring email provider: {str(e)}")


@router.get("/email-providers")
async def get_available_email_providers():
    """Get list of available email providers"""
    return {
        "providers": [
            {
                "name": "gmail",
                "display_name": "Gmail",
                "description": "Google Gmail with App Password",
                "setup_required": ["email", "app_password"]
            },
            {
                "name": "outlook",
                "display_name": "Outlook/Hotmail",
                "description": "Microsoft Outlook/Hotmail",
                "setup_required": ["email", "password"]
            },
            {
                "name": "custom",
                "display_name": "Custom SMTP",
                "description": "Custom SMTP server",
                "setup_required": ["email", "password", "smtp_server", "smtp_port"]
            }
        ]
    }



