# README2.md — Guía rápida de la aplicación web

Este documento explica las funcionalidades principales de la web y cómo agregar datos en cada sección.

## 🧭 Funcionalidades principales

### 1. Autenticación

- Registro de nuevos usuarios.
- Login con email y contraseña.
- Cierre de sesión funcional.
- Rutas privadas accesibles solo cuando el usuario está autenticado.

### 2. Dashboard

- Muestra métricas generales del usuario:
  - total de rutas
  - entregas completadas
  - rutas en tránsito
  - rutas pendientes
  - ratio de éxito
  - notificaciones totales
  - notificaciones sin leer
  - notificaciones fallidas

### 3. Rutas

- Crear nuevas rutas desde la interfaz.
- Consultar el listado de rutas existentes.
- Ver detalles como origen, destino, repartidor y estado.
- Recargar el listado manualmente.

### 4. Notificaciones

- Enviar notificaciones desde el formulario.
- Ver el historial de notificaciones del usuario.
- Filtrar por tipo y estado de lectura.
- Buscar notificaciones por título o mensaje.
- Marcar notificaciones como leídas.

### 5. Perfil

- Ver datos básicos del usuario autenticado.
- Navegar desde el menú a la información del perfil.

## 📝 Cómo usar cada sección

### Registro / Login

1. Abre la aplicación en el navegador.
2. Haz clic en **Crear cuenta** para registrar un usuario.
3. Completa `Nombre completo`, `Email` y `Password`.
4. La contraseña debe tener al menos 8 caracteres.
5. Al registrarte, la aplicación iniciará sesión automáticamente y te llevará al **Dashboard**.

### Dashboard

1. Al ingresar correctamente, el sistema muestra el dashboard.
2. Este panel ofrece un resumen inmediato del estado de rutas y notificaciones.
3. Si necesitas más detalle, usa los menús de **Rutas** o **Notificaciones**.

### Agregar una nueva ruta

1. Ingresa a la sección **Rutas** desde la barra lateral.
2. Completa los campos del formulario de creación.
3. Presiona **Crear ruta**.
4. La ruta se registra y aparece en la tabla de rutas.

> Nota: Los endpoints del backend reciben datos JSON para crear rutas. Asegúrate de tener sesiones activas y acceso al servicio `rutas`.

### Agregar datos en Notificaciones

1. Ve a la sección **Notificaciones**.
2. Completa el formulario de envío con título, mensaje y tipo.
3. Haz clic en **Enviar notificación**.
4. La notificación se muestra en el historial.

### Filtrar y buscar notificaciones

1. En la página de **Notificaciones**, usa los filtros por `tipo` y `estado`.
2. Escribe texto en el campo de búsqueda para encontrar coincidencias en título o mensaje.
3. La lista se actualizará según los filtros aplicados.

### Panel de usuario / Perfil

1. Haz clic en el enlace de **Perfil**.
2. Verás tu información de usuario y estado de sesión.
3. Usa el botón de **Cerrar sesión** en la cabecera para salir.

## 🔧 Qué se puede agregar manualmente desde el backend

Si deseas agregar datos directamente al backend o por API, estos son los principales endpoints:

- Registro de usuario: `POST /api/auth/register`
- Login: `POST /api/auth/login`
- Crear ruta: `POST /api/rutas/rutas`
- Listar rutas: `GET /api/rutas/rutas`
- Crear notificación: `POST /api/notificaciones/`
- Listar notificaciones por usuario: `GET /api/notificaciones/user/{user_id}`

## 📌 Consejos rápidos

- Usa un email válido para registrar usuarios.
- Asegúrate de no repetir emails al registrar una nueva cuenta.
- Si recibes un error 422, revisa que la contraseña tenga al menos 8 caracteres y que los campos requeridos no estén vacíos.
- Para trabajar con datos de rutas y notificaciones, primero inicia sesión.

---

## 🚀 Resumen de la experiencia de usuario

1. Registro → Inicio de sesión automática → Dashboard.
2. Dashboard → Navegación a **Rutas** para crear y consultar rutas.
3. Dashboard → Navegación a **Notificaciones** para enviar y gestionar mensajes.
4. Perfil → Ver datos propios y cerrar sesión.

Este README2.md es un manual rápido para usar y probar la plataforma web.
