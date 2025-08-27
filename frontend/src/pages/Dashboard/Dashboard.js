import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Avatar,
  LinearProgress,
  IconButton,
  Tooltip,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Dashboard as DashboardIcon,
  Psychology,
  GroupWork,
  NotificationsActive,
  Refresh,
  Visibility,
  Campaign,
  Analytics,
  SmartToy,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import axios from 'axios';

// Components
import MetricCard from '../../components/Dashboard/MetricCard';
import ChartCard from '../../components/Dashboard/ChartCard';
import RecentActivity from '../../components/Dashboard/RecentActivity';
import QuickActions from '../../components/Dashboard/QuickActions';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    totalCampaigns: 0,
    activeCampaigns: 0,
    totalRevenue: 0,
    conversionRate: 0,
    roas: 0,
    totalImpressions: 0,
    totalClicks: 0,
    totalConversions: 0,
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [features, setFeatures] = useState([]);

  useEffect(() => {
    fetchDashboardData();
    fetchFeatures();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // In a real app, you'd fetch from your API
      // const response = await axios.get('/api/dashboard/metrics');
      
      // Mock data for demonstration
      const mockMetrics = {
        totalCampaigns: 24,
        activeCampaigns: 8,
        totalRevenue: 125000,
        conversionRate: 3.2,
        roas: 2.8,
        totalImpressions: 1250000,
        totalClicks: 45000,
        totalConversions: 1440,
      };
      
      setMetrics(mockMetrics);
      setLoading(false);
    } catch (err) {
      setError('Failed to load dashboard data');
      setLoading(false);
    }
  };

  const fetchFeatures = async () => {
    try {
      const response = await axios.get('/api/features');
      setFeatures(response.data.features || []);
    } catch (err) {
      console.error('Failed to fetch features:', err);
    }
  };

  const handleRefresh = () => {
    fetchDashboardData();
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button onClick={fetchDashboardData} variant="contained">
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
            Marketing Intelligence Dashboard
          </Typography>
          <Tooltip title="Refresh Data">
            <IconButton onClick={handleRefresh} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Real-time insights and AI-powered predictions for your marketing campaigns
        </Typography>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Campaigns"
            value={metrics.totalCampaigns}
            icon={<Campaign />}
            color="primary"
            trend={+5}
            trendLabel="vs last month"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Campaigns"
            value={metrics.activeCampaigns}
            icon={<TrendingUp />}
            color="success"
            trend={+2}
            trendLabel="vs last week"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Revenue"
            value={`$${(metrics.totalRevenue / 1000).toFixed(0)}K`}
            icon={<TrendingUp />}
            color="success"
            trend={+12.5}
            trendLabel="vs last month"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Conversion Rate"
            value={`${metrics.conversionRate}%`}
            icon={<TrendingUp />}
            color="success"
            trend={+0.8}
            trendLabel="vs last month"
          />
        </Grid>
      </Grid>

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <MetricCard
            title="ROAS"
            value={metrics.roas}
            icon={<TrendingUp />}
            color="success"
            trend={+0.3}
            trendLabel="vs last month"
            subtitle="Return on Ad Spend"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <MetricCard
            title="Total Impressions"
            value={`${(metrics.totalImpressions / 1000000).toFixed(1)}M`}
            icon={<Visibility />}
            color="info"
            trend={+8.2}
            trendLabel="vs last month"
          />
        </Grid>
      </Grid>

      {/* Platform Features */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
            <DashboardIcon color="primary" />
            Platform Features
          </Typography>
          <Grid container spacing={2}>
            {features.map((feature) => (
              <Grid item xs={12} sm={6} md={3} key={feature.id}>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  transition={{ duration: 0.2 }}
                >
                  <Card 
                    variant="outlined" 
                    sx={{ 
                      p: 2, 
                      textAlign: 'center',
                      cursor: 'pointer',
                      '&:hover': { borderColor: 'primary.main' }
                    }}
                  >
                    <Box sx={{ mb: 1 }}>
                      {feature.icon === 'dashboard' && <DashboardIcon color="primary" sx={{ fontSize: 40 }} />}
                      {feature.icon === 'psychology' && <Psychology color="primary" sx={{ fontSize: 40 }} />}
                      {feature.icon === 'group_work' && <GroupWork color="primary" sx={{ fontSize: 40 }} />}
                      {feature.icon === 'notifications_active' && <NotificationsActive color="primary" sx={{ fontSize: 40 }} />}
                    </Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {feature.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {feature.description}
                    </Typography>
                    <Chip 
                      label={feature.enabled ? "Active" : "Coming Soon"} 
                      color={feature.enabled ? "success" : "default"}
                      size="small"
                    />
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Charts and Analytics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={8}>
          <ChartCard
            title="Campaign Performance Over Time"
            subtitle="Revenue, Conversions, and ROAS trends"
            height={400}
          >
            {/* Chart component would go here */}
            <Box sx={{ 
              height: 350, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              bgcolor: 'grey.50',
              borderRadius: 1
            }}>
              <Typography color="text.secondary">
                Chart: Campaign Performance Over Time
              </Typography>
            </Box>
          </ChartCard>
        </Grid>
        <Grid item xs={12} lg={4}>
          <ChartCard
            title="Channel Performance"
            subtitle="Top performing marketing channels"
            height={400}
          >
            {/* Chart component would go here */}
            <Box sx={{ 
              height: 350, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              bgcolor: 'grey.50',
              borderRadius: 1
            }}>
              <Typography color="text.secondary">
                Chart: Channel Performance
              </Typography>
            </Box>
          </ChartCard>
        </Grid>
      </Grid>

      {/* Bottom Row */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={6}>
          <RecentActivity />
        </Grid>
        <Grid item xs={12} lg={6}>
          <QuickActions />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
