"""
Admin routes for the rutas service.
"""

import io
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.database import get_db
from app.models import Repartidor, Ruta
from app.routes import verify_auth_token
from app.schemas import RepartidorResponse, RutaResponse
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

router = APIRouter()


def require_admin(auth: dict = Depends(verify_auth_token)) -> dict:
    if auth.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return auth


@router.get("/admin/repartidores", response_model=list[RepartidorResponse])
async def admin_list_repartidores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth: dict = Depends(require_admin),
):
    return db.query(Repartidor).offset(skip).limit(limit).all()


@router.get("/admin/pedidos", response_model=list[RutaResponse])
async def admin_list_pedidos(
    repartidor_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth: dict = Depends(require_admin),
):
    query = db.query(Ruta)
    if repartidor_id is not None:
        query = query.filter(Ruta.repartidor_id == repartidor_id)
    if status is not None:
        query = query.filter(Ruta.status == status)
    return query.offset(skip).limit(limit).all()


@router.get("/admin/historial-diario", response_model=list[RutaResponse])
async def admin_daily_history(
    date: Optional[str] = None,
    db: Session = Depends(get_db),
    auth: dict = Depends(require_admin),
):
    if date:
        try:
            day_start = datetime.fromisoformat(date).replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format, use YYYY-MM-DD",
            )
    else:
        now = datetime.now(timezone.utc)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    day_end = day_start + timedelta(days=1)

    routes = (
        db.query(Ruta).filter(Ruta.completed_at >= day_start, Ruta.completed_at < day_end).all()
    )
    return routes


@router.get("/admin/seguimiento")
async def admin_overview(
    db: Session = Depends(get_db),
    auth: dict = Depends(require_admin),
):
    total_rutas = db.query(Ruta).count()
    pending = db.query(Ruta).filter(Ruta.status == "pending").count()
    assigned = db.query(Ruta).filter(Ruta.status == "assigned").count()
    in_transit = db.query(Ruta).filter(Ruta.status == "in_transit").count()
    delivered = db.query(Ruta).filter(Ruta.status == "delivered").count()
    repartidores = db.query(Repartidor).count()
    active_repartidores = db.query(Repartidor).filter(Repartidor.is_active.is_(True)).count()

    return {
        "total_rutas": total_rutas,
        "pending": pending,
        "assigned": assigned,
        "in_transit": in_transit,
        "delivered": delivered,
        "total_repartidores": repartidores,
        "active_repartidores": active_repartidores,
    }


@router.get("/admin/pedidos/{pedido_id}/recibo/pdf")
async def admin_download_receipt(
    pedido_id: int,
    db: Session = Depends(get_db),
    auth: dict = Depends(require_admin),
):
    ruta = db.query(Ruta).filter(Ruta.id == pedido_id).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido not found",
        )

    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj<< /Length 56 >>\nstream\nBT /F1 24 Tf 72 100 Td (Recibo de entrega) Tj ET\nendstream\nendobj\n"
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000110 00000 n \n0000000230 00000 n \n0000000340 00000 n \ntrailer<< /Size 6 /Root 1 0 R >>\nstartxref\n400\n%%EOF\n"
    )
    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=pedido_{pedido_id}_recibo.pdf"},
    )
