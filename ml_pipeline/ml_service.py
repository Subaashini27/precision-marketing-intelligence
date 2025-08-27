import joblib
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketingMLService:
    """
    Marketing ML Service for integrating existing ML models
    Handles predictions for conversion, churn, ROI, and campaign performance
    """
    
    def __init__(self, models_dir: str = "models/"):
        self.models_dir = models_dir
        self.models = {}
        self.feature_encoders = {}
        self.scalers = {}
        self.load_models()
    
    def load_models(self):
        """Load all available ML models"""
        try:
            # Load conversion prediction model
            if os.path.exists(os.path.join(self.models_dir, "conversion_model.pkl")):
                self.models["conversion"] = joblib.load(os.path.join(self.models_dir, "conversion_model.pkl"))
                logger.info("Conversion model loaded successfully")
            
            # Load churn prediction model
            if os.path.exists(os.path.join(self.models_dir, "churn_model.pkl")):
                self.models["churn"] = joblib.load(os.path.join(self.models_dir, "churn_model.pkl"))
                logger.info("Churn model loaded successfully")
            
            # Load ROI prediction model
            if os.path.exists(os.path.join(self.models_dir, "roi_model.pkl")):
                self.models["roi"] = joblib.load(os.path.join(self.models_dir, "roi_model.pkl"))
                logger.info("ROI model loaded successfully")
            
            # Load campaign performance model
            if os.path.exists(os.path.join(self.models_dir, "campaign_performance_model.pkl")):
                self.models["campaign_performance"] = joblib.load(os.path.join(self.models_dir, "campaign_performance_model.pkl"))
                logger.info("Campaign performance model loaded successfully")
            
            # Load feature encoders
            if os.path.exists(os.path.join(self.models_dir, "feature_encoder.pkl")):
                self.feature_encoders["main"] = joblib.load(os.path.join(self.models_dir, "feature_encoder.pkl"))
                logger.info("Feature encoder loaded successfully")
            
            # Load scalers
            if os.path.exists(os.path.join(self.models_dir, "scaler.pkl")):
                self.scalers["main"] = joblib.load(os.path.join(self.models_dir, "scaler.pkl"))
                logger.info("Scaler loaded successfully")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def predict_conversion(self, features: Dict) -> Dict:
        """
        Predict conversion likelihood for a customer
        
        Args:
            features: Dictionary containing customer features
            
        Returns:
            Dictionary with prediction results
        """
        try:
            if "conversion" not in self.models:
                return {"error": "Conversion model not available"}
            
            # Prepare features
            feature_df = self._prepare_features(features)
            
            # Make prediction
            prediction = self.models["conversion"].predict_proba(feature_df)[0]
            conversion_prob = prediction[1]  # Probability of conversion
            
            # Determine risk level
            risk_level = self._determine_risk_level(conversion_prob, "conversion")
            
            # Generate insights
            insights = self._generate_conversion_insights(features, conversion_prob)
            
            return {
                "prediction_type": "conversion",
                "prediction_value": float(conversion_prob),
                "prediction_probability": float(conversion_prob),
                "risk_level": risk_level,
                "confidence_score": 0.85,  # This would come from model metadata
                "insights": insights,
                "recommendations": self._get_conversion_recommendations(conversion_prob),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in conversion prediction: {e}")
            return {"error": str(e)}
    
    def predict_churn(self, features: Dict) -> Dict:
        """
        Predict churn risk for a customer
        
        Args:
            features: Dictionary containing customer features
            
        Returns:
            Dictionary with prediction results
        """
        try:
            if "churn" not in self.models:
                return {"error": "Churn model not available"}
            
            # Prepare features
            feature_df = self._prepare_features(features)
            
            # Make prediction
            prediction = self.models["churn"].predict_proba(feature_df)[0]
            churn_prob = prediction[1]  # Probability of churn
            
            # Determine risk level
            risk_level = self._determine_risk_level(churn_prob, "churn")
            
            # Generate insights
            insights = self._generate_churn_insights(features, churn_prob)
            
            return {
                "prediction_type": "churn",
                "prediction_value": float(churn_prob),
                "prediction_probability": float(churn_prob),
                "risk_level": risk_level,
                "confidence_score": 0.82,  # This would come from model metadata
                "insights": insights,
                "recommendations": self._get_churn_recommendations(churn_prob),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in churn prediction: {e}")
            return {"error": str(e)}
    
    def predict_roi(self, features: Dict) -> Dict:
        """
        Predict ROI for a marketing campaign
        
        Args:
            features: Dictionary containing campaign features
            
        Returns:
            Dictionary with prediction results
        """
        try:
            if "roi" not in self.models:
                return {"error": "ROI model not available"}
            
            # Prepare features
            feature_df = self._prepare_features(features)
            
            # Make prediction
            roi_prediction = self.models["roi"].predict(feature_df)[0]
            
            # Determine performance level
            performance_level = self._determine_performance_level(roi_prediction, "roi")
            
            return {
                "prediction_type": "roi",
                "prediction_value": float(roi_prediction),
                "roi_prediction": float(roi_prediction),
                "performance_level": performance_level,
                "confidence_score": 0.78,  # This would come from model metadata
                "recommendations": self._get_roi_recommendations(roi_prediction),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in ROI prediction: {e}")
            return {"error": str(e)}
    
    def predict_campaign_performance(self, features: Dict) -> Dict:
        """
        Predict overall campaign performance
        
        Args:
            features: Dictionary containing campaign features
            
        Returns:
            Dictionary with prediction results
        """
        try:
            if "campaign_performance" not in self.models:
                return {"error": "Campaign performance model not available"}
            
            # Prepare features
            feature_df = self._prepare_features(features)
            
            # Make prediction
            performance_score = self.models["campaign_performance"].predict(feature_df)[0]
            
            # Determine performance level
            performance_level = self._determine_performance_level(performance_score, "campaign")
            
            return {
                "prediction_type": "campaign_performance",
                "prediction_value": float(performance_score),
                "performance_score": float(performance_score),
                "performance_level": performance_level,
                "confidence_score": 0.80,  # This would come from model metadata
                "recommendations": self._get_campaign_recommendations(performance_score),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in campaign performance prediction: {e}")
            return {"error": str(e)}
    
    def _prepare_features(self, features: Dict) -> pd.DataFrame:
        """Prepare features for model input"""
        # Convert to DataFrame
        feature_df = pd.DataFrame([features])
        
        # Handle categorical variables
        if "main" in self.feature_encoders:
            categorical_cols = self.feature_encoders["main"].get_feature_names_out()
            feature_df = self.feature_encoders["main"].transform(feature_df)
            feature_df = pd.DataFrame(feature_df, columns=categorical_cols)
        
        # Handle scaling
        if "main" in self.scalers:
            feature_df = self.scalers["main"].transform(feature_df)
        
        return feature_df
    
    def _determine_risk_level(self, probability: float, prediction_type: str) -> str:
        """Determine risk level based on probability"""
        if prediction_type == "conversion":
            if probability >= 0.7:
                return "low"
            elif probability >= 0.4:
                return "medium"
            else:
                return "high"
        elif prediction_type == "churn":
            if probability <= 0.3:
                return "low"
            elif probability <= 0.6:
                return "medium"
            else:
                return "high"
        return "medium"
    
    def _determine_performance_level(self, score: float, prediction_type: str) -> str:
        """Determine performance level based on score"""
        if prediction_type == "roi":
            if score >= 3.0:
                return "excellent"
            elif score >= 2.0:
                return "good"
            elif score >= 1.5:
                return "average"
            else:
                return "poor"
        elif prediction_type == "campaign":
            if score >= 80:
                return "excellent"
            elif score >= 60:
                return "good"
            elif score >= 40:
                return "average"
            else:
                return "poor"
        return "average"
    
    def _generate_conversion_insights(self, features: Dict, probability: float) -> List[str]:
        """Generate insights for conversion prediction"""
        insights = []
        
        if probability > 0.7:
            insights.append("High conversion probability - customer shows strong intent")
            if features.get("time_on_site", 0) > 300:
                insights.append("Extended site engagement indicates high interest")
        elif probability < 0.3:
            insights.append("Low conversion probability - consider retargeting strategies")
            if features.get("bounce_rate", 0) > 0.7:
                insights.append("High bounce rate suggests poor landing page experience")
        
        return insights
    
    def _generate_churn_insights(self, features: Dict, probability: float) -> List[str]:
        """Generate insights for churn prediction"""
        insights = []
        
        if probability > 0.6:
            insights.append("High churn risk - immediate retention action needed")
            if features.get("days_since_last_purchase", 0) > 30:
                insights.append("Long period since last purchase indicates disengagement")
        elif probability < 0.3:
            insights.append("Low churn risk - customer shows strong loyalty")
        
        return insights
    
    def _get_conversion_recommendations(self, probability: float) -> List[str]:
        """Get recommendations based on conversion probability"""
        if probability > 0.7:
            return [
                "Increase bid/budget for this customer segment",
                "Show premium products/services",
                "Implement urgency messaging"
            ]
        elif probability < 0.3:
            return [
                "Review targeting criteria",
                "Improve landing page experience",
                "Consider retargeting campaigns"
            ]
        return ["Monitor performance and optimize gradually"]
    
    def _get_churn_recommendations(self, probability: float) -> List[str]:
        """Get recommendations based on churn probability"""
        if probability > 0.6:
            return [
                "Implement immediate retention campaign",
                "Offer personalized incentives",
                "Schedule customer success call"
            ]
        elif probability < 0.3:
            return [
                "Continue current engagement strategy",
                "Upsell opportunities available"
            ]
        return ["Monitor engagement and adjust strategy"]
    
    def _get_roi_recommendations(self, roi: float) -> List[str]:
        """Get recommendations based on ROI prediction"""
        if roi > 3.0:
            return [
                "Excellent ROI - consider scaling campaign",
                "Increase budget allocation",
                "Expand to similar audiences"
            ]
        elif roi < 1.5:
            return [
                "Poor ROI - review campaign strategy",
                "Optimize targeting and creative",
                "Consider pausing campaign"
            ]
        return ["Monitor performance and optimize gradually"]
    
    def _get_campaign_recommendations(self, score: float) -> List[str]:
        """Get recommendations based on campaign performance score"""
        if score > 80:
            return [
                "Excellent performance - scale successful elements",
                "Increase budget allocation",
                "Document best practices"
            ]
        elif score < 40:
            return [
                "Poor performance - immediate optimization needed",
                "Review targeting and creative",
                "Consider campaign pause"
            ]
        return ["Monitor performance and optimize gradually"]
    
    def get_model_status(self) -> Dict:
        """Get status of all loaded models"""
        return {
            "models_loaded": list(self.models.keys()),
            "total_models": len(self.models),
            "feature_encoders": list(self.feature_encoders.keys()),
            "scalers": list(self.scalers.keys()),
            "status": "ready" if self.models else "no_models_loaded"
        }

# Create global instance
ml_service = MarketingMLService()
