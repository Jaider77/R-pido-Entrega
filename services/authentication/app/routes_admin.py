"""
Admin routes for the authentication service.

TODO:
- agregar endpoints de administración de usuarios
- definir acceso exclusivo para rol admin
- listar usuarios, ver detalle y actualizar permisos
"""

from fastapi import APIRouter

router = APIRouter()

# TODO: implement routes for admin user management
# - GET /admin/users
# - GET /admin/users/{user_id}
# - PATCH /admin/users/{user_id}
# - POST /admin/users/{user_id}/roles
# - validar que el token corresponda a un admin
