import React from 'react';
import { Box, Typography } from '@mui/material';

const ExceptionDashboard: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
        Exception Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Monitor and resolve transaction exceptions and anomalies.
      </Typography>
    </Box>
  );
};

export default ExceptionDashboard;