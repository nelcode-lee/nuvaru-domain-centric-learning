# Development Guide

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nuvaru_domain_centric_learning
   ```

2. **Run the setup script**
   ```bash
   ./scripts/setup.sh
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development Workflow

### Backend Development

1. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Run tests**
   ```bash
   pytest
   ```

4. **Code formatting**
   ```bash
   black .
   isort .
   flake8 .
   ```

### Frontend Development

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server**
   ```bash
   npm run dev
   ```

3. **Run tests**
   ```bash
   npm test
   ```

4. **Code formatting**
   ```bash
   npm run lint
   npm run format
   ```

## Architecture Overview

### Backend Architecture

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Core functionality (config, security, etc.)
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── utils/         # Utility functions
├── tests/             # Test files
└── requirements.txt   # Python dependencies
```

### Frontend Architecture

```
frontend/
├── src/
│   ├── components/    # React components
│   ├── pages/         # Next.js pages
│   ├── services/      # API services
│   └── utils/         # Utility functions
├── public/            # Static assets
└── package.json       # Node.js dependencies
```

## Database Management

### Using Neon DB

The platform is configured to use Neon DB as the primary database. Update the `NEON_DATABASE_URL` in your `.env` file:

```env
NEON_DATABASE_URL="postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb"
```

### Database Migrations

1. **Create a new migration**
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

2. **Apply migrations**
   ```bash
   alembic upgrade head
   ```

3. **Rollback migrations**
   ```bash
   alembic downgrade -1
   ```

## Security Considerations

### Authentication

- JWT tokens for API authentication
- Refresh token rotation
- Password hashing with bcrypt
- Rate limiting on API endpoints

### Data Privacy

- All data processing happens within the VPC
- No external API calls for sensitive data
- Air-gapped deployment option
- Compliance with HIPAA, SOX, GDPR

## Testing

### Backend Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Frontend Testing

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- --testPathPattern=auth.test.tsx
```

## Deployment

### Development Deployment

```bash
docker-compose up -d
```

### Production Deployment

1. **Build production images**
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

2. **Deploy to production**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Infrastructure as Code

The platform uses Terraform for infrastructure management:

```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

## Monitoring and Logging

### Logging

- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Sensitive data filtering
- Request/response logging

### Monitoring

- Health check endpoints
- Prometheus metrics
- Performance monitoring
- Error tracking with Sentry

## Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Run tests and linting**
5. **Commit your changes**
   ```bash
   git commit -m "Add your feature"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a pull request**

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check database URL in `.env`
   - Ensure database is running
   - Verify network connectivity

2. **Docker issues**
   - Check Docker daemon is running
   - Verify Docker Compose version
   - Check port conflicts

3. **Authentication errors**
   - Verify JWT secret key
   - Check token expiration
   - Validate user permissions

### Getting Help

- Check the logs: `docker-compose logs -f [service_name]`
- Review the API documentation: http://localhost:8000/docs
- Check the troubleshooting section in the main README



