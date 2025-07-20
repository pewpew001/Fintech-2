import React from 'react';
import { Box, Typography } from '@mui/material';

const Reports: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
        Reports & Insights
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Generate comprehensive reports and view analytics.
      </Typography>
    </Box>
  );
};

export default Reports;