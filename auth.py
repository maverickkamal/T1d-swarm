"""
Judge Authentication Module for T1D-Swarm
Add this to your existing FastAPI backend
"""

import os
import logging
from typing import Dict, Any
from fastapi import HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Pydantic models
class JudgeCodeRequest(BaseModel):
    code: str

class AuthResponse(BaseModel):
    valid: bool
    message: str = ""

# Configuration
JUDGE_CODES = os.getenv("JUDGE_CODES", "").split(",")
JUDGE_CODES = [code.strip() for code in JUDGE_CODES if code.strip()]

if not JUDGE_CODES:
    logger.warning("No JUDGE_CODES found in environment. Using default demo codes.")
    JUDGE_CODES = ["JUDGE2025", "T1D_ADMIN", "DEMO_JUDGE"]

logger.info(f"Judge authentication initialized with {len(JUDGE_CODES)} codes")

async def verify_judge_code_endpoint(request: JudgeCodeRequest, req: Request):
    """
    Verify if the provided code is a valid judge access code
    """
    client_ip = req.client.host if req else "unknown"
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