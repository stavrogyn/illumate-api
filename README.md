# Therapy Management API

Современное FastAPI приложение с интеграцией PostgreSQL для управления терапевтической практикой, включая аутентификацию пользователей, управление клиентами и сессиями.

## Features

- **FastAPI**: Современный, быстрый веб-фреймворк для создания API
- **PostgreSQL**: Надежная реляционная база данных
- **SQLAlchemy**: SQL toolkit и ORM
- **Alembic**: Инструмент для миграций базы данных
- **Pydantic**: Валидация данных с использованием Python type annotations
- **Аутентификация**: JWT токены, хеширование паролей с bcrypt
- **Подтверждение Email**: Отправка писем для подтверждения регистрации
- **CORS Support**: Поддержка cross-origin resource sharing
- **Auto-generated API Documentation**: Интерактивная документация на `/docs`

## Project Structure

```
fastapi/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings
├── database.py          # Database connection and session management
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas for request/response
├── crud.py              # CRUD operations
├── auth_service.py      # Authentication and email services
├── requirements.txt     # Python dependencies
├── alembic.ini         # Alembic configuration
├── alembic/            # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── test_auth.py        # Authentication tests
├── env_example.txt     # Environment variables example
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

   Create a `.env` file in the project root (see `env_example.txt` for reference):

   ```env
   # Database
   DATABASE_URL=postgresql://postgres:password@localhost:5432/fastapi_db

   # Security
   SECRET_KEY=your-secret-key-change-in-production

   # Email settings (optional - for email verification)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   FROM_EMAIL=noreply@therapyapp.com
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

3. **Test authentication**
   ```bash
   python test_auth.py
   ```

## API Endpoints

### Authentication

- `POST /auth/register` - Регистрация нового пользователя
- `POST /auth/login` - Вход пользователя (возвращает http-only cookie)
- `GET /auth/verify` - Подтверждение email по токену
- `POST /auth/logout` - Выход пользователя
- `GET /auth/me` - Получение информации о текущем пользователе

### Tenants (Организации)

- `POST /tenants/` - Создание новой организации
- `GET /tenants/` - Получение списка организаций
- `GET /tenants/{tenant_id}` - Получение информации об организации

### Users (Пользователи)

- `POST /users/` - Создание нового пользователя (требует аутентификации)
- `GET /users/` - Получение списка пользователей организации
- `GET /users/{user_id}` - Получение информации о пользователе

### Clients (Клиенты)

- `POST /clients/` - Создание нового клиента
- `GET /clients/` - Получение списка клиентов организации
- `GET /clients/{client_id}` - Получение информации о клиенте
- `PATCH /clients/{client_id}` - Обновление информации о клиенте
- `DELETE /clients/{client_id}` - Удаление клиента

### Sessions (Сессии)

- `POST /sessions/` - Создание новой сессии
- `GET /sessions/` - Получение списка сессий клиента
- `GET /sessions/{session_id}` - Получение информации о сессии
- `PATCH /sessions/{session_id}` - Обновление информации о сессии
- `DELETE /sessions/{session_id}` - Удаление сессии

## Example Usage

### Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "therapist@example.com",
       "password": "securepassword123",
       "tenant_name": "Моя Терапевтическая Практика",
       "role": "therapist",
       "locale": "ru"
     }'
```

### Вход пользователя

```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "therapist@example.com",
       "password": "securepassword123"
     }'
```

### Подтверждение email

```bash
curl "http://localhost:8000/auth/verify?token=YOUR_VERIFICATION_TOKEN"
```

### Получение информации о текущем пользователе

```bash
curl -X GET "http://localhost:8000/auth/me" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Создание клиента

```bash
curl -X POST "http://localhost:8000/clients/" \
     -H "Content-Type: application/json" \
     -d '{
       "full_name": "Иван Иванов",
       "birthday": "1990-01-01T00:00:00",
       "tags": ["новый", "депрессия"]
     }'
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
