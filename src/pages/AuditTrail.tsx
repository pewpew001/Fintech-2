import React from 'react';
import { Box, Typography } from '@mui/material';

const AuditTrail: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
        Audit Trail
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Track all user actions and system changes.
      </Typography>
    </Box>
  );
};

export default AuditTrail;