import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
} from '@mui/material';
import { CloudUpload, Download, Delete, CheckCircle, Error } from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import axios from 'axios';

interface UploadResult {
  filename: string;
  status: 'success' | 'error';
  message: string;
  count?: number;
  errors?: string[];
}

const DataUpload: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState<UploadResult[]>([]);

  const handleUpload = async (files: File[], type: 'pos' | 'bank') => {
    setUploading(true);
    const results: UploadResult[] = [];

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const endpoint = type === 'pos' 
          ? '/api/uploads/pos-transactions' 
          : '/api/uploads/bank-transactions';

        const response = await axios.post(endpoint, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        results.push({
          filename: file.name,
          status: 'success',
          message: `Successfully uploaded ${response.data.length} transactions`,
          count: response.data.length,
        });

        toast.success(`${file.name} uploaded successfully!`);
      } catch (error: any) {
        const errorMessage = error.response?.data?.detail || 'Upload failed';
        results.push({
          filename: file.name,
          status: 'error',
          message: errorMessage,
        });

        toast.error(`Failed to upload ${file.name}`);
      }
    }

    setUploadResults(prev => [...prev, ...results]);
    setUploading(false);
  };

  const UploadZone: React.FC<{ 
    title: string; 
    description: string; 
    type: 'pos' | 'bank';
    templateUrl: string;
  }> = ({ title, description, type, templateUrl }) => {
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      accept: {
        'text/csv': ['.csv'],
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
        'application/vnd.ms-excel': ['.xls'],
      },
      onDrop: (acceptedFiles) => {
        handleUpload(acceptedFiles, type);
      },
      disabled: uploading,
    });

    const downloadTemplate = async () => {
      try {
        const response = await axios.get(templateUrl, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${type}_transactions_template.csv`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (error) {
        toast.error('Failed to download template');
      }
    };

    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {description}
          </Typography>
          
          <Box
            {...getRootProps()}
            sx={{
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'grey.300',
              borderRadius: 2,
              p: 3,
              textAlign: 'center',
              cursor: 'pointer',
              bgcolor: isDragActive ? 'action.hover' : 'background.paper',
              transition: 'all 0.3s ease',
              '&:hover': {
                borderColor: 'primary.main',
                bgcolor: 'action.hover',
              },
              mb: 2,
            }}
          >
            <input {...getInputProps()} />
            <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              or click to browse
            </Typography>
            <Typography variant="caption" display="block" sx={{ mt: 1 }}>
              Supports CSV, XLS, XLSX files
            </Typography>
          </Box>

          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={downloadTemplate}
            fullWidth
          >
            Download Template
          </Button>
        </CardContent>
      </Card>
    );
  };

  const clearResults = () => {
    setUploadResults([]);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
        Data Upload & Import
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload your transaction data via CSV or Excel files. You can upload both POS and Bank transactions.
      </Typography>

      {uploading && (
        <Box sx={{ mb: 3 }}>
          <Alert severity="info" sx={{ mb: 1 }}>
            Uploading files... Please wait.
          </Alert>
          <LinearProgress />
        </Box>
      )}

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <UploadZone
            title="POS Transactions"
            description="Upload POS transaction data with terminal information"
            type="pos"
            templateUrl="/api/uploads/template/pos"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <UploadZone
            title="Bank Transactions"
            description="Upload bank transaction data for reconciliation"
            type="bank"
            templateUrl="/api/uploads/template/bank"
          />
        </Grid>
      </Grid>

      {uploadResults.length > 0 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Upload Results
              </Typography>
              <Button
                variant="outlined"
                startIcon={<Delete />}
                onClick={clearResults}
                size="small"
              >
                Clear
              </Button>
            </Box>
            
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>File Name</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Records</TableCell>
                    <TableCell>Message</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {uploadResults.map((result, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {result.filename}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={result.status === 'success' ? <CheckCircle /> : <Error />}
                          label={result.status}
                          color={result.status === 'success' ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {result.count || '-'}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {result.message}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      <Box sx={{ mt: 4 }}>
        <Alert severity="info">
          <Typography variant="subtitle2" gutterBottom>
            Upload Guidelines:
          </Typography>
          <Typography variant="body2" component="div">
            • Ensure your files contain the required columns (see templates)
            • Date format should be YYYY-MM-DD or DD/MM/YYYY
            • Amount should be numeric values only
            • Remove any header rows except column names
            • Maximum file size: 10MB per file
          </Typography>
        </Alert>
      </Box>
    </Box>
  );
};

export default DataUpload;