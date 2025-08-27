import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PowerBIService:
    """
    Power BI Service for integrating with Power BI REST API
    Handles authentication, report embedding, and data refresh
    """
    
    def __init__(self):
        self.client_id = settings.powerbi_client_id
        self.client_secret = settings.powerbi_client_secret
        self.tenant_id = settings.powerbi_tenant_id
        self.workspace_id = settings.powerbi_workspace_id
        self.report_id = settings.powerbi_report_id
        
        self.access_token = None
        self.token_expiry = None
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        
        # Initialize authentication
        if self.client_id and self.client_secret and self.tenant_id:
            self.authenticate()
    
    def authenticate(self) -> bool:
        """Authenticate with Power BI using service principal"""
        try:
            if not all([self.client_id, self.client_secret, self.tenant_id]):
                logger.warning("Power BI credentials not configured")
                return False
            
            # Get access token
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            token_data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "https://analysis.windows.net/powerbi/api/.default"
            }
            
            response = requests.post(token_url, data=token_data)
            response.raise_for_status()
            
            token_info = response.json()
            self.access_token = token_info["access_token"]
            self.token_expiry = datetime.utcnow() + timedelta(seconds=token_info["expires_in"])
            
            logger.info("Power BI authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Power BI authentication failed: {e}")
            return False
    
    def is_token_valid(self) -> bool:
        """Check if access token is still valid"""
        if not self.access_token or not self.token_expiry:
            return False
        return datetime.utcnow() < self.token_expiry
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        if not self.is_token_valid():
            self.authenticate()
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_workspaces(self) -> List[Dict]:
        """Get list of available workspaces"""
        try:
            if not self.is_token_valid():
                return []
            
            url = f"{self.base_url}/groups"
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            workspaces = response.json().get("value", [])
            logger.info(f"Retrieved {len(workspaces)} workspaces")
            return workspaces
            
        except Exception as e:
            logger.error(f"Error getting workspaces: {e}")
            return []
    
    def get_reports(self, workspace_id: Optional[str] = None) -> List[Dict]:
        """Get list of reports in a workspace"""
        try:
            if not self.is_token_valid():
                return []
            
            workspace = workspace_id or self.workspace_id
            if not workspace:
                logger.error("No workspace ID provided")
                return []
            
            url = f"{self.base_url}/groups/{workspace}/reports"
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            reports = response.json().get("value", [])
            logger.info(f"Retrieved {len(reports)} reports from workspace {workspace}")
            return reports
            
        except Exception as e:
            logger.error(f"Error getting reports: {e}")
            return []
    
    def get_datasets(self, workspace_id: Optional[str] = None) -> List[Dict]:
        """Get list of datasets in a workspace"""
        try:
            if not self.is_token_valid():
                return []
            
            workspace = workspace_id or self.workspace_id
            if not workspace:
                logger.error("No workspace ID provided")
                return []
            
            url = f"{self.base_url}/groups/{workspace}/datasets"
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            datasets = response.json().get("value", [])
            logger.info(f"Retrieved {len(datasets)} datasets from workspace {workspace}")
            return datasets
            
        except Exception as e:
            logger.error(f"Error getting datasets: {e}")
            return []
    
    def get_embed_token(self, report_id: Optional[str] = None, 
                       workspace_id: Optional[str] = None,
                       user_email: Optional[str] = None) -> Dict:
        """Get embed token for a report"""
        try:
            if not self.is_token_valid():
                return {"error": "Authentication required"}
            
            report = report_id or self.report_id
            workspace = workspace_id or self.workspace_id
            
            if not report or not workspace:
                return {"error": "Report ID and workspace ID required"}
            
            # Generate embed token
            token_url = f"{self.base_url}/groups/{workspace}/reports/{report}/GenerateToken"
            
            token_request = {
                "accessLevel": "View",
                "allowSaveAs": False,
                "identities": []
            }
            
            # Add user identity if provided
            if user_email:
                token_request["identities"].append({
                    "username": user_email,
                    "roles": ["Viewer"],
                    "datasets": [workspace]
                })
            
            response = requests.post(token_url, headers=self.get_headers(), json=token_request)
            response.raise_for_status()
            
            token_info = response.json()
            logger.info(f"Generated embed token for report {report}")
            
            return {
                "embed_token": token_info["token"],
                "expiration": token_info["expiration"],
                "report_id": report,
                "workspace_id": workspace
            }
            
        except Exception as e:
            logger.error(f"Error generating embed token: {e}")
            return {"error": str(e)}
    
    def get_embed_url(self, report_id: Optional[str] = None,
                     workspace_id: Optional[str] = None) -> str:
        """Get embed URL for a report"""
        report = report_id or self.report_id
        workspace = workspace_id or self.workspace_id
        
        if not report or not workspace:
            return ""
        
        return f"https://app.powerbi.com/reportEmbed?reportId={report}&groupId={workspace}"
    
    def refresh_dataset(self, dataset_id: str, 
                       workspace_id: Optional[str] = None) -> bool:
        """Refresh a dataset"""
        try:
            if not self.is_token_valid():
                return False
            
            workspace = workspace_id or self.workspace_id
            if not workspace:
                logger.error("No workspace ID provided")
                return False
            
            url = f"{self.base_url}/groups/{workspace}/datasets/{dataset_id}/refreshes"
            response = requests.post(url, headers=self.get_headers())
            response.raise_for_status()
            
            logger.info(f"Dataset {dataset_id} refresh initiated")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing dataset: {e}")
            return False
    
    def get_dataset_refresh_history(self, dataset_id: str,
                                  workspace_id: Optional[str] = None) -> List[Dict]:
        """Get refresh history for a dataset"""
        try:
            if not self.is_token_valid():
                return []
            
            workspace = workspace_id or self.workspace_id
            if not workspace:
                logger.error("No workspace ID provided")
                return []
            
            url = f"{self.base_url}/groups/{workspace}/datasets/{dataset_id}/refreshes"
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            refreshes = response.json().get("value", [])
            logger.info(f"Retrieved {len(refreshes)} refresh records for dataset {dataset_id}")
            return refreshes
            
        except Exception as e:
            logger.error(f"Error getting refresh history: {e}")
            return []
    
    def get_report_parameters(self, report_id: Optional[str] = None,
                             workspace_id: Optional[str] = None) -> List[Dict]:
        """Get parameters for a report"""
        try:
            if not self.is_token_valid():
                return []
            
            report = report_id or self.report_id
            workspace = workspace_id or self.workspace_id
            
            if not report or not workspace:
                logger.error("Report ID and workspace ID required")
                return []
            
            url = f"{self.base_url}/groups/{workspace}/reports/{report}/parameters"
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            parameters = response.json().get("value", [])
            logger.info(f"Retrieved {len(parameters)} parameters for report {report}")
            return parameters
            
        except Exception as e:
            logger.error(f"Error getting report parameters: {e}")
            return []
    
    def get_report_pages(self, report_id: Optional[str] = None,
                         workspace_id: Optional[str] = None) -> List[Dict]:
        """Get pages for a report"""
        try:
            if not self.is_token_valid():
                return []
            
            report = report_id or self.report_id
            workspace = workspace_id or self.workspace_id
            
            if not report or not workspace:
                logger.error("Report ID and workspace ID required")
                return []
            
            url = f"{self.base_url}/groups/{workspace}/reports/{report}/pages"
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            pages = response.json().get("value", [])
            logger.info(f"Retrieved {len(pages)} pages for report {report}")
            return pages
            
        except Exception as e:
            logger.error(f"Error getting report pages: {e}")
            return []
    
    def create_embed_config(self, report_id: Optional[str] = None,
                           workspace_id: Optional[str] = None,
                           user_email: Optional[str] = None) -> Dict:
        """Create complete embed configuration for a report"""
        try:
            # Get embed token
            token_info = self.get_embed_token(report_id, workspace_id, user_email)
            if "error" in token_info:
                return token_info
            
            # Get embed URL
            embed_url = self.get_embed_url(report_id, workspace_id)
            
            # Get report details
            reports = self.get_reports(workspace_id)
            report_details = next((r for r in reports if r["id"] == (report_id or self.report_id)), {})
            
            config = {
                "embed_url": embed_url,
                "embed_token": token_info["embed_token"],
                "report_id": token_info["report_id"],
                "workspace_id": token_info["workspace_id"],
                "report_name": report_details.get("name", "Unknown Report"),
                "report_type": report_details.get("reportType", "Report"),
                "expiration": token_info["expiration"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Created embed config for report {config['report_id']}")
            return config
            
        except Exception as e:
            logger.error(f"Error creating embed config: {e}")
            return {"error": str(e)}
    
    def get_service_status(self) -> Dict:
        """Get overall service status"""
        return {
            "authenticated": self.is_token_valid(),
            "client_id_configured": bool(self.client_id),
            "workspace_id_configured": bool(self.workspace_id),
            "report_id_configured": bool(self.report_id),
            "token_expiry": self.token_expiry.isoformat() if self.token_expiry else None,
            "status": "ready" if self.is_token_valid() else "not_authenticated"
        }

# Create global instance
powerbi_service = PowerBIService()
