import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Alert,
  LinearProgress,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  Dashboard,
  Refresh,
  Settings,
  Fullscreen,
  Share,
  Download,
  FilterList,
  Visibility,
  TrendingUp,
  Analytics,
} from '@mui/icons-material';
import axios from 'axios';

const PowerBIDashboard = () => {
  const [embedConfig, setEmbedConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  [error, setError] = useState(null);
  const [workspaces, setWorkspaces] = useState([]);
  const [reports, setReports] = useState([]);
  const [selectedWorkspace, setSelectedWorkspace] = useState('');
  const [selectedReport, setSelectedReport] = useState('');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [embedSettings, setEmbedSettings] = useState({
    theme: 'light',
    filterPaneEnabled: true,
    navContentPaneEnabled: true,
    showReportNavigation: true,
  });

  useEffect(() => {
    fetchWorkspaces();
  }, []);

  useEffect(() => {
    if (selectedWorkspace) {
      fetchReports(selectedWorkspace);
    }
  }, [selectedWorkspace]);

  useEffect(() => {
    if (selectedReport && selectedWorkspace) {
      generateEmbedConfig();
    }
  }, [selectedReport, selectedWorkspace]);

  const fetchWorkspaces = async () => {
    try {
      const response = await axios.get('/api/powerbi/workspaces');
      setWorkspaces(response.data || []);
      if (response.data && response.data.length > 0) {
        setSelectedWorkspace(response.data[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch workspaces:', err);
      setError('Failed to load Power BI workspaces');
    }
  };

  const fetchReports = async (workspaceId) => {
    try {
      const response = await axios.get(`/api/powerbi/reports?workspace_id=${workspaceId}`);
      setReports(response.data || []);
      if (response.data && response.data.length > 0) {
        setSelectedReport(response.data[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch reports:', err);
      setError('Failed to load Power BI reports');
    }
  };

  const generateEmbedConfig = async () => {
    try {
      setLoading(true);
      const response = await axios.post('/api/powerbi/embed-config', {
        report_id: selectedReport,
        workspace_id: selectedWorkspace,
      });
      
      if (response.data.error) {
        setError(response.data.error);
      } else {
        setEmbedConfig(response.data);
        setError(null);
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to generate embed config:', err);
      setError('Failed to generate Power BI embed configuration');
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    if (selectedReport && selectedWorkspace) {
      generateEmbedConfig();
    }
  };

  const handleFullscreen = () => {
    const iframe = document.getElementById('powerbi-iframe');
    if (iframe) {
      if (iframe.requestFullscreen) {
        iframe.requestFullscreen();
      }
    }
  };

  const handleShare = () => {
    // Implement sharing functionality
    console.log('Share functionality');
  };

  const handleDownload = () => {
    // Implement download functionality
    console.log('Download functionality');
  };

  const handleSettingsSave = () => {
    setSettingsOpen(false);
    // Apply new settings to iframe
    if (embedConfig) {
      generateEmbedConfig();
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Loading Power BI Dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
            <Dashboard color="primary" />
            Power BI Dashboard
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Settings">
              <IconButton onClick={() => setSettingsOpen(true)} color="primary">
                <Settings />
              </IconButton>
            </Tooltip>
            <Tooltip title="Refresh">
              <IconButton onClick={handleRefresh} color="primary">
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Interactive Power BI dashboards with real-time marketing analytics and insights
        </Typography>
      </Box>

      {/* Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Workspace</InputLabel>
                <Select
                  value={selectedWorkspace}
                  onChange={(e) => setSelectedWorkspace(e.target.value)}
                  label="Workspace"
                >
                  {workspaces.map((workspace) => (
                    <MenuItem key={workspace.id} value={workspace.id}>
                      {workspace.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Report</InputLabel>
                <Select
                  value={selectedReport}
                  onChange={(e) => setSelectedReport(e.target.value)}
                  label="Report"
                  disabled={!selectedWorkspace}
                >
                  {reports.map((report) => (
                    <MenuItem key={report.id} value={report.id}>
                      {report.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<FilterList />}
                  onClick={() => setSettingsOpen(true)}
                >
                  Filters
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Analytics />}
                  onClick={handleRefresh}
                >
                  Refresh Data
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Power BI Dashboard */}
      {embedConfig && !error ? (
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ p: 0 }}>
            {/* Dashboard Header */}
            <Box sx={{ 
              p: 2, 
              borderBottom: 1, 
              borderColor: 'divider',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  {embedConfig.report_name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {embedConfig.report_type} • Last updated: {new Date(embedConfig.timestamp).toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Tooltip title="Share">
                  <IconButton onClick={handleShare} size="small">
                    <Share />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Download">
                  <IconButton onClick={handleDownload} size="small">
                    <Download />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Fullscreen">
                  <IconButton onClick={handleFullscreen} size="small">
                    <Fullscreen />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>

            {/* Power BI Embed */}
            <Box sx={{ position: 'relative', minHeight: 600 }}>
              <iframe
                id="powerbi-iframe"
                title="Power BI Dashboard"
                width="100%"
                height="600"
                src={`${embedConfig.embed_url}&embedToken=${embedConfig.embed_token}`}
                frameBorder="0"
                allowFullScreen={true}
                style={{
                  border: 'none',
                  borderRadius: '0 0 8px 8px'
                }}
              />
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ 
              textAlign: 'center', 
              py: 8,
              color: 'text.secondary'
            }}>
              <Dashboard sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
              <Typography variant="h6" sx={{ mb: 1 }}>
                No Dashboard Selected
              </Typography>
              <Typography variant="body2">
                Please select a workspace and report to view the Power BI dashboard
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Dashboard Info */}
      {embedConfig && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Visibility color="primary" />
                  Dashboard Information
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Report ID:</Typography>
                    <Typography variant="body2" fontFamily="monospace">{embedConfig.report_id}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Workspace ID:</Typography>
                    <Typography variant="body2" fontFamily="monospace">{embedConfig.workspace_id}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Token Expires:</Typography>
                    <Typography variant="body2">
                      {new Date(embedConfig.expiration).toLocaleString()}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TrendingUp color="primary" />
                  Quick Actions
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<Refresh />}
                    onClick={handleRefresh}
                    fullWidth
                  >
                    Refresh Dashboard
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Settings />}
                    onClick={() => setSettingsOpen(true)}
                    fullWidth
                  >
                    Configure Settings
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Share />}
                    onClick={handleShare}
                    fullWidth
                  >
                    Share Dashboard
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Dashboard Settings</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Theme</InputLabel>
                <Select
                  value={embedSettings.theme}
                  onChange={(e) => setEmbedSettings({ ...embedSettings, theme: e.target.value })}
                  label="Theme"
                >
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="dark">Dark</MenuItem>
                  <MenuItem value="contrast">High Contrast</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Filter Pane</InputLabel>
                <Select
                  value={embedSettings.filterPaneEnabled ? 'enabled' : 'disabled'}
                  onChange={(e) => setEmbedSettings({ 
                    ...embedSettings, 
                    filterPaneEnabled: e.target.value === 'enabled' 
                  })}
                  label="Filter Pane"
                >
                  <MenuItem value="enabled">Enabled</MenuItem>
                  <MenuItem value="disabled">Disabled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Navigation</InputLabel>
                <Select
                  value={embedSettings.showReportNavigation ? 'enabled' : 'disabled'}
                  onChange={(e) => setEmbedSettings({ 
                    ...embedSettings, 
                    showReportNavigation: e.target.value === 'enabled' 
                  })}
                  label="Navigation"
                >
                  <MenuItem value="enabled">Enabled</MenuItem>
                  <MenuItem value="disabled">Disabled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Cancel</Button>
          <Button onClick={handleSettingsSave} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PowerBIDashboard;
