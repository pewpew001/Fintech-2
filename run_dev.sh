#!/bin/bash

# POS Reconciliation Dashboard - Development Startup Script

echo "🚀 Starting POS Reconciliation Dashboard Development Environment"

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Check if PostgreSQL is running
echo "🗄️  Checking PostgreSQL connection..."
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
    echo "   On macOS: brew services start postgresql"
    echo "   On Ubuntu: sudo service postgresql start"
    exit 1
fi

# Create database if it doesn't exist
echo "🗄️  Setting up database..."
createdb pos_reconciliation 2>/dev/null || echo "Database already exists"

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head 2>/dev/null || echo "Migration files need to be created"

# Create admin user
echo "👤 Creating admin user..."
python scripts/create_admin.py

# Start backend server in background
echo "🔧 Starting backend server..."
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if Node.js dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Start frontend server
echo "🎨 Starting frontend server..."
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Development environment started successfully!"
echo ""
echo "🔗 Application URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "👤 Default login credentials:"
echo "   Admin: admin / admin123"
echo "   Analyst: analyst / analyst123"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Wait for user input to keep script running
wait