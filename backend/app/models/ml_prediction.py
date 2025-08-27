from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class MLPrediction(Base):
    __tablename__ = "ml_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    
    # Prediction details
    prediction_type = Column(String(100), nullable=False)  # conversion, churn, roi, etc.
    model_version = Column(String(50), nullable=False)
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Input features
    input_features = Column(JSON, nullable=True)  # JSON object with feature values
    feature_importance = Column(JSON, nullable=True)  # JSON object with feature importance scores
    
    # Prediction results
    prediction_value = Column(Float, nullable=False)  # Raw prediction score
    prediction_probability = Column(Float, nullable=True)  # Probability if applicable
    prediction_class = Column(String(100), nullable=True)  # Class label if classification
    confidence_score = Column(Float, nullable=True)  # Model confidence in prediction
    
    # Thresholds and decisions
    threshold = Column(Float, nullable=True)
    decision = Column(String(50), nullable=True)  # approve, reject, review, etc.
    risk_level = Column(String(20), nullable=True)  # low, medium, high
    
    # Business impact
    expected_value = Column(Float, nullable=True)  # Expected monetary value
    roi_prediction = Column(Float, nullable=True)  # Predicted ROI
    conversion_probability = Column(Float, nullable=True)  # Likelihood of conversion
    
    # Model metadata
    model_accuracy = Column(Float, nullable=True)
    training_data_size = Column(Integer, nullable=True)
    last_training_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ml_predictions")
    campaign = relationship("Campaign", back_populates="ml_predictions")
    
    def __repr__(self):
        return f"<MLPrediction(id={self.id}, type='{self.prediction_type}', value={self.prediction_value})>"
    
    @property
    def is_high_confidence(self):
        """Check if prediction has high confidence"""
        return self.confidence_score and self.confidence_score >= 0.8
    
    @property
    def is_high_risk(self):
        """Check if prediction indicates high risk"""
        return self.risk_level == "high" or (self.prediction_probability and self.prediction_probability < 0.3)
    
    @property
    def actionable_insight(self):
        """Generate actionable insight from prediction"""
        if self.prediction_type == "conversion":
            if self.prediction_probability and self.prediction_probability > 0.7:
                return "High conversion probability - consider increasing bid or budget"
            elif self.prediction_probability and self.prediction_probability < 0.3:
                return "Low conversion probability - review targeting or creative"
        
        elif self.prediction_type == "churn":
            if self.prediction_probability and self.prediction_probability > 0.6:
                return "High churn risk - implement retention strategies"
        
        return "Monitor performance and adjust strategy as needed"
