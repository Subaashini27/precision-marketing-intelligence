"""
Email Notification Service for Precision Marketing Intelligence Platform
Supports multiple email providers with fallback options
"""

import smtplib
import logging
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime
import asyncio
import aiosmtplib
from jinja2 import Template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailConfig(BaseModel):
    """Email configuration settings"""
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True
    use_ssl: bool = False

class EmailMessage(BaseModel):
    """Email message structure"""
    to_emails: List[EmailStr]
    subject: str
    html_content: str
    text_content: Optional[str] = None
    cc_emails: Optional[List[EmailStr]] = None
    bcc_emails: Optional[List[EmailStr]] = None
    attachments: Optional[List[Dict[str, Any]]] = None

class EmailService:
    """
    Professional Email Service with multiple provider support
    """
    
    def __init__(self):
        self.providers = {
            'gmail': EmailConfig(
                smtp_server='smtp.gmail.com',
                smtp_port=587,
                username='your-email@gmail.com',  # Configure with your credentials
                password='your-app-password',     # Use App Password for Gmail
                use_tls=True
            ),
            'outlook': EmailConfig(
                smtp_server='smtp-mail.outlook.com',
                smtp_port=587,
                username='your-email@outlook.com',
                password='your-password',
                use_tls=True
            ),
            'yahoo': EmailConfig(
                smtp_server='smtp.mail.yahoo.com',
                smtp_port=587,
                username='your-email@yahoo.com',
                password='your-app-password',
                use_tls=True
            ),
            'custom': EmailConfig(
                smtp_server='smtp.your-domain.com',
                smtp_port=587,
                username='your-email@your-domain.com',
                password='your-password',
                use_tls=True
            )
        }
        self.default_provider = 'gmail'
        self.email_templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Load email templates for different notification types"""
        return {
            'alert': """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Marketing Alert - Precision Marketing Intelligence</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                    .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
                    .content { padding: 30px; }
                    .alert-{{ severity|lower }} { border-left: 4px solid; padding: 15px; margin: 20px 0; border-radius: 4px; }
                    .alert-high { border-color: #dc3545; background-color: #f8d7da; }
                    .alert-medium { border-color: #ffc107; background-color: #fff3cd; }
                    .alert-low { border-color: #28a745; background-color: #d4edda; }
                    .button { display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 6px; margin: 10px 0; }
                    .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; }
                    .metric { background: #f8f9fa; padding: 15px; border-radius: 6px; margin: 10px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚨 Marketing Alert</h1>
                        <p>Precision Marketing Intelligence Platform</p>
                    </div>
                    <div class="content">
                        <div class="alert-{{ severity|lower }}">
                            <h2>{{ title }}</h2>
                            <p>{{ message }}</p>
                        </div>
                        
                        {% if metrics %}
                        <h3>📊 Current Metrics</h3>
                        {% for metric in metrics %}
                        <div class="metric">
                            <strong>{{ metric.name }}:</strong> {{ metric.value }}
                            {% if metric.change %}<span style="color: {{ 'green' if metric.change > 0 else 'red' }};">({{ metric.change }})</span>{% endif %}
                        </div>
                        {% endfor %}
                        {% endif %}
                        
                        {% if recommendations %}
                        <h3>💡 AI Recommendations</h3>
                        <ul>
                        {% for rec in recommendations %}
                            <li>{{ rec }}</li>
                        {% endfor %}
                        </ul>
                        {% endif %}
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ dashboard_url }}" class="button">View Dashboard</a>
                            <a href="{{ campaign_url }}" class="button">Manage Campaigns</a>
                        </div>
                        
                        <p><strong>Time:</strong> {{ timestamp }}</p>
                        <p><strong>Severity:</strong> <span style="color: {{ 'red' if severity == 'high' else 'orange' if severity == 'medium' else 'green' }};">{{ severity|upper }}</span></p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Precision Marketing Intelligence Platform</p>
                        <p>Malaysian Business Analytics Solution</p>
                        <p><small>You are receiving this because you have alerts enabled. <a href="{{ unsubscribe_url }}">Unsubscribe</a></small></p>
                    </div>
                </div>
            </body>
            </html>
            """,
            
            'campaign_update': """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Campaign Update - Precision Marketing Intelligence</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                    .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                    .header { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; }
                    .content { padding: 30px; }
                    .stats { display: flex; justify-content: space-between; margin: 20px 0; }
                    .stat { text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; flex: 1; margin: 0 5px; }
                    .button { display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 6px; margin: 10px 0; }
                    .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📈 Campaign Update</h1>
                        <p>{{ campaign_name }}</p>
                    </div>
                    <div class="content">
                        <h2>Performance Summary</h2>
                        <div class="stats">
                            <div class="stat">
                                <h3>rm{{ budget }}</h3>
                                <p>Budget</p>
                            </div>
                            <div class="stat">
                                <h3>rm{{ spent }}</h3>
                                <p>Spent</p>
                            </div>
                            <div class="stat">
                                <h3>{{ impressions }}</h3>
                                <p>Impressions</p>
                            </div>
                            <div class="stat">
                                <h3>{{ clicks }}</h3>
                                <p>Clicks</p>
                            </div>
                        </div>
                        
                        <h3>📊 Key Metrics</h3>
                        <ul>
                            <li><strong>Click-through Rate:</strong> {{ ctr }}%</li>
                            <li><strong>Cost per Click:</strong> rm{{ cpc }}</li>
                            <li><strong>Conversion Rate:</strong> {{ conversion_rate }}%</li>
                            <li><strong>Return on Ad Spend:</strong> {{ roas }}x</li>
                        </ul>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ campaign_url }}" class="button">View Campaign Details</a>
                        </div>
                    </div>
                    <div class="footer">
                        <p>© 2024 Precision Marketing Intelligence Platform</p>
                        <p>Malaysian Business Analytics Solution</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            
            'weekly_report': """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Weekly Marketing Report - Precision Marketing Intelligence</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                    .container { max-width: 700px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                    .header { background: linear-gradient(135deg, #6f42c1 0%, #007bff 100%); color: white; padding: 30px; text-align: center; }
                    .content { padding: 30px; }
                    .summary-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }
                    .summary-card { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 20px; border-radius: 10px; text-align: center; }
                    .trend-up { color: #28a745; }
                    .trend-down { color: #dc3545; }
                    .button { display: inline-block; padding: 12px 24px; background: #6f42c1; color: white; text-decoration: none; border-radius: 6px; margin: 10px 0; }
                    .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 Weekly Marketing Report</h1>
                        <p>{{ week_start }} - {{ week_end }}</p>
                    </div>
                    <div class="content">
                        <h2>Performance Overview</h2>
                        <div class="summary-grid">
                            <div class="summary-card">
                                <h3>rm{{ total_revenue }}</h3>
                                <p>Total Revenue</p>
                                <span class="trend-{{ revenue_trend }}">{{ revenue_change }}</span>
                            </div>
                            <div class="summary-card">
                                <h3>{{ total_conversions }}</h3>
                                <p>Conversions</p>
                                <span class="trend-{{ conversion_trend }}">{{ conversion_change }}</span>
                            </div>
                            <div class="summary-card">
                                <h3>{{ website_visitors }}</h3>
                                <p>Website Visitors</p>
                                <span class="trend-{{ visitor_trend }}">{{ visitor_change }}</span>
                            </div>
                            <div class="summary-card">
                                <h3>{{ active_campaigns }}</h3>
                                <p>Active Campaigns</p>
                                <span class="trend-{{ campaign_trend }}">{{ campaign_change }}</span>
                            </div>
                        </div>
                        
                        <h3>🏆 Top Performing Campaigns</h3>
                        {% for campaign in top_campaigns %}
                        <div style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 6px;">
                            <strong>{{ campaign.name }}</strong> - rm{{ campaign.revenue }} revenue ({{ campaign.performance }}% efficiency)
                        </div>
                        {% endfor %}
                        
                        <h3>💡 AI Insights & Recommendations</h3>
                        <ul>
                        {% for insight in ai_insights %}
                            <li>{{ insight }}</li>
                        {% endfor %}
                        </ul>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ dashboard_url }}" class="button">View Full Dashboard</a>
                            <a href="{{ analytics_url }}" class="button">Detailed Analytics</a>
                        </div>
                    </div>
                    <div class="footer">
                        <p>© 2024 Precision Marketing Intelligence Platform</p>
                        <p>Your Malaysian Marketing Intelligence Partner</p>
                    </div>
                </div>
            </body>
            </html>
            """
        }

    async def send_email_async(self, message: EmailMessage, provider: str = None) -> bool:
        """
        Send email asynchronously with fallback support
        """
        provider = provider or self.default_provider
        config = self.providers.get(provider)
        
        if not config:
            logger.error(f"Email provider '{provider}' not configured")
            return False

        try:
            # Create message
            msg = MimeMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = config.username
            msg['To'] = ', '.join(message.to_emails)
            
            if message.cc_emails:
                msg['Cc'] = ', '.join(message.cc_emails)

            # Add text and HTML parts
            if message.text_content:
                text_part = MimeText(message.text_content, 'plain')
                msg.attach(text_part)
            
            html_part = MimeText(message.html_content, 'html')
            msg.attach(html_part)

            # Add attachments if any
            if message.attachments:
                for attachment in message.attachments:
                    part = MimeBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    msg.attach(part)

            # Send email
            async with aiosmtplib.SMTP(
                hostname=config.smtp_server,
                port=config.smtp_port,
                use_tls=config.use_tls
            ) as smtp:
                await smtp.login(config.username, config.password)
                
                # Prepare recipient list
                recipients = list(message.to_emails)
                if message.cc_emails:
                    recipients.extend(message.cc_emails)
                if message.bcc_emails:
                    recipients.extend(message.bcc_emails)
                
                await smtp.send_message(msg, recipients=recipients)
                
            logger.info(f"Email sent successfully to {len(recipients)} recipients via {provider}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email via {provider}: {str(e)}")
            
            # Try fallback providers
            fallback_providers = [p for p in self.providers.keys() if p != provider]
            for fallback in fallback_providers:
                logger.info(f"Trying fallback provider: {fallback}")
                try:
                    return await self.send_email_async(message, fallback)
                except Exception as fe:
                    logger.error(f"Fallback provider {fallback} also failed: {str(fe)}")
                    continue
            
            return False

    def render_template(self, template_name: str, **kwargs) -> str:
        """
        Render email template with provided data
        """
        template_content = self.email_templates.get(template_name)
        if not template_content:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = Template(template_content)
        return template.render(**kwargs)

    async def send_alert_email(self, 
                              recipients: List[str], 
                              alert_type: str,
                              title: str,
                              message: str,
                              severity: str = "medium",
                              metrics: List[Dict] = None,
                              recommendations: List[str] = None) -> bool:
        """
        Send marketing alert email
        """
        html_content = self.render_template(
            'alert',
            title=title,
            message=message,
            severity=severity,
            metrics=metrics or [],
            recommendations=recommendations or [],
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S MYT"),
            dashboard_url="http://localhost:3000/dashboard",
            campaign_url="http://localhost:3000/campaigns",
            unsubscribe_url="http://localhost:3000/profile"
        )

        email_message = EmailMessage(
            to_emails=recipients,
            subject=f"🚨 Marketing Alert: {title}",
            html_content=html_content
        )

        return await self.send_email_async(email_message)

    async def send_campaign_update_email(self,
                                       recipients: List[str],
                                       campaign_data: Dict) -> bool:
        """
        Send campaign performance update email
        """
        html_content = self.render_template(
            'campaign_update',
            **campaign_data,
            campaign_url=f"http://localhost:3000/campaigns/{campaign_data.get('id', '')}"
        )

        email_message = EmailMessage(
            to_emails=recipients,
            subject=f"📈 Campaign Update: {campaign_data.get('campaign_name', 'Unknown Campaign')}",
            html_content=html_content
        )

        return await self.send_email_async(email_message)

    async def send_weekly_report_email(self,
                                     recipients: List[str],
                                     report_data: Dict) -> bool:
        """
        Send weekly marketing performance report
        """
        html_content = self.render_template(
            'weekly_report',
            **report_data,
            dashboard_url="http://localhost:3000/dashboard",
            analytics_url="http://localhost:3000/analytics"
        )

        email_message = EmailMessage(
            to_emails=recipients,
            subject=f"📊 Weekly Marketing Report - {report_data.get('week_start', '')} to {report_data.get('week_end', '')}",
            html_content=html_content
        )

        return await self.send_email_async(email_message)

    def configure_provider(self, provider_name: str, config: EmailConfig):
        """
        Configure or update email provider settings
        """
        self.providers[provider_name] = config
        logger.info(f"Email provider '{provider_name}' configured successfully")

    def set_default_provider(self, provider_name: str):
        """
        Set the default email provider
        """
        if provider_name in self.providers:
            self.default_provider = provider_name
            logger.info(f"Default email provider set to '{provider_name}'")
        else:
            raise ValueError(f"Provider '{provider_name}' not configured")

# Global email service instance
email_service = EmailService()

# Quick setup functions for popular providers
def setup_gmail(email: str, app_password: str):
    """Quick setup for Gmail"""
    config = EmailConfig(
        smtp_server='smtp.gmail.com',
        smtp_port=587,
        username=email,
        password=app_password,
        use_tls=True
    )
    email_service.configure_provider('gmail', config)
    email_service.set_default_provider('gmail')

def setup_outlook(email: str, password: str):
    """Quick setup for Outlook"""
    config = EmailConfig(
        smtp_server='smtp-mail.outlook.com',
        smtp_port=587,
        username=email,
        password=password,
        use_tls=True
    )
    email_service.configure_provider('outlook', config)
    email_service.set_default_provider('outlook')

def setup_custom_smtp(email: str, password: str, smtp_server: str, smtp_port: int = 587):
    """Quick setup for custom SMTP"""
    config = EmailConfig(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        username=email,
        password=password,
        use_tls=True
    )
    email_service.configure_provider('custom', config)
    email_service.set_default_provider('custom')
