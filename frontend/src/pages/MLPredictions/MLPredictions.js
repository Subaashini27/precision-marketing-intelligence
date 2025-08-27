import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  LinearProgress,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Paper,
} from '@mui/material';
import {
  Psychology,
  TrendingUp,
  TrendingDown,
  Refresh,
  Info,
  CheckCircle,
  Warning,
  Error,
  Lightbulb,
  Analytics,
  SmartToy,
  Assessment,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import axios from 'axios';

const MLPredictions = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [predictionType, setPredictionType] = useState('conversion');
  const [inputFeatures, setInputFeatures] = useState({});
  const [showInputForm, setShowInputForm] = useState(false);
  const [modelStatus, setModelStatus] = useState({});

  useEffect(() => {
    fetchModelStatus();
    loadSampleData();
  }, []);

  const fetchModelStatus = async () => {
    try {
      const response = await axios.get('/api/ml/status');
      setModelStatus(response.data);
    } catch (err) {
      console.error('Failed to fetch model status:', err);
    }
  };

  const loadSampleData = () => {
    // Sample input features for different prediction types
    const sampleData = {
      conversion: {
        time_on_site: 300,
        page_views: 5,
        bounce_rate: 0.3,
        source: 'google',
        device: 'desktop',
        location: 'US',
        age_group: '25-34',
        previous_purchases: 2,
      },
      churn: {
        days_since_last_purchase: 45,
        total_purchases: 8,
        avg_order_value: 150,
        customer_satisfaction: 4.2,
        support_tickets: 1,
        email_engagement: 0.7,
        loyalty_program_tier: 'gold',
      },
      roi: {
        campaign_budget: 5000,
        target_audience_size: 100000,
        avg_cpc: 2.5,
        conversion_rate: 0.025,
        avg_order_value: 200,
        campaign_duration: 30,
        channel: 'facebook',
      },
      campaign_performance: {
        budget: 10000,
        target_audience: 50000,
        creative_quality: 8.5,
        targeting_precision: 9.0,
        seasonality_factor: 1.2,
        competition_level: 'medium',
        channel_mix: 'multi',
      },
    };

    setInputFeatures(sampleData[predictionType] || {});
  };

  const handlePredictionTypeChange = (event) => {
    const newType = event.target.value;
    setPredictionType(newType);
    loadSampleData();
  };

  const handleInputChange = (field, value) => {
    setInputFeatures(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const generatePrediction = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.post('/api/ml/predict', {
        prediction_type: predictionType,
        features: inputFeatures,
      });

      if (response.data.error) {
        setError(response.data.error);
      } else {
        const newPrediction = {
          ...response.data,
          id: Date.now(),
          timestamp: new Date().toISOString(),
        };
        setPredictions(prev => [newPrediction, ...prev]);
      }
    } catch (err) {
      console.error('Prediction failed:', err);
      setError('Failed to generate prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getPredictionIcon = (prediction) => {
    if (prediction.prediction_type === 'conversion') {
      return prediction.prediction_probability > 0.7 ? 
        <CheckCircle color="success" /> : 
        <Warning color="warning" />;
    } else if (prediction.prediction_type === 'churn') {
      return prediction.prediction_probability < 0.3 ? 
        <CheckCircle color="success" /> : 
        <Error color="error" />;
    }
    return <Analytics color="info" />;
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      default: return 'default';
    }
  };

  const getPerformanceColor = (level) => {
    switch (level) {
      case 'excellent': return 'success';
      case 'good': return 'info';
      case 'average': return 'warning';
      case 'poor': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
            <Psychology color="primary" />
            AI/ML Predictions
          </Typography>
          <Button
            variant="contained"
            startIcon={<Psychology />}
            onClick={() => setShowInputForm(true)}
          >
            New Prediction
          </Button>
        </Box>
        <Typography variant="body1" color="text.secondary">
          AI-powered predictions for conversion likelihood, churn risk, ROI forecasting, and campaign performance
        </Typography>
      </Box>

      {/* Model Status */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <SmartToy color="primary" />
            Model Status
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                  {modelStatus.total_models || 4}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Models Loaded
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h4" color="success.main" sx={{ fontWeight: 'bold' }}>
                  {modelStatus.status === 'ready' ? 'Ready' : 'Loading'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  System Status
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h4" color="info.main" sx={{ fontWeight: 'bold' }}>
                  {predictions.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Predictions Made
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h4" color="warning.main" sx={{ fontWeight: 'bold' }}>
                  99.2%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Model Accuracy
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Prediction Types */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ scale: 1.05 }}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                border: predictionType === 'conversion' ? 2 : 1,
                borderColor: predictionType === 'conversion' ? 'primary.main' : 'divider',
                '&:hover': { borderColor: 'primary.main' }
              }}
              onClick={() => setPredictionType('conversion')}
            >
              <CardContent sx={{ textAlign: 'center' }}>
                <TrendingUp color="primary" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Conversion Prediction
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Predict customer conversion likelihood
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ scale: 1.05 }}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                border: predictionType === 'churn' ? 2 : 1,
                borderColor: predictionType === 'churn' ? 'primary.main' : 'divider',
                '&:hover': { borderColor: 'primary.main' }
              }}
              onClick={() => setPredictionType('churn')}
            >
              <CardContent sx={{ textAlign: 'center' }}>
                <TrendingDown color="error" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Churn Risk
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Assess customer retention risk
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ scale: 1.05 }}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                border: predictionType === 'roi' ? 2 : 1,
                borderColor: predictionType === 'roi' ? 'primary.main' : 'divider',
                '&:hover': { borderColor: 'primary.main' }
              }}
              onClick={() => setPredictionType('roi')}
            >
              <CardContent sx={{ textAlign: 'center' }}>
                <Analytics color="success" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  ROI Prediction
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Forecast campaign return on investment
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <motion.div whileHover={{ scale: 1.05 }}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                border: predictionType === 'campaign_performance' ? 2 : 1,
                borderColor: predictionType === 'campaign_performance' ? 'primary.main' : 'divider',
                '&:hover': { borderColor: 'primary.main' }
              }}
              onClick={() => setPredictionType('campaign_performance')}
            >
              <CardContent sx={{ textAlign: 'center' }}>
                <Assessment color="info" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Campaign Performance
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Predict overall campaign success
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Recent Predictions */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Assessment color="primary" />
            Recent Predictions
          </Typography>
          
          {predictions.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
              <Psychology sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
              <Typography variant="h6" sx={{ mb: 1 }}>
                No Predictions Yet
              </Typography>
              <Typography variant="body2">
                Generate your first AI prediction to see insights and recommendations
              </Typography>
            </Box>
          ) : (
            <List>
              {predictions.map((prediction, index) => (
                <React.Fragment key={prediction.id}>
                  <ListItem>
                    <ListItemIcon>
                      {getPredictionIcon(prediction)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                            {prediction.prediction_type.replace('_', ' ').toUpperCase()}
                          </Typography>
                          {prediction.risk_level && (
                            <Chip 
                              label={prediction.risk_level.toUpperCase()} 
                              color={getRiskColor(prediction.risk_level)}
                              size="small"
                            />
                          )}
                          {prediction.performance_level && (
                            <Chip 
                              label={prediction.performance_level.toUpperCase()} 
                              color={getPerformanceColor(prediction.performance_level)}
                              size="small"
                            />
                          )}
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            <strong>Score:</strong> {prediction.prediction_value.toFixed(3)}
                            {prediction.prediction_probability && (
                              <span> • <strong>Probability:</strong> {(prediction.prediction_probability * 100).toFixed(1)}%</span>
                            )}
                          </Typography>
                          {prediction.insights && (
                            <Box sx={{ mb: 1 }}>
                              <Typography variant="body2" color="text.secondary">
                                <strong>Insights:</strong>
                              </Typography>
                              {prediction.insights.map((insight, i) => (
                                <Typography key={i} variant="body2" color="text.secondary" sx={{ ml: 2 }}>
                                  • {insight}
                                </Typography>
                              ))}
                            </Box>
                          )}
                          {prediction.recommendations && (
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                <strong>Recommendations:</strong>
                              </Typography>
                              {prediction.recommendations.map((rec, i) => (
                                <Typography key={i} variant="body2" color="text.secondary" sx={{ ml: 2 }}>
                                  • {rec}
                                </Typography>
                              ))}
                            </Box>
                          )}
                          <Typography variant="caption" color="text.secondary">
                            Generated: {new Date(prediction.timestamp).toLocaleString()}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < predictions.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Input Form Dialog */}
      <Dialog open={showInputForm} onClose={() => setShowInputForm(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Psychology color="primary" />
            Generate {predictionType.replace('_', ' ').toUpperCase()} Prediction
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              {Object.entries(inputFeatures).map(([field, value]) => (
                <Grid item xs={12} sm={6} key={field}>
                  <TextField
                    fullWidth
                    label={field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    value={value}
                    onChange={(e) => handleInputChange(field, e.target.value)}
                    type={typeof value === 'number' ? 'number' : 'text'}
                    variant="outlined"
                  />
                </Grid>
              ))}
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowInputForm(false)}>Cancel</Button>
          <Button 
            onClick={generatePrediction} 
            variant="contained"
            disabled={loading}
            startIcon={loading ? <LinearProgress /> : <Psychology />}
          >
            {loading ? 'Generating...' : 'Generate Prediction'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default MLPredictions;
