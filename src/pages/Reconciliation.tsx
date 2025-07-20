import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  TextField,
  Alert,
  LinearProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  PlayArrow,
  Schedule,
  CheckCircle,
  Warning,
  TrendingUp,
  Settings,
  History,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import toast from 'react-hot-toast';
import axios from 'axios';
import { format, subDays } from 'date-fns';

interface ReconciliationResult {
  auto_matched: number;
  total_pos_transactions: number;
  total_bank_transactions: number;
  unmatched_pos: number;
  unmatched_bank: number;
}

const Reconciliation: React.FC = () => {
  const [dateFrom, setDateFrom] = useState<Date | null>(subDays(new Date(), 7));
  const [dateTo, setDateTo] = useState<Date | null>(new Date());
  const [reconciling, setReconciling] = useState(false);
  const [result, setResult] = useState<ReconciliationResult | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [matchThreshold, setMatchThreshold] = useState(85);

  const handleAutoReconcile = async () => {
    if (!dateFrom || !dateTo) {
      toast.error('Please select both start and end dates');
      return;
    }

    setReconciling(true);
    try {
      const response = await axios.post('/api/reconciliation/auto-reconcile', null, {
        params: {
          date_from: format(dateFrom, 'yyyy-MM-dd'),
          date_to: format(dateTo, 'yyyy-MM-dd'),
        },
      });

      setResult(response.data.results);
      toast.success('Auto-reconciliation completed successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Reconciliation failed');
    } finally {
      setReconciling(false);
    }
  };

  const reconciliationProgress = result ? (result.auto_matched / result.total_pos_transactions) * 100 : 0;

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
          Auto Reconciliation Engine
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Automatically match POS and Bank transactions using AI-powered algorithms.
        </Typography>

        <Grid container spacing={3}>
          {/* Reconciliation Controls */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Reconciliation Parameters
                </Typography>
                
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={12} sm={6}>
                    <DatePicker
                      label="Start Date"
                      value={dateFrom}
                      onChange={setDateFrom}
                      renderInput={(params) => <TextField {...params} fullWidth />}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <DatePicker
                      label="End Date"
                      value={dateTo}
                      onChange={setDateTo}
                      renderInput={(params) => <TextField {...params} fullWidth />}
                    />
                  </Grid>
                </Grid>

                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<PlayArrow />}
                    onClick={handleAutoReconcile}
                    disabled={reconciling || !dateFrom || !dateTo}
                    sx={{ minWidth: 200 }}
                  >
                    {reconciling ? 'Processing...' : 'Start Auto Reconciliation'}
                  </Button>
                  
                  <Button
                    variant="outlined"
                    startIcon={<Settings />}
                    onClick={() => setShowSettings(true)}
                  >
                    Settings
                  </Button>
                  
                  <Button
                    variant="outlined"
                    startIcon={<History />}
                  >
                    View History
                  </Button>
                </Box>

                {reconciling && (
                  <Box sx={{ mt: 3 }}>
                    <Alert severity="info" sx={{ mb: 2 }}>
                      Processing transactions... This may take a few minutes depending on the data volume.
                    </Alert>
                    <LinearProgress />
                  </Box>
                )}
              </CardContent>
            </Card>

            {/* Results */}
            {result && (
              <Card sx={{ mt: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Reconciliation Results
                  </Typography>
                  
                  <Grid container spacing={3} sx={{ mb: 3 }}>
                    <Grid item xs={6} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="success.main" fontWeight="bold">
                          {result.auto_matched}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Auto Matched
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="primary.main" fontWeight="bold">
                          {result.total_pos_transactions}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          POS Total
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="warning.main" fontWeight="bold">
                          {result.unmatched_pos}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Unmatched POS
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="info.main" fontWeight="bold">
                          {result.unmatched_bank}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Unmatched Bank
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>

                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Success Rate</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {reconciliationProgress.toFixed(1)}%
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={reconciliationProgress} 
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>

                  <Alert severity="success">
                    Successfully processed {result.total_pos_transactions} POS transactions and {result.total_bank_transactions} bank transactions.
                  </Alert>
                </CardContent>
              </Card>
            )}
          </Grid>

          {/* Sidebar */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Matching Criteria
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <CheckCircle color="success" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Amount Matching"
                      secondary="Exact or within 1% variance"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Schedule color="primary" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Date Matching"
                      secondary="Same day or within 72 hours"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <TrendingUp color="warning" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Reference Numbers"
                      secondary="Fuzzy matching algorithm"
                    />
                  </ListItem>
                </List>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle2" gutterBottom>
                  Current Settings
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip label={`Threshold: ${matchThreshold}%`} size="small" />
                  <Chip label="AI Enabled" size="small" color="primary" />
                  <Chip label="Auto-mode" size="small" color="success" />
                </Box>
              </CardContent>
            </Card>

            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Actions
                </Typography>
                <Button fullWidth variant="outlined" sx={{ mb: 1 }}>
                  View Unmatched Transactions
                </Button>
                <Button fullWidth variant="outlined" sx={{ mb: 1 }}>
                  Exception Dashboard
                </Button>
                <Button fullWidth variant="outlined">
                  Export Results
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Settings Dialog */}
        <Dialog open={showSettings} onClose={() => setShowSettings(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Reconciliation Settings</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              label="Match Confidence Threshold (%)"
              type="number"
              value={matchThreshold}
              onChange={(e) => setMatchThreshold(Number(e.target.value))}
              inputProps={{ min: 50, max: 100 }}
              helperText="Minimum confidence score for auto-matching (50-100%)"
              sx={{ mt: 2 }}
            />
            
            <Alert severity="info" sx={{ mt: 2 }}>
              Higher thresholds result in more accurate matches but may leave more transactions unmatched.
            </Alert>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowSettings(false)}>Cancel</Button>
            <Button variant="contained" onClick={() => setShowSettings(false)}>
              Save Settings
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};

export default Reconciliation;