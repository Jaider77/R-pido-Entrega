# 🐳 Docker Setup Guide

## Quick Start

### Prerequisites

- Docker Desktop 20.10+
- Docker Compose 2.0+
- At least 4GB RAM allocated to Docker

### Starting Services

```bash
cd R-pido-Entrega

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services and Ports

| Service | Port | URL |
|---------|------|-----|
| API Gateway (Nginx) | 80 | <http://localhost> |
| Auth Service | 8001 | <http://localhost/api/auth> |
| Rutas Service | 8002 | <http://localhost/api/rutas> |
| Notificaciones | 8003 | <http://localhost/api/notificaciones> |
| Service3 | 8004 | <http://localhost/api/service3> |
| Frontend | 3000 | <http://localhost:3000> |
| Redis | 6379 | redis://localhost:6379 |
| RabbitMQ | 5672 | amqp://localhost:5672 |
| RabbitMQ Admin | 15672 | <http://localhost:15672> |
| PostgreSQL Auth | 5432 | postgresql://localhost/auth_db |
| PostgreSQL Rutas | 5433 | postgresql://localhost/rutas_db |
| PostgreSQL Notif | 5434 | postgresql://localhost/notificaciones_db |
| PostgreSQL Service3 | 5435 | postgresql://localhost/service3_db |

### Development Mode

For hot-reload and debugging:

```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

## Health Checks

All services include health checks:

```bash
# Check service status
docker-compose ps

# Verify specific service
curl http://localhost/api/auth/health
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # or any port

# Kill process
kill -9 <PID>
```

### Database Connection Issues

```bash
# Check database logs
docker-compose logs db-auth

# Recreate database
docker-compose down -v
docker-compose up db-auth
```

### Redis Connection Issues

```bash
# Check Redis
docker exec -it redis redis-cli ping

# Clear all data
docker exec -it redis redis-cli FLUSHALL
```

## Database Access

### Using psql

```bash
# Connect to auth database
psql -h localhost -U auth_user -d auth_db

# Password: auth_password
```

### Using DBeaver/DataGrip

- Host: localhost
- Port: 5432 (auth), 5433 (rutas), 5434 (notif), 5435 (service3)
- Database: auth_db, rutas_db, notificaciones_db, service3_db
- User: auth_user, rutas_user, notificaciones_user, service3_user
- Password: check docker-compose.yml

## Production Deployment

For production environments:

1. Update environment variables in `.env`
2. Use only `docker-compose.yml` (not override)
3. Configure proper volumes for data persistence
4. Set resource limits in compose file
5. Use environment-specific configuration

## Performance Tuning

```yaml
# In docker-compose.yml services section
resources:
  limits:
    cpus: '1'
    memory: 512M
  reservations:
    cpus: '0.5'
    memory: 256M
```

## Logs and Monitoring

```bash
# Stream all logs
docker-compose logs -f

# Stream specific service
docker-compose logs -f auth-service

# View last 100 lines
docker-compose logs --tail 100 auth-service

# Save logs to file
docker-compose logs > logs.txt
```
