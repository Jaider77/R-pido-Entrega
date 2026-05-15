# 📘 API Documentation

## Overview

Rápido-Entrega is a microservices-based logistics platform with the following services:

- **Authentication Service** (Port 8001): User management and JWT token generation
- **Rutas Service** (Port 8002): Delivery routing and repartidor tracking
- **Notificaciones Service** (Port 8003): Multi-channel notifications
- **Service3** (Port 8004): Generic items and activities management

## Base URL

```
http://localhost/api
```

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require a JWT token in the Authorization header:

```bash
Authorization: Bearer <token>
```

## Common Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |

---

## Authentication Service (`/api/auth`)

### Register User

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

**Response (201):**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "created_at": "2026-05-14T10:00:00Z"
}
```

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user"
  }
}
```

### Get Current User

```http
GET /api/auth/me
Authorization: Bearer <token>
```

**Response (200):**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "created_at": "2026-05-14T10:00:00Z"
}
```

### Change Password

```http
PUT /api/auth/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "old_pass",
  "new_password": "new_secure_pass"
}
```

### Verify Token

```http
POST /api/auth/verify-token
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Health Check

```http
GET /api/auth/health
```

---

## Rutas Service (`/api/rutas`)

### Create Repartidor

```http
POST /api/rutas/repartidores
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "uuid",
  "vehicle_type": "moto",
  "coordinates": {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

### List Repartidores

```http
GET /api/rutas/repartidores
Authorization: Bearer <token>
```

### Get Repartidor

```http
GET /api/rutas/repartidores/{id}
Authorization: Bearer <token>
```

### Create Ruta

```http
POST /api/rutas/rutas
Authorization: Bearer <token>
Content-Type: application/json

{
  "repartidor_id": "uuid",
  "origin_coordinates": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "destination_coordinates": {
    "latitude": 40.7580,
    "longitude": -73.9855
  }
}
```

### Update Location

```http
POST /api/rutas/rutas/{ruta_id}/location
Authorization: Bearer <token>
Content-Type: application/json

{
  "latitude": 40.7200,
  "longitude": -74.0100,
  "accuracy": 10
}
```

### Get Repartidor Stats

```http
GET /api/rutas/stats/repartidor/{repartidor_id}
Authorization: Bearer <token>
```

**Response:**

```json
{
  "total_rutas": 45,
  "delivered_rutas": 42,
  "in_transit_rutas": 3,
  "success_rate": 0.9333
}
```

---

## Notificaciones Service (`/api/notificaciones`)

### Create Notification

```http
POST /api/notificaciones
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "uuid",
  "type": "EMAIL",
  "title": "Entrega Completada",
  "message": "Tu entrega ha sido completada",
  "recipient": "user@example.com"
}
```

**Notification Types:** EMAIL, SMS, PUSH, IN_APP

### Get User Notifications

```http
GET /api/notificaciones/user/{user_id}
Authorization: Bearer <token>
```

### Create Notification Template

```http
POST /api/notificaciones/templates
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "delivery_complete",
  "title_template": "¡Entrega #{order_id} Completada!",
  "message_template": "Tu paquete ha llegado a {location} a las {time}"
}
```

### Send Bulk Notifications

```http
POST /api/notificaciones/send/bulk
Authorization: Bearer <token>
Content-Type: application/json

{
  "template_id": "uuid",
  "user_ids": ["uuid1", "uuid2", "uuid3"],
  "variables": {
    "order_id": "12345",
    "location": "Centro",
    "time": "14:30"
  }
}
```

### Get User Stats

```http
GET /api/notificaciones/stats/user/{user_id}
Authorization: Bearer <token>
```

**Response:**

```json
{
  "total_notifications": 150,
  "unread_notifications": 5,
  "sent_notifications": 145,
  "failed_notifications": 0
}
```

---

## Service3 (`/api/service3`)

### Create Item

```http
POST /api/service3/items?owner_id=uuid
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Package A",
  "description": "Important shipment",
  "status": "active"
}
```

### List Items

```http
GET /api/service3/items?owner_id=uuid
Authorization: Bearer <token>
```

### Get Item

```http
GET /api/service3/items/{id}
Authorization: Bearer <token>
```

### Update Item

```http
PUT /api/service3/items/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Package A Updated",
  "description": "Updated description",
  "status": "completed"
}
```

### Delete Item

```http
DELETE /api/service3/items/{id}
Authorization: Bearer <token>
```

### Log Activity

```http
POST /api/service3/activities?user_id=uuid
Authorization: Bearer <token>
Content-Type: application/json

{
  "item_id": "uuid",
  "action": "updated",
  "details": "Status changed from active to completed"
}
```

### Get Owner Stats

```http
GET /api/service3/stats/owner/{owner_id}
Authorization: Bearer <token>
```

**Response:**

```json
{
  "total_items": 50,
  "active_items": 30,
  "completed_items": 20
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message",
  "status": 400,
  "timestamp": "2026-05-14T10:00:00Z"
}
```

## Rate Limiting

- Unauthenticated: 10 requests/minute
- Authenticated: 100 requests/minute
- Admin: Unlimited

Headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1620000000
```

## Testing with cURL

```bash
# Register
curl -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"pass123","full_name":"Test User"}'

# Login
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"pass123"}'

# Use token
curl -X GET http://localhost/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Testing with Postman

1. Import the API collection
2. Set `{{base_url}}` to `http://localhost/api`
3. After login, copy the token to `{{token}}`
4. Use `Bearer {{token}}` in Authorization header

## API Monitoring

Access monitoring dashboard:

- Prometheus: <http://localhost:9090> (if enabled)
- Grafana: <http://localhost:3001> (if enabled)

## Support

For API issues:

- Check logs: `docker-compose logs auth-service`
- Review database: `docker-compose exec db-auth psql`
- Test connectivity: `curl http://localhost/api/auth/health`
