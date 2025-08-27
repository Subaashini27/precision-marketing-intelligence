from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class PowerBIReport(Base):
    __tablename__ = "powerbi_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Power BI details
    report_name = Column(String(255), nullable=False)
    report_id = Column(String(255), nullable=False, unique=True)  # Power BI report ID
    workspace_id = Column(String(255), nullable=False)
    dataset_id = Column(String(255), nullable=True)
    
    # Report configuration
    report_type = Column(String(100), nullable=False)  # dashboard, report, paginated
    category = Column(String(100), nullable=True)  # marketing, sales, finance, etc.
    description = Column(Text, nullable=True)
    
    # Embedding settings
    embed_url = Column(Text, nullable=True)
    embed_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime(timezone=True), nullable=True)
    
    # Access control
    is_public = Column(Boolean, default=False)
    allowed_users = Column(JSON, nullable=True)  # Array of user IDs
    allowed_roles = Column(JSON, nullable=True)  # Array of role names
    
    # Report settings
    refresh_schedule = Column(String(100), nullable=True)  # daily, weekly, monthly
    last_refresh = Column(DateTime(timezone=True), nullable=True)
    auto_refresh = Column(Boolean, default=True)
    
    # Customization
    theme = Column(String(50), default="default")
    layout_settings = Column(JSON, nullable=True)  # Custom layout preferences
    filter_defaults = Column(JSON, nullable=True)  # Default filter values
    
    # Usage tracking
    view_count = Column(Integer, default=0)
    last_viewed = Column(DateTime(timezone=True), nullable=True)
    favorite_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="powerbi_reports")
    
    def __repr__(self):
        return f"<PowerBIReport(id={self.id}, name='{self.report_name}', type='{self.report_type}')>"
    
    @property
    def is_accessible(self, current_user=None):
        """Check if report is accessible to current user"""
        if self.is_public:
            return True
        
        if not current_user:
            return False
        
        # Check if user is owner
        if current_user.id == self.user_id:
            return True
        
        # Check if user has explicit access
        if self.allowed_users and current_user.id in self.allowed_users:
            return True
        
        # Check if user has role-based access
        if self.allowed_roles and current_user.role in self.allowed_roles:
            return True
        
        return False
    
    @property
    def needs_refresh(self):
        """Check if report needs refresh based on schedule"""
        if not self.last_refresh or not self.refresh_schedule:
            return False
        
        now = datetime.utcnow()
        time_diff = now - self.last_refresh
        
        if self.refresh_schedule == "daily" and time_diff.days >= 1:
            return True
        elif self.refresh_schedule == "weekly" and time_diff.days >= 7:
            return True
        elif self.refresh_schedule == "monthly" and time_diff.days >= 30:
            return True
        
        return False
    
    @property
    def popularity_score(self):
        """Calculate popularity score based on views and favorites"""
        return (self.view_count * 0.7 + self.favorite_count * 0.3) / 100
