# FastAPI with PostgreSQL

A modern FastAPI application with PostgreSQL database integration, featuring user management and item tracking.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation using Python type annotations
- **Password Hashing**: Secure password storage with bcrypt
- **CORS Support**: Cross-origin resource sharing enabled
- **Auto-generated API Documentation**: Interactive docs at `/docs`

## Project Structure

```
fastapi/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings
├── database.py          # Database connection and session management
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas for request/response
├── crud.py              # CRUD operations
├── requirements.txt     # Python dependencies
├── alembic.ini         # Alembic configuration
├── alembic/            # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
└── README.md           # This file
```

## Prerequisites

- Python 3.8+
- PostgreSQL database
- pip (Python package manager)

## Installation

1. **Clone or navigate to the project directory**

   ```bash
   cd /path/to/fastapi
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL**

   Make sure PostgreSQL is running and create a database:

   ```sql
   CREATE DATABASE fastapi_db;
   CREATE USER postgres WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO postgres;
   ```

5. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/fastapi_db
   SECRET_KEY=your-secret-key-here-change-in-production
   DEBUG=True
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

## Running the Application

1. **Start the FastAPI server**

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the application**
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc
   - Health check: http://localhost:8000/health

## API Endpoints

### Users

- `POST /users/` - Create a new user
- `GET /users/` - Get all users (with pagination)
- `GET /users/{user_id}` - Get a specific user
- `PUT /users/{user_id}` - Update a user
- `DELETE /users/{user_id}` - Delete a user

### Items

- `POST /items/` - Create a new item
- `GET /items/` - Get all items (with pagination)
- `GET /items/{item_id}` - Get a specific item
- `PUT /items/{item_id}` - Update an item
- `DELETE /items/{item_id}` - Delete an item
- `GET /users/{user_id}/items/` - Get items owned by a specific user

## Example Usage

### Create a User

```bash
curl -X POST "http://localhost:8000/users/" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "username": "testuser",
       "full_name": "Test User",
       "password": "securepassword123"
     }'
```

### Create an Item

```bash
curl -X POST "http://localhost:8000/items/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "My First Item",
       "description": "This is a test item",
       "owner_id": 1
     }'
```

### Get All Users

```bash
curl "http://localhost:8000/users/"
```

## Database Migrations

### Create a new migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback migrations

```bash
alembic downgrade -1
```

## Development

### Code Structure

- **Models** (`models.py`): Define database tables and relationships
- **Schemas** (`schemas.py`): Define API request/response data structures
- **CRUD** (`crud.py`): Database operations and business logic
- **API Routes** (`main.py`): HTTP endpoints and request handling

### Adding New Features

1. Define models in `models.py`
2. Create schemas in `schemas.py`
3. Add CRUD operations in `crud.py`
4. Create API endpoints in `main.py`
5. Generate and run migrations with Alembic

## Security Features

- Password hashing with bcrypt
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy
- CORS configuration for web applications

## Production Deployment

For production deployment:

1. Change the `SECRET_KEY` in your environment variables
2. Set `DEBUG=False`
3. Use a production PostgreSQL instance
4. Configure proper CORS origins
5. Set up proper logging
6. Use a production ASGI server like Gunicorn with Uvicorn workers

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Verify database credentials in `.env`
- Check if the database exists

### Migration Issues

- Make sure all dependencies are installed
- Verify the database URL in `alembic.ini`
- Check if the database is accessible

### Import Errors

- Ensure you're in the correct virtual environment
- Verify all dependencies are installed
- Check Python path configuration

## License

This project is open source and available under the MIT License.
