#!/usr/bin/env python3
"""
T1D-Swarm Judge Authentication Backend

Simple FastAPI server to handle judge access code verification.
This allows controlled access to the T1D management system.

Usage:
    pip install fastapi uvicorn python-dotenv
    python judge-auth-backend.py

Environment Variables:
    JUDGE_CODES - Comma-separated list of valid judge codes
    PORT - Port to run server on (default: 8001)
"""

import os
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="T1D-Swarm Judge Authentication",
    description="Authentication service for T1D management system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JudgeCodeRequest(BaseModel):
    code: str

class AuthResponse(BaseModel):
    valid: bool
    message: str = ""

# Get judge codes from environment variable
JUDGE_CODES = os.getenv("JUDGE_CODES", "").split(",")
JUDGE_CODES = [code.strip() for code in JUDGE_CODES if code.strip()]

if not JUDGE_CODES:
    logger.warning("No JUDGE_CODES found in environment. Using default demo codes.")
    JUDGE_CODES = ["JUDGE2025", "T1D_ADMIN", "DEMO_JUDGE"]

logger.info(f"Initialized with {len(JUDGE_CODES)} judge codes")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "T1D-Swarm Judge Authentication",
        "status": "running",
        "version": "1.0.0"
    }

@app.post("/api/verify-judge", response_model=AuthResponse)
async def verify_judge_code(request: JudgeCodeRequest, req: Request):
    """
    Verify if the provided code is a valid judge access code
    
    Args:
        request: Request containing the judge code to verify
        
    Returns:
        AuthResponse indicating if the code is valid
        
    Raises:
        HTTPException: If the code is invalid (401)
    """
    client_ip = req.client.host
    logger.info(f"Judge code verification attempt from {client_ip}")
    
    if not request.code:
        logger.warning(f"Empty code submission from {client_ip}")
        raise HTTPException(
            status_code=400,
            detail="Judge code cannot be empty"
        )
    
    if request.code in JUDGE_CODES:
        logger.info(f"Valid judge code used from {client_ip}")
        return AuthResponse(
            valid=True,
            message="Judge access granted"
        )
    else:
        logger.warning(f"Invalid judge code attempt from {client_ip}: {request.code}")
        raise HTTPException(
            status_code=401,
            detail="Invalid judge code"
        )

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "judge_codes_configured": len(JUDGE_CODES) > 0,
        "active_codes": len(JUDGE_CODES)
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    
    print(f"""
    🔐 T1D-Swarm Judge Authentication Server
    =======================================
    
    Server starting on: http://localhost:{port}
    Health check: http://localhost:{port}/api/health
    
    Judge codes configured: {len(JUDGE_CODES)}
    
    Environment setup:
    - Set JUDGE_CODES environment variable with comma-separated codes
    - Set PORT to change server port (default: 8001)
    
    Example:
    export JUDGE_CODES="SECRET1,SECRET2,SECRET3"
    export PORT=8001
    
    """)
    
    uvicorn.run(
        "judge-auth-backend:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 