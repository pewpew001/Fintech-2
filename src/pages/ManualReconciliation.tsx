import React from 'react';
import { Box, Typography } from '@mui/material';

const ManualReconciliation: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
        Manual Reconciliation
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Manually match unreconciled POS and Bank transactions.
      </Typography>
    </Box>
  );
};

export default ManualReconciliation;