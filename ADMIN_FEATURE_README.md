# Mejora: Perfil de Administrador

## Objetivo

Crear un perfil de administrador que permita monitorear la plataforma sin modificar el flujo actual de repartidores y usuarios.

## Alcance

El nuevo perfil de administrador debe incluir:

- Seguimiento general de entregas
- Lista de repartidores con datos de perfil y estado
- Lista de usuarios registrados
- Lista de pedidos con sus estados
- Historial diario de entregas
- Opción para descargar en PDF el recibo de cada entrega (placeholder)

## Entregables previstos

- `frontend/src/pages/Admin.jsx`
- `frontend/src/services/adminService.js`
- `services/authentication/app/routes_admin.py`
- `services/service1-rutas/app/routes_admin.py`
- `ADMIN_FEATURE_README.md`

## Paso a paso

1. Extender el servicio de autenticación para soportar el rol `admin`.
   - Añadir validación de rol en la creación de usuarios.
   - Crear endpoints de administración de usuarios en `services/authentication/app/routes_admin.py`.

2. Añadir endpoints de monitoreo en `service1-rutas`.
   - Listado de repartidores con datos de perfil.
   - Listado de pedidos / rutas con estado.
   - Historial diario de entregas.
   - Endpoint de descarga de recibo PDF por entrega.
   - Definir autorizaciones para que solo admin pueda acceder.

3. Construir la interfaz de administrador en frontend.
   - Página de administración `frontend/src/pages/Admin.jsx`.
   - Servicio de API para admin `frontend/src/services/adminService.js`.
   - Componentes de tabla y cards para seguimiento, repartidores, usuarios, pedidos e historial.

4. Documentar y validar el flujo.
   - Actualizar los endpoints en la documentación del API.
   - Añadir pruebas unitarias y/o de integración para los roles y endpoints admin.

## Comentarios de implementación

- Todos los archivos creados son placeholders y contienen TODOs.
- No se implementa lógica todavía.
- La estructura está pensada para separar:
  - autenticación/admin de usuarios
  - monitoreo de rutas/pedidos/repartidores
  - presentación frontend

## Criterios de aceptación

- El administrador puede revisar seguimiento, repartidores, usuarios, pedidos e historial.
- El backend dispone de puntos claros donde agregar las rutas admin.
- El frontend dispone de una página y servicio admin listos para desarrollar.
- Queda marcado el soporte futuro para descarga de recibos PDF.
