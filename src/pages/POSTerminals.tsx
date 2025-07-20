import React from 'react';
import { Box, Typography } from '@mui/material';

const POSTerminals: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
        POS Terminals
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Manage and monitor all POS terminals with their transaction history.
      </Typography>
    </Box>
  );
};

export default POSTerminals;