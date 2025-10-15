"""
FastAPI main application for the Offline Dictionary API.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database.connection import db_connection
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Offline Dictionary API",
    description="A personal dictionary API for managing custom word collections",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from routers import auth, dictionaries, words

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dictionaries.router, prefix="/api/dictionaries", tags=["Dictionaries"])
app.include_router(words.router, prefix="/api/words", tags=["Words"])

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Starting Offline Dictionary API...")
    
    # Check database connection
    if db_connection.is_connected():
        logger.info("✅ Database connected successfully")
    else:
        logger.error("❌ Database connection failed")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("Shutting down Offline Dictionary API...")
    db_connection.close()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Offline Dictionary API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "database_connected": db_connection.is_connected()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database_connected": db_connection.is_connected(),
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8099,
        reload=True,
        log_level="info"
    )
