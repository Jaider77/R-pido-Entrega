# 🛠️ Development Setup Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Git
- Virtual environment (venv or conda)

## Backend Setup

### Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -e .

# Install pre-commit hooks
pre-commit install
```

### Database Initialization

```bash
# Run migrations (for each service)
cd services/authentication
alembic upgrade head

cd ../service1-rutas
alembic upgrade head

# ... repeat for other services
```

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=services --cov-report=html

# Run specific service tests
pytest services/authentication/ -v

# Run with parallel execution
pytest -n auto
```

### Code Quality Checks

```bash
# Format code
black services/ --line-length=100

# Lint
ruff check services/ --fix

# Type checking
mypy services/ --ignore-missing-imports

# Security scan
bandit -r services/ -ll

# All checks (pre-commit)
pre-commit run --all-files
```

## Frontend Setup

### Install Dependencies

```bash
cd frontend

# Install npm packages
npm install

# Or with yarn
yarn install
```

### Development Server

```bash
# Start Vite dev server
npm run dev

# Server runs on http://localhost:5173
```

### Building for Production

```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview
```

### Frontend Testing

```bash
# Run tests
npm run test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

## Microservices Development

### Starting Individual Service

```bash
cd services/authentication

# Install deps (if not using docker)
pip install -r requirements.txt

# Run with hot-reload
uvicorn app.main:app --reload --port 8001

# With environment file
uvicorn app.main:app --reload --port 8001 --env-file .env
```

### Local API Testing

```bash
# Test auth endpoint
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# Login
curl -X POST http://localhost:8001/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'
```

## Git Workflow

### Pre-commit Checks

Every commit runs:

- Black formatter
- Ruff linter
- MyPy type checker
- Bandit security
- Trailing whitespace checks
- JSON/YAML validation

If checks fail, fix and try again:

```bash
git add .
git commit -m "Fix: address linting issues"
```

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/new-feature

# Create Pull Request on GitHub
```

## Environment Configuration

### Backend (.env)

```bash
cp .env.example .env

# Edit with your values
PYTHONUNBUFFERED=1
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key
LOG_LEVEL=INFO
```

### Frontend (.env)

```bash
cd frontend
cp .env.example .env

# Edit with your values
VITE_API_URL=http://localhost/api
VITE_ENV=development
```

## Debugging

### Python Debugging

```python
# Add breakpoint in code
breakpoint()

# Or use pdb
import pdb; pdb.set_trace()
```

### Frontend Debugging

```javascript
// Chrome DevTools
console.log('Debug info:', variable)
debugger  // Sets breakpoint

// React DevTools browser extension recommended
```

### Docker Debugging

```bash
# Access container shell
docker exec -it auth-service sh

# View real-time logs
docker logs -f auth-service

# Inspect network
docker network inspect rapido-network
```

## Performance Monitoring

### Python Performance

```bash
# Profile code
python -m cProfile -s cumtime app.py

# Memory profiling
pip install memory-profiler
python -m memory_profiler app.py
```

### Database Performance

```bash
# PostgreSQL query analysis
EXPLAIN ANALYZE SELECT * FROM users;
```

## Troubleshooting Common Issues

### Port Already in Use

```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

### Module Not Found

```bash
# Ensure virtual environment activated
which python  # Should show venv path

# Reinstall dependencies
pip install -e .
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps | grep db

# Test connection
psql -h localhost -U auth_user -d auth_db
```

### Pre-commit Hooks Not Running

```bash
# Reinstall hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## VS Code Extensions (Recommended)

- Python (Microsoft)
- Pylance (Microsoft)
- Ruff (charliermarsh)
- Black Formatter (Microsoft)
- ES7+ React/Redux/React-Native snippets
- Thunder Client (API testing)
- Docker (Microsoft)
- PostgreSQL (Chris Kolkman)

## Useful Commands Cheatsheet

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -e .
pre-commit install
cd frontend && npm install

# Development
docker-compose up -d
uvicorn app.main:app --reload --port 8001
npm run dev  # in frontend dir

# Testing
pytest --cov=services
npm run test

# Code Quality
black services/ && ruff check services/
mypy services/
bandit -r services/ -ll

# Git
git checkout -b feature/name
git commit -m "feat: description"
git push origin feature/name
```

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Docs](https://docs.docker.com/)
- [GitHub Actions](https://docs.github.com/actions)
