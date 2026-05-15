"""
Routes service main application
"""

import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routes import router as routes_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Logging setup
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting up routes service...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down routes service...")


# Create FastAPI app
app = FastAPI(
    title="Rápido-Entrega Routes Service",
    description="API de logística, rutas y seguimiento de repartidores",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "rutas",
        "version": "1.0.0",
    }


# Include routers
app.include_router(routes_router, prefix="/api/rutas", tags=["rutas"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "rutas",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
