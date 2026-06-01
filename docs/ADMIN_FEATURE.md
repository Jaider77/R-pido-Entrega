# 👨‍💼 Panel de Administrador

## Objetivo

Crear un perfil de administrador que permita monitorear la plataforma sin modificar el flujo actual de repartidores y usuarios.

## Alcance

El panel de administrador incluye:

- Seguimiento general de entregas y métricas
- Lista de repartidores con datos de perfil y estado
- Lista de usuarios registrados
- Lista de pedidos/rutas con estados
- Historial diario de entregas
- Descarga de reportes en PDF

## Arquitectura

### Backend

#### Servicio de Autenticación (`services/authentication/app/routes_admin.py`)

- Validación de rol `admin` en la creación de usuarios
- Endpoints privados para gestión de administradores
- Listado y búsqueda de usuarios por rol

#### Servicio de Rutas (`services/service1-rutas/app/routes_admin.py`)

- Listado de repartidores con datos de perfil
- Listado de rutas/pedidos con filtros por estado
- Historial diario de entregas
- Estadísticas y métricas de desempeño

### Frontend

#### Página de Administración (`frontend/src/pages/Admin.jsx`)

- Panel principal con KPIs
- Tablas de repartidores, usuarios y rutas
- Filtros y búsqueda avanzada

#### Servicio API (`frontend/src/services/adminService.js`)

- Integración con endpoints de admin
- Funciones para obtener métricas y listados

## Rutas y Endpoints

### Autenticación (Admin)

```http
GET /api/auth/admin/users
GET /api/auth/admin/users/{user_id}
GET /api/auth/admin/repartidores
```

### Rutas (Admin)

```http
GET /api/rutas/admin/dashboard
GET /api/rutas/admin/repartidores
GET /api/rutas/admin/rutas
GET /api/rutas/admin/historial
GET /api/rutas/admin/rutas/{ruta_id}/pdf
```

## Seguridad

- Solo usuarios con rol `admin` pueden acceder a estos endpoints
- Validación de JWT en todas las peticiones
- Los datos sensibles están enmascarados

## Próximos Pasos

- [ ] Implementar endpoints de admin en autenticación
- [ ] Implementar endpoints de admin en rutas
- [ ] Construir componentes de administración en frontend
- [ ] Agregar pruebas unitarias para roles admin
- [ ] Documentar API completo

---

Para más información, ver [README.MD](../README.MD)
