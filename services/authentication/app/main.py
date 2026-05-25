"""
Authentication Microservice
Gestión de usuarios, autenticación y tokens JWT
"""

import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routes import router as auth_router
from app.routes_admin import router as auth_admin_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Logging setup
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting up authentication service...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down authentication service...")


# Create FastAPI app
app = FastAPI(
    title="Rápido-Entrega Authentication Service",
    description="API de autenticación y gestión de usuarios",
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
        "service": "authentication",
        "version": "1.0.0",
    }


# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(auth_admin_router, prefix="/api/auth", tags=["admin"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "authentication",
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
