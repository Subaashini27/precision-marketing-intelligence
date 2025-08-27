from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    
    # Analytics metadata
    data_source = Column(String(100), nullable=False)  # google_analytics, facebook, linkedin, etc.
    metric_date = Column(DateTime(timezone=True), nullable=False)
    metric_period = Column(String(20), nullable=False)  # daily, weekly, monthly
    
    # Core metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    
    # Calculated metrics
    ctr = Column(Float, default=0.0)  # Click-through rate
    cpc = Column(Float, default=0.0)  # Cost per click
    cpa = Column(Float, default=0.0)  # Cost per acquisition
    roas = Column(Float, default=0.0)  # Return on ad spend
    conversion_rate = Column(Float, default=0.0)
    
    # Channel-specific metrics
    channel = Column(String(100), nullable=True)
    ad_group = Column(String(255), nullable=True)
    keyword = Column(String(255), nullable=True)
    placement = Column(String(255), nullable=True)
    
    # Audience metrics
    reach = Column(Integer, default=0)
    frequency = Column(Float, default=0.0)
    unique_visitors = Column(Integer, default=0)
    returning_visitors = Column(Integer, default=0)
    
    # Engagement metrics
    time_on_site = Column(Float, default=0.0)
    bounce_rate = Column(Float, default=0.0)
    page_views = Column(Integer, default=0)
    social_shares = Column(Integer, default=0)
    
    # Custom dimensions
    custom_dimensions = Column(JSON, nullable=True)  # JSON object with custom metrics
    segments = Column(JSON, nullable=True)  # JSON array of audience segments
    
    # Data quality
    data_confidence = Column(Float, default=1.0)  # 0.0 to 1.0
    is_estimated = Column(Boolean, default=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analytics")
    campaign = relationship("Campaign", back_populates="analytics")
    
    def __repr__(self):
        return f"<Analytics(id={self.id}, date='{self.metric_date}', source='{self.data_source}')>"
    
    @property
    def is_performing_well(self):
        """Check if metrics indicate good performance"""
        if self.ctr >= 0.02 and self.conversion_rate >= 0.01 and self.roas >= 2.0:
            return True
        return False
    
    @property
    def needs_attention(self):
        """Check if metrics indicate issues that need attention"""
        if self.ctr < 0.005 or self.conversion_rate < 0.005 or self.roas < 1.0:
            return True
        return False
    
    @property
    def trend_direction(self):
        """Determine trend direction based on metrics"""
        # This would typically compare with previous period data
        # For now, return neutral
        return "neutral"
    
    @property
    def efficiency_score(self):
        """Calculate overall efficiency score"""
        if self.impressions == 0:
            return 0
        
        # Weighted score based on multiple metrics
        ctr_score = min(self.ctr * 1000, 100)
        conversion_score = min(self.conversion_rate * 1000, 100)
        roas_score = min(self.roas * 10, 100)
        
        return (ctr_score * 0.3 + conversion_score * 0.4 + roas_score * 0.3)
