"""
Marketing Alert Service
Triggers email notifications based on marketing thresholds and events
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.app.services.email_service import email_service

logger = logging.getLogger(__name__)

class MarketingAlertService:
    """
    Service for triggering marketing alerts and email notifications
    """
    
    def __init__(self):
        self.alert_thresholds = {
            'campaign_budget_threshold': 80,  # Percentage
            'conversion_rate_drop': 30,       # Percentage drop
            'click_through_rate_drop': 25,    # Percentage drop
            'cost_per_click_increase': 50,    # Percentage increase
            'revenue_drop': 20,               # Percentage drop
        }
        
        self.default_recipients = [
            'admin@company.com',
            'manager@company.com'
        ]

    async def check_campaign_budget_alert(self, campaign_data: Dict[str, Any]) -> bool:
        """
        Check if campaign budget usage exceeds threshold
        """
        try:
            budget = campaign_data.get('budget', 0)
            spent = campaign_data.get('spent', 0)
            
            if budget > 0:
                usage_percentage = (spent / budget) * 100
                
                if usage_percentage >= self.alert_thresholds['campaign_budget_threshold']:
                    await self._send_budget_alert(campaign_data, usage_percentage)
                    return True
                    
        except Exception as e:
            logger.error(f"Error checking campaign budget alert: {str(e)}")
            
        return False

    async def check_performance_alert(self, performance_data: Dict[str, Any]) -> bool:
        """
        Check for performance drops that require attention
        """
        try:
            alerts_sent = []
            
            # Check conversion rate drop
            if self._check_percentage_drop(
                performance_data.get('conversion_rate_current'),
                performance_data.get('conversion_rate_previous'),
                self.alert_thresholds['conversion_rate_drop']
            ):
                await self._send_performance_alert(
                    "Conversion Rate Drop",
                    performance_data,
                    "conversion_rate"
                )
                alerts_sent.append("conversion_rate")
            
            # Check CTR drop
            if self._check_percentage_drop(
                performance_data.get('ctr_current'),
                performance_data.get('ctr_previous'),
                self.alert_thresholds['click_through_rate_drop']
            ):
                await self._send_performance_alert(
                    "Click-Through Rate Drop",
                    performance_data,
                    "ctr"
                )
                alerts_sent.append("ctr")
            
            # Check revenue drop
            if self._check_percentage_drop(
                performance_data.get('revenue_current'),
                performance_data.get('revenue_previous'),
                self.alert_thresholds['revenue_drop']
            ):
                await self._send_performance_alert(
                    "Revenue Drop Alert",
                    performance_data,
                    "revenue"
                )
                alerts_sent.append("revenue")
            
            return len(alerts_sent) > 0
            
        except Exception as e:
            logger.error(f"Error checking performance alerts: {str(e)}")
            return False

    async def send_weekly_report(self, report_data: Dict[str, Any], recipients: Optional[List[str]] = None):
        """
        Send weekly marketing performance report
        """
        try:
            recipients = recipients or self.default_recipients
            
            # Enhance report data with additional insights
            enhanced_data = {
                **report_data,
                'week_start': report_data.get('week_start', datetime.now().strftime('%Y-%m-%d')),
                'week_end': report_data.get('week_end', datetime.now().strftime('%Y-%m-%d')),
                'ai_insights': report_data.get('ai_insights', self._generate_ai_insights(report_data))
            }
            
            success = await email_service.send_weekly_report_email(
                recipients=recipients,
                report_data=enhanced_data
            )
            
            if success:
                logger.info(f"Weekly report sent to {len(recipients)} recipients")
            else:
                logger.error("Failed to send weekly report")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending weekly report: {str(e)}")
            return False

    async def send_campaign_update(self, campaign_data: Dict[str, Any], recipients: Optional[List[str]] = None):
        """
        Send campaign performance update
        """
        try:
            recipients = recipients or self.default_recipients
            
            success = await email_service.send_campaign_update_email(
                recipients=recipients,
                campaign_data=campaign_data
            )
            
            if success:
                logger.info(f"Campaign update sent for '{campaign_data.get('campaign_name', 'Unknown')}'")
            else:
                logger.error("Failed to send campaign update")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending campaign update: {str(e)}")
            return False

    async def _send_budget_alert(self, campaign_data: Dict[str, Any], usage_percentage: float):
        """
        Send budget threshold alert
        """
        try:
            campaign_name = campaign_data.get('name', 'Unknown Campaign')
            budget = campaign_data.get('budget', 0)
            spent = campaign_data.get('spent', 0)
            
            metrics = [
                {
                    "name": "Budget Utilization",
                    "value": f"{usage_percentage:.1f}%",
                    "change": f"+{usage_percentage - self.alert_thresholds['campaign_budget_threshold']:.1f}%"
                },
                {
                    "name": "Total Budget",
                    "value": f"rm{budget:,.0f}",
                    "change": None
                },
                {
                    "name": "Amount Spent",
                    "value": f"rm{spent:,.0f}",
                    "change": None
                },
                {
                    "name": "Remaining Budget",
                    "value": f"rm{budget - spent:,.0f}",
                    "change": None
                }
            ]
            
            recommendations = [
                f"Consider pausing '{campaign_name}' if performance is not meeting expectations",
                "Review current ad creative performance and optimize low-performing ads",
                "Analyze conversion data to ensure budget is being used effectively",
                "Consider reallocating budget to higher-performing campaigns",
                "Set up automated rules to prevent overspending"
            ]
            
            success = await email_service.send_alert_email(
                recipients=self.default_recipients,
                alert_type="budget_threshold",
                title=f"Budget Alert: {campaign_name}",
                message=f"Campaign '{campaign_name}' has used {usage_percentage:.1f}% of its budget (rm{spent:,.0f} of rm{budget:,.0f}). This exceeds the {self.alert_thresholds['campaign_budget_threshold']}% threshold.",
                severity="high",
                metrics=metrics,
                recommendations=recommendations
            )
            
            if success:
                logger.info(f"Budget alert sent for campaign '{campaign_name}'")
            else:
                logger.error(f"Failed to send budget alert for campaign '{campaign_name}'")
                
        except Exception as e:
            logger.error(f"Error sending budget alert: {str(e)}")

    async def _send_performance_alert(self, alert_title: str, performance_data: Dict[str, Any], metric_type: str):
        """
        Send performance drop alert
        """
        try:
            current = performance_data.get(f'{metric_type}_current', 0)
            previous = performance_data.get(f'{metric_type}_previous', 0)
            drop_percentage = self._calculate_percentage_change(current, previous)
            
            metrics = [
                {
                    "name": f"Current {metric_type.replace('_', ' ').title()}",
                    "value": self._format_metric_value(current, metric_type),
                    "change": f"{drop_percentage:+.1f}%"
                },
                {
                    "name": f"Previous {metric_type.replace('_', ' ').title()}",
                    "value": self._format_metric_value(previous, metric_type),
                    "change": None
                }
            ]
            
            recommendations = self._get_performance_recommendations(metric_type, drop_percentage)
            
            severity = "high" if abs(drop_percentage) > 50 else "medium"
            
            success = await email_service.send_alert_email(
                recipients=self.default_recipients,
                alert_type="performance_drop",
                title=alert_title,
                message=f"Your {metric_type.replace('_', ' ')} has dropped by {abs(drop_percentage):.1f}% from {self._format_metric_value(previous, metric_type)} to {self._format_metric_value(current, metric_type)}. This requires immediate attention.",
                severity=severity,
                metrics=metrics,
                recommendations=recommendations
            )
            
            if success:
                logger.info(f"Performance alert sent for {metric_type}")
            else:
                logger.error(f"Failed to send performance alert for {metric_type}")
                
        except Exception as e:
            logger.error(f"Error sending performance alert: {str(e)}")

    def _check_percentage_drop(self, current: float, previous: float, threshold: float) -> bool:
        """
        Check if percentage drop exceeds threshold
        """
        if previous is None or previous == 0 or current is None:
            return False
            
        drop_percentage = abs(self._calculate_percentage_change(current, previous))
        return drop_percentage >= threshold

    def _calculate_percentage_change(self, current: float, previous: float) -> float:
        """
        Calculate percentage change between two values
        """
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100

    def _format_metric_value(self, value: float, metric_type: str) -> str:
        """
        Format metric value based on type
        """
        if metric_type in ['revenue_current', 'revenue_previous']:
            return f"rm{value:,.0f}"
        elif metric_type in ['conversion_rate_current', 'conversion_rate_previous', 'ctr_current', 'ctr_previous']:
            return f"{value:.2f}%"
        else:
            return f"{value:,.0f}"

    def _get_performance_recommendations(self, metric_type: str, drop_percentage: float) -> List[str]:
        """
        Get performance-specific recommendations
        """
        recommendations = {
            'conversion_rate': [
                "Review and optimize your landing pages for better user experience",
                "Test different call-to-action buttons and placement",
                "Analyze your target audience and refine your targeting",
                "Check if there are technical issues affecting the conversion process",
                "Consider running A/B tests on your ad creative"
            ],
            'ctr': [
                "Refresh your ad creative with new images and copy",
                "Review your audience targeting and exclude non-performing segments",
                "Test different ad formats and placements",
                "Adjust your bidding strategy to improve ad position",
                "Analyze competitor ads for inspiration and differentiation"
            ],
            'revenue': [
                "Investigate if there are external factors affecting sales",
                "Review your pricing strategy and promotions",
                "Analyze customer feedback for potential issues",
                "Consider expanding to new marketing channels",
                "Focus budget on your highest-converting campaigns"
            ]
        }
        
        return recommendations.get(metric_type, [
            "Monitor the situation closely for trend continuation",
            "Review recent changes that might have caused this drop",
            "Consider consulting with your marketing team",
            "Analyze competitor activity and market conditions"
        ])

    def _generate_ai_insights(self, report_data: Dict[str, Any]) -> List[str]:
        """
        Generate AI insights based on report data
        """
        insights = []
        
        # Revenue trend analysis
        revenue_trend = report_data.get('revenue_trend', 'stable')
        if revenue_trend == 'up':
            insights.append("Revenue is trending upward - consider scaling successful campaigns")
        elif revenue_trend == 'down':
            insights.append("Revenue decline detected - investigate underperforming channels")
        
        # Conversion optimization
        conversion_rate = report_data.get('conversion_rate', 0)
        if conversion_rate < 3:
            insights.append("Conversion rate below industry average - focus on landing page optimization")
        elif conversion_rate > 6:
            insights.append("Excellent conversion rate - consider increasing ad spend to scale results")
        
        # Channel performance
        top_channels = report_data.get('top_channels', [])
        if top_channels:
            best_channel = top_channels[0].get('name', 'Unknown')
            insights.append(f"{best_channel} is your top-performing channel - allocate more budget here")
        
        # Weekend performance
        insights.append("Weekend campaigns typically show 32% better performance - consider scheduling more ads for weekends")
        
        # Mobile optimization
        insights.append("Mobile users show 65% higher conversion rates - ensure mobile-optimized landing pages")
        
        return insights[:4]  # Return top 4 insights

# Global alert service instance
alert_service = MarketingAlertService()

# Example usage functions
async def trigger_sample_alerts():
    """
    Trigger sample alerts for demonstration
    """
    # Sample campaign budget alert
    await alert_service.check_campaign_budget_alert({
        'name': 'Summer Sale 2024',
        'budget': 25000,
        'spent': 21000,  # 84% usage
        'status': 'active'
    })
    
    # Sample performance alert
    await alert_service.check_performance_alert({
        'conversion_rate_current': 2.1,
        'conversion_rate_previous': 4.2,
        'ctr_current': 1.8,
        'ctr_previous': 3.5,
        'revenue_current': 18500,
        'revenue_previous': 24000
    })

async def send_sample_weekly_report():
    """
    Send sample weekly report
    """
    await alert_service.send_weekly_report({
        'week_start': '2024-01-01',
        'week_end': '2024-01-07',
        'total_revenue': '48,500',
        'revenue_change': '+12.5%',
        'revenue_trend': 'up',
        'total_conversions': '245',
        'conversion_change': '+8.3%',
        'conversion_trend': 'up',
        'website_visitors': '12,458',
        'visitor_change': '+15.2%',
        'visitor_trend': 'up',
        'active_campaigns': '12',
        'campaign_change': '+2',
        'campaign_trend': 'up',
        'top_campaigns': [
            {'name': 'Summer Sale', 'revenue': '18,500', 'performance': '85'},
            {'name': 'Product Launch', 'revenue': '15,200', 'performance': '78'},
            {'name': 'Brand Awareness', 'revenue': '14,800', 'performance': '72'}
        ]
    })
