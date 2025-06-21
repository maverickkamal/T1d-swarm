"""
Judge Authentication Module for T1D-Swarm
Persistent session-based rate limiting with SQLite storage
"""

import os
import logging
import sqlite3
import hashlib
import time
from typing import Optional, Tuple
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
    sessions_remaining: Optional[int] = None
    is_judge: bool = False

# Configuration
judge_codes_raw = os.getenv("JUDGE_CODES", "")
# Handle both comma-separated and space-separated formats
if "," in judge_codes_raw:
    JUDGE_CODES = [code.strip() for code in judge_codes_raw.split(",") if code.strip()]
else:
    JUDGE_CODES = [code.strip() for code in judge_codes_raw.split() if code.strip()]

if not JUDGE_CODES:
    logger.warning("No JUDGE_CODES found in environment. Using default demo codes.")
    JUDGE_CODES = ["JUDGE2025", "T1D_ADMIN", "DEMO_JUDGE"]

logger.info(f"Judge authentication initialized with {len(JUDGE_CODES)} codes")

# Session limits
MAX_FREE_SESSIONS = 3  # Total sessions allowed for free users
AUTH_DB_PATH = "auth_sessions.db"

def init_auth_database():
    """Initialize the SQLite database for session tracking"""
    conn = sqlite3.connect(AUTH_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            device_id TEXT PRIMARY KEY,
            sessions_used INTEGER DEFAULT 0,
            is_judge INTEGER DEFAULT 0,
            first_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Auth database initialized")

def get_device_fingerprint(request: Request) -> str:
    """
    Create a device fingerprint from request headers and IP
    This persists across browser sessions but resets if user changes browser/device
    """
    # Get real client IP (works with Cloud Run)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    # Create fingerprint from IP + User-Agent + Accept-Language
    user_agent = request.headers.get("User-Agent", "")
    accept_language = request.headers.get("Accept-Language", "")
    
    fingerprint_data = f"{client_ip}_{user_agent}_{accept_language}"
    device_id = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
    
    return device_id

def get_user_session_info(device_id: str) -> Tuple[int, bool]:
    """
    Get user's session usage and judge status
    Returns: (sessions_used, is_judge)
    """
    conn = sqlite3.connect(AUTH_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT sessions_used, is_judge FROM user_sessions WHERE device_id = ?",
        (device_id,)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0], bool(result[1])
    else:
        return 0, False

def increment_session_usage(device_id: str) -> int:
    """
    Increment session usage for a device
    Returns: new session count
    """
    conn = sqlite3.connect(AUTH_DB_PATH)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT sessions_used FROM user_sessions WHERE device_id = ?", (device_id,))
    result = cursor.fetchone()
    
    if result:
        # Update existing user
        new_count = result[0] + 1
        cursor.execute(
            "UPDATE user_sessions SET sessions_used = ?, last_access = CURRENT_TIMESTAMP WHERE device_id = ?",
            (new_count, device_id)
        )
    else:
        # Create new user
        new_count = 1
        cursor.execute(
            "INSERT INTO user_sessions (device_id, sessions_used) VALUES (?, ?)",
            (device_id, new_count)
        )
    
    conn.commit()
    conn.close()
    
    return new_count

def mark_as_judge(device_id: str):
    """Mark a device as judge for unlimited access"""
    conn = sqlite3.connect(AUTH_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO user_sessions (device_id, is_judge, last_access) 
        VALUES (?, 1, CURRENT_TIMESTAMP)
        ON CONFLICT(device_id) 
        DO UPDATE SET is_judge = 1, last_access = CURRENT_TIMESTAMP
        """,
        (device_id,)
    )
    
    conn.commit()
    conn.close()
    logger.info(f"Device {device_id} marked as judge")

def check_session_limit(request: Request) -> Tuple[bool, str, int]:
    """
    Check if user can start a new session
    Returns: (can_access, message, sessions_remaining)
    """
    device_id = get_device_fingerprint(request)
    sessions_used, is_judge = get_user_session_info(device_id)
    
    if is_judge:
        return True, "Judge access - unlimited sessions", -1
    
    if sessions_used >= MAX_FREE_SESSIONS:
        return False, f"You've used all {MAX_FREE_SESSIONS} free sessions. Enter a judge code for unlimited access.", 0
    
    sessions_remaining = MAX_FREE_SESSIONS - sessions_used
    return True, f"Access granted. {sessions_remaining} sessions remaining after this one.", sessions_remaining

def consume_session(request: Request) -> int:
    """
    Consume one session for the user
    Returns: sessions remaining
    """
    device_id = get_device_fingerprint(request)
    sessions_used = increment_session_usage(device_id)
    return MAX_FREE_SESSIONS - sessions_used

async def verify_judge_code_endpoint(request: JudgeCodeRequest, req: Request):
    """
    Verify judge code and grant unlimited access to the device
    """
    device_id = get_device_fingerprint(req)
    logger.info(f"Judge code verification attempt from device {device_id}")
    
    if not request.code:
        logger.warning(f"Empty code submission from device {device_id}")
        raise HTTPException(
            status_code=400,
            detail="Judge code cannot be empty"
        )
    
    if request.code in JUDGE_CODES:
        # Grant unlimited access to this device
        mark_as_judge(device_id)
        logger.info(f"Valid judge code used from device {device_id}")
        return AuthResponse(
            valid=True,
            message="Judge access granted! You now have unlimited sessions.",
            sessions_remaining=-1,
            is_judge=True
        )
    else:
        logger.warning(f"Invalid judge code attempt from device {device_id}: {request.code}")
        raise HTTPException(
            status_code=401,
            detail="Invalid judge code"
        )

def check_access_middleware(request: Request):
    """
    Middleware function to check session limits
    Call this before allowing access to main features
    """
    device_id = get_device_fingerprint(request)
    
    # Skip rate limiting for certain endpoints
    skip_paths = ["/docs", "/openapi.json", "/api/verify-judge", "/scenarios", "/", "/check-access"]
    if any(request.url.path.startswith(path) for path in skip_paths):
        return None
    
    can_access, message, sessions_remaining = check_session_limit(request)
    
    if not can_access:
        logger.warning(f"Session limit exceeded for device {device_id}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Session limit exceeded",
                "message": message,
                "sessions_remaining": 0,
                "solution": "Enter a judge code at /api/verify-judge for unlimited access"
            }
        )
    
    # If it's a session-consuming endpoint, consume one session
    session_paths = ["/get-scenario", "/set-session"]
    if any(request.url.path.startswith(path) for path in session_paths):
        sessions_remaining = consume_session(request)
        logger.info(f"Session consumed for device {device_id}. Remaining: {sessions_remaining}")
    
    return {"message": message, "sessions_remaining": sessions_remaining}

# Initialize database on module load
init_auth_database()