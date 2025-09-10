# User Service API

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-000000?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)

**A robust FastAPI-based user management service with comprehensive authentication, authorization, and user profile management capabilities.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge)](https://www.python.org/downloads/)

</div>

---

## 🚀 Features

### Authentication & Authorization
- **JWT-based authentication** with access and refresh tokens
- **Token blacklisting** for secure logout
- **Flexible login** using email or phone number
- **Role-based access control** (User, Group Admin)
- **Token validation** and refresh mechanisms

### User Management
- **User registration** with comprehensive validation
- **Profile management** with partial updates
- **Secure password hashing** using bcrypt
- **Unique constraints** on email and phone number
- **User roles** and permissions

### Security Features
- **Input validation** with regex patterns
- **SQL injection protection** via SQLAlchemy ORM
- **Password security** with bcrypt hashing
- **Token expiration** and refresh mechanisms
- **Database connection** error handling

## 🏗️ Architecture

<div align="center">

![Project Architecture](images/architecture.png)

*Project structure and data flow diagram*

</div>

```
user_service/
├── app/
│   ├── api/v1/routes/          # API endpoints
│   │   ├── auth.py            # Authentication routes
│   │   └── users.py           # User management routes
│   ├── core/                  # Core configuration
│   │   └── config.py          # App configuration
│   ├── db/                    # Database layer
│   │   ├── database.py        # Database connection & session
│   │   └── migrations/        # Database migrations
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py           # User model
│   │   ├── blacklisted_token.py
│   │   └── otp_code.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── auth_schema.py    # Auth request/response models
│   │   └── user_schema.py    # User request/response models
│   ├── services/              # Business logic
│   │   ├── auth/             # Authentication services
│   │   └── user_service.py   # User business logic
│   ├── utils/                 # Utility functions
│   │   ├── email_sender.py   # Email functionality
│   │   └── validators.py     # Input validation
│   ├── tests/                 # Test files
│   └── main.py               # FastAPI application entry point
└── requirements.txt          # Python dependencies
```

## 🛠️ Technology Stack

<div align="center">

![Tech Stack](images/tech-stack.png)

</div>

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Lightweight database (configurable)
- **Pydantic** - Data validation using Python type annotations
- **PyJWT** - JSON Web Token implementation
- **Passlib** - Password hashing library
- **bcrypt** - Password hashing algorithm
- **Uvicorn** - ASGI server

## 📋 Prerequisites

- Python 3.8+
- pip (Python package installer)

## 🚀 Installation & Setup

<div align="center">

![Installation Steps](images/installation.png)

</div>

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd user_service
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📚 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/check` | Check if user exists with email or phone number |
| `POST` | `/auth/login` | User login with email/phone identifier and password |
| `POST` | `/auth/signup` | User registration with email or phone identifier |
| `POST` | `/auth/refresh` | Refresh access token using refresh token |
| `POST` | `/auth/logout` | Logout and blacklist current token |
| `POST` | `/auth/check-user` | Validate current access token |

### User Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/` | Create new user account |
| `GET` | `/users/profile` | Get current user profile |
| `PATCH` | `/users/profile` | Update user profile |

## 🔐 Authentication Flow

<div align="center">

![Authentication Flow](images/auth-flow.png)

*JWT Authentication and Token Management Flow*

</div>

1. **Registration**: User creates account with email/phone, password, and role
2. **Login**: User authenticates with email/phone and password
3. **Token Issuance**: System returns access token (15 min) and refresh token (7 days)
4. **API Access**: Include access token in Authorization header
5. **Token Refresh**: Use refresh token to get new access token
6. **Logout**: Blacklist current token for security

## 📊 Data Models

### User Model
```python
{
    "id": "uuid",
    "name": "string (2-100 chars)",
    "phone_number": "string (10-15 digits)",
    "email": "valid email format",
    "password_hash": "bcrypt hash",
    "avatar_url": "optional URL",
    "card_number": "optional 16 digits",
    "card_holder_name": "optional string",
    "role": "user | group_admin",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### Token Response
```python
{
    "access_token": "JWT token (15 min expiry)",
    "refresh_token": "JWT token (7 days expiry)"
}
```

## 🔒 Security Features

<div align="center">

![Security Features](images/security.png)

*Security Implementation Overview*

</div>

### Input Validation
- **Name**: 2-100 characters, letters and spaces only
- **Phone**: 10-15 digits, optional + prefix
- **Email**: Standard email format validation
- **Card Number**: 16 digits for payment cards
- **Avatar URL**: Valid HTTP/HTTPS URL format

### Password Security
- **Hashing**: bcrypt with salt
- **Verification**: Secure comparison against stored hash

### Token Security
- **Access Token**: 15-minute expiry for API access
- **Refresh Token**: 7-day expiry for token renewal
- **Blacklisting**: Secure logout by token invalidation
- **Validation**: JWT signature verification

## 🧪 Testing

The project includes test files for both authentication and user management:

```bash
# Run tests (when implemented)
pytest app/tests/
```

## 🔧 Configuration

### Environment Variables
The application uses SQLite by default. For production, consider:

- Database URL configuration
- JWT secret keys
- CORS settings
- Rate limiting configuration

### Database
- **Default**: SQLite with file-based storage
- **Production**: PostgreSQL/MySQL recommended
- **Migrations**: Alembic support included

## 📝 API Examples

### User Registration
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone_number": "+1234567890",
    "email": "john@example.com",
    "password": "securepassword123",
    "role": "user"
  }'
```

### User Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "john@example.com",
    "password": "securepassword123"
  }'
```

### Get User Profile
```bash
curl -X GET "http://localhost:8000/users/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Update User Profile
```bash
curl -X PATCH "http://localhost:8000/users/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "avatar_url": "https://example.com/avatar.jpg"
  }'
```

## 🚀 Deployment

### Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🤝 Contributing

<div align="center">

![Contributing](images/contributing.png)

</div>

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test files for usage examples

## 🔄 Future Enhancements

- [ ] Email verification system
- [ ] Password reset functionality
- [ ] Rate limiting implementation
- [ ] OAuth integration
- [ ] Multi-factor authentication
- [ ] User activity logging
- [ ] Advanced role-based permissions
- [ ] API versioning strategy

---

<div align="center">

**Made with ❤️ using FastAPI**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/user_service?style=social)](https://github.com/yourusername/user_service)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/user_service?style=social)](https://github.com/yourusername/user_service)

</div>
