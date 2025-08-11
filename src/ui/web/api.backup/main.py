# -*- coding: utf-8 -*-
"""
FastAPI Application Main Entry Point - WF EOL Tester Web API

This module sets up the FastAPI application with:
- Application configuration and initialization
- Route registration and middleware setup
- CORS configuration for web interface
- WebSocket endpoint setup
- Static file serving
- API documentation configuration
- Error handling and logging
- Database connection management
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import route modules
# from .routes import hardware, tests, configuration, websocket

app = FastAPI(
    title="WF EOL Tester Web API",
    description="REST API for WF EOL Tester web interface",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# Include API routes
# app.include_router(hardware.router, prefix="/api/v1/hardware", tags=["hardware"])
# app.include_router(tests.router, prefix="/api/v1/tests", tags=["tests"])
# app.include_router(configuration.router, prefix="/api/v1/config", tags=["configuration"])

@app.get("/")
async def root():
    """Root endpoint returning API information"""
    return {"message": "WF EOL Tester Web API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)