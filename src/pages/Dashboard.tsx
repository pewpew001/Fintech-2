import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Button,
  IconButton,
  Paper,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Warning,
  Error,
  Refresh,
  Download,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Sample data - replace with actual API calls
const summaryData = {
  total_pos_transactions: 2456,
  total_bank_transactions: 2398,
  matched_transactions: 2234,
  unmatched_pos: 222,
  unmatched_bank: 164,
  exceptions: 58,
  total_pos_amount: 1234567.89,
  total_bank_amount: 1228945.23,
  matched_amount: 1198234.56,
  variance_amount: 5622.66,
};

const chartData = [
  { name: 'Mon', pos: 345, bank: 342, matched: 338 },
  { name: 'Tue', pos: 423, bank: 419, matched: 415 },
  { name: 'Wed', pos: 378, bank: 375, matched: 370 },
  { name: 'Thu', pos: 456, bank: 448, matched: 442 },
  { name: 'Fri', pos: 389, bank: 385, matched: 380 },
  { name: 'Sat', pos: 267, bank: 265, matched: 262 },
  { name: 'Sun', pos: 198, bank: 164, matched: 158 },
];

const reconciliationStatusData = [
  { name: 'Matched', value: 2234, color: '#4caf50' },
  { name: 'Pending POS', value: 222, color: '#ff9800' },
  { name: 'Pending Bank', value: 164, color: '#2196f3' },
  { name: 'Exceptions', value: 58, color: '#f44336' },
];

const StatCard: React.FC<{
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactElement;
  color: 'primary' | 'success' | 'warning' | 'error';
  trend?: {
    value: number;
    isPositive: boolean;
  };
}> = ({ title, value, subtitle, icon, color, trend }) => {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="text.secondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" fontWeight="bold">
              {typeof value === 'number' ? value.toLocaleString() : value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
            {trend && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                {trend.isPositive ? (
                  <TrendingUp sx={{ color: 'success.main', mr: 0.5 }} />
                ) : (
                  <TrendingDown sx={{ color: 'error.main', mr: 0.5 }} />
                )}
                <Typography
                  variant="caption"
                  sx={{
                    color: trend.isPositive ? 'success.main' : 'error.main',
                    fontWeight: 'medium',
                  }}
                >
                  {Math.abs(trend.value)}% from last week
                </Typography>
              </Box>
            )}
          </Box>
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              backgroundColor: `${color}.light`,
              color: `${color}.contrastText`,
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

const Dashboard: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate refresh
    setTimeout(() => setRefreshing(false), 2000);
  };

  const reconciliationRate = summaryData.total_pos_transactions > 0 
    ? (summaryData.matched_transactions / summaryData.total_pos_transactions) * 100 
    : 0;

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Dashboard Overview
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <IconButton onClick={handleRefresh} disabled={refreshing}>
            <Refresh sx={{ transform: refreshing ? 'rotate(180deg)' : 'none', transition: 'transform 0.3s' }} />
          </IconButton>
          <Button variant="outlined" startIcon={<Download />}>
            Export Report
          </Button>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total POS Transactions"
            value={summaryData.total_pos_transactions}
            subtitle={`₦${summaryData.total_pos_amount.toLocaleString()}`}
            icon={<CheckCircle />}
            color="primary"
            trend={{ value: 12.5, isPositive: true }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Matched Transactions"
            value={summaryData.matched_transactions}
            subtitle={`₦${summaryData.matched_amount.toLocaleString()}`}
            icon={<CheckCircle />}
            color="success"
            trend={{ value: 8.2, isPositive: true }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Reconciliation"
            value={summaryData.unmatched_pos + summaryData.unmatched_bank}
            subtitle="Needs attention"
            icon={<Warning />}
            color="warning"
            trend={{ value: 3.1, isPositive: false }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Exceptions"
            value={summaryData.exceptions}
            subtitle="Requires manual review"
            icon={<Error />}
            color="error"
            trend={{ value: 15.3, isPositive: false }}
          />
        </Grid>
      </Grid>

      {/* Reconciliation Rate */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Weekly Transaction Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="pos" fill="#2196f3" name="POS Transactions" />
                  <Bar dataKey="bank" fill="#4caf50" name="Bank Transactions" />
                  <Bar dataKey="matched" fill="#ff9800" name="Matched" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Reconciliation Status
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={reconciliationStatusData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {reconciliationStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Performance Metrics */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Reconciliation Performance
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Overall Rate</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {reconciliationRate.toFixed(1)}%
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={reconciliationRate} 
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip 
                  label={`Auto-matched: 89.2%`} 
                  color="success" 
                  size="small" 
                />
                <Chip 
                  label={`Manual: 8.5%`} 
                  color="primary" 
                  size="small" 
                />
                <Chip 
                  label={`Exceptions: 2.3%`} 
                  color="error" 
                  size="small" 
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Last reconciliation: 2 hours ago
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Next auto-reconciliation: In 4 hours
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Active users: 3 analysts online
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  System status: All services operational
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;