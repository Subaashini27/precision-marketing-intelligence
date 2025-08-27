from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Campaign details
    campaign_type = Column(String(50), nullable=False)  # email, social, ppc, content
    status = Column(String(50), default="draft")  # draft, active, paused, completed
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Budget and goals
    budget = Column(Float, nullable=True)
    target_audience = Column(Text, nullable=True)
    goals = Column(JSON, nullable=True)  # JSON object with KPIs
    
    # Performance metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    
    # Calculated metrics
    ctr = Column(Float, default=0.0)  # Click-through rate
    cpc = Column(Float, default=0.0)  # Cost per click
    cpa = Column(Float, default=0.0)  # Cost per acquisition
    roas = Column(Float, default=0.0)  # Return on ad spend
    
    # Campaign settings
    channels = Column(JSON, nullable=True)  # Array of channel names
    targeting_criteria = Column(JSON, nullable=True)
    creative_assets = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="campaigns")
    analytics = relationship("Analytics", back_populates="campaign")
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    @property
    def is_active(self):
        if not self.start_date or not self.end_date:
            return False
        now = datetime.utcnow()
        return self.start_date <= now <= self.end_date and self.status == "active"
    
    @property
    def performance_score(self):
        """Calculate overall performance score based on metrics"""
        if self.impressions == 0:
            return 0
        
        # Weighted score based on CTR, conversions, and ROAS
        ctr_score = min(self.ctr * 100, 100)  # Normalize CTR
        conversion_score = min((self.conversions / self.impressions) * 1000, 100)
        roas_score = min(self.roas * 20, 100)  # Normalize ROAS
        
        return (ctr_score * 0.3 + conversion_score * 0.4 + roas_score * 0.3)
