import React from 'react';
import { Box, Typography } from '@mui/material';

const Transactions: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
        Transactions
      </Typography>
      <Typography variant="body1" color="text.secondary">
        View and manage all POS and Bank transactions.
      </Typography>
    </Box>
  );
};

export default Transactions;