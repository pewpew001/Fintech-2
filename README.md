# POS Reconciliation Dashboard

A comprehensive bank and POS transaction reconciliation system built with FastAPI (Python) backend and React (TypeScript) frontend. The system provides automated reconciliation using AI-powered matching algorithms, manual reconciliation capabilities, and complete audit trails.

## 🚀 Features

### Core Functionality
- **POS Terminal Management**: Complete terminal information with real-time transaction tracking
- **Automated Reconciliation**: AI-powered matching engine with configurable confidence thresholds
- **Manual Reconciliation**: Drag-and-drop interface for manual transaction matching
- **Exception Handling**: Comprehensive exception dashboard with filtering and resolution workflows
- **Bulk Data Upload**: Support for CSV/Excel uploads with field mapping and validation
- **Real-time Dashboard**: Live statistics, charts, and performance metrics

### Advanced Features
- **Smart Matching Algorithm**: Uses multiple criteria (amount, date, reference, terminal ID, merchant name)
- **Role-based Access Control**: Admin, Reviewer, Analyst, and Viewer roles with granular permissions
- **Comprehensive Reporting**: Exportable reports in CSV/Excel with various formats
- **Audit Trail**: Complete action logging with user tracking and change history
- **Google Sheets Integration**: Live data sync from Google Sheets (optional)
- **Mobile Responsive**: Optimized for desktop, tablet, and mobile devices

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Robust relational database
- **SQLAlchemy**: ORM for database operations
- **Pandas**: Data processing and analysis
- **Scikit-learn**: Machine learning for smart matching
- **JWT Authentication**: Secure token-based authentication
- **Celery + Redis**: Background task processing

### Frontend
- **React 18**: Modern UI library with hooks
- **TypeScript**: Type-safe JavaScript
- **Material-UI (MUI)**: Professional component library
- **React Query**: Data fetching and state management
- **React Router**: Client-side routing
- **Recharts**: Data visualization
- **React Dropzone**: File upload interface

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis (optional, for background tasks)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd pos-reconciliation-dashboard
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
alembic upgrade head

# Create initial admin user
python scripts/create_admin.py

# Start the backend server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
# Install dependencies
npm install

# Start the development server
npm start
```

### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/pos_reconciliation

# Security
SECRET_KEY=your-secret-key-here

# Server
HOST=0.0.0.0
PORT=8000

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_FOLDER=./uploads

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-password

# Redis (optional)
REDIS_URL=redis://localhost:6379
```

### Default Users

The system comes with default demo users:

- **Admin**: username: `admin`, password: `admin123`
- **Analyst**: username: `analyst`, password: `analyst123`

## 📊 Usage Guide

### 1. Data Upload
- Navigate to "Data Upload" section
- Download CSV templates for POS and Bank transactions
- Upload your transaction files via drag-and-drop interface
- Review upload results and error logs

### 2. Auto Reconciliation
- Go to "Auto Reconciliation" page
- Select date range for reconciliation
- Configure matching thresholds if needed
- Click "Start Auto Reconciliation"
- Review results and success rate

### 3. Manual Reconciliation
- Access "Manual Reconciliation" for unmatched transactions
- Use side-by-side view to compare POS and Bank transactions
- Drag and drop to create manual matches
- Add comments for audit purposes

### 4. Exception Management
- Visit "Exception Dashboard" for all exceptions
- Filter by date, type, or reason
- Resolve exceptions with bulk actions
- Export exception reports

### 5. Reports & Analytics
- Generate various reports from "Reports & Insights"
- Export data in CSV or Excel format
- Schedule automated reports (admin only)
- View performance analytics and trends

## 🔒 Security Features

- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Password hashing with bcrypt
- CORS protection
- Input validation and sanitization
- Audit logging for all actions
- Session management

## 🧪 Testing

### Backend Tests
```bash
pytest
```

### Frontend Tests
```bash
npm test
```

## 📈 Performance

- **Scalability**: Handles millions of transactions with proper indexing
- **Caching**: Redis caching for frequently accessed data
- **Background Processing**: Celery for heavy reconciliation tasks
- **Database Optimization**: Optimized queries and proper indexing
- **File Processing**: Efficient pandas-based data processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 API Documentation

The API is documented using OpenAPI/Swagger. Access the interactive documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 Deployment

### Production Setup

1. **Database**: Set up PostgreSQL with proper backup strategies
2. **Web Server**: Use Nginx as reverse proxy
3. **Process Manager**: Use systemd or supervisor for process management
4. **SSL**: Configure SSL certificates for HTTPS
5. **Monitoring**: Set up logging and monitoring (Prometheus, Grafana)

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 📚 Documentation

- [API Reference](docs/api-reference.md)
- [User Guide](docs/user-guide.md)
- [Admin Guide](docs/admin-guide.md)
- [Development Guide](docs/development.md)

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Ensure database exists

2. **File Upload Issues**
   - Check file format (CSV/Excel)
   - Verify column mappings
   - Check file size limits

3. **Reconciliation Failures**
   - Review matching criteria
   - Check data quality
   - Verify date formats

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent Python framework
- Material-UI for the beautiful React components
- Recharts for data visualization
- The open-source community for various libraries and tools

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: support@example.com
- Documentation: [Wiki](https://github.com/your-repo/wiki)

---

**Built with ❤️ for efficient financial reconciliation**