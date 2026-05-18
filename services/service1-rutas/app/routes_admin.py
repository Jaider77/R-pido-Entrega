"""
Admin routes for the rutas service.

TODO:
- agregar endpoints de monitoreo de repartidores, pedidos y entregas
- incluir descarga de recibo PDF por pedido
- restringir acceso a administradores
"""

from fastapi import APIRouter

router = APIRouter()

# TODO: implement routes for admin monitoring
# - GET /admin/repartidores
# - GET /admin/pedidos
# - GET /admin/pedidos/{pedido_id}/recibo/pdf
# - GET /admin/historial-diario
# - GET /admin/seguimiento
# - posibles filtros por fecha, estado y repartidor
