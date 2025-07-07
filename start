#!/bin/bash

# FastAPI Application Startup Script

echo "🚀 Starting FastAPI Application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if PostgreSQL is running (basic check)
echo "🔍 Checking PostgreSQL connection..."
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://postgres:password@localhost:5432/fastapi_db')
    conn.close()
    print('✅ PostgreSQL connection successful')
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')
    print('Please make sure PostgreSQL is running and the database exists.')
    exit(1)
"

# Run database setup
echo "🗄️ Setting up database..."
python3 setup_db.py

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Start the application
echo "🌟 Starting FastAPI server..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔗 API Base URL: http://localhost:8000"
echo "💚 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000 
