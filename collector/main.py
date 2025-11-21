# Copyright © 2025 Jaye Freymann / The Watchtower Project
#
# This file is part of Watchtower, licensed under the Watchtower Community License 1.0.
# You may not use this file except in compliance with the License.
# See LICENSE.md for details.
#
# For commercial licensing: jfreymann@gmail.com

import os
import time
import logging
import secrets
from datetime import datetime, timedelta
from typing import List, Optional

import requests
from fastapi import (
    FastAPI,
    Depends,
    Header,
    HTTPException,
    status,
    Query,
    Request,
)
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, LoginEvent, ApiToken

# ----- logging setup -----
logger = logging.getLogger("watchtower.collector")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Watchtower Collector",
    description="Receives login events from SSH login watcher agents.",
    version="1.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# Env config
INITIAL_TOKEN_ENV = os.environ.get("LOGIN_ALERT_TOKEN")
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

if not ADMIN_API_KEY:
    logger.warning("ADMIN_API_KEY not set. Admin endpoints will not be usable.")

# This will be loaded from DB on startup
EXPECTED_TOKEN: Optional[str] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----- Pydantic models -----

class LoginEventIn(BaseModel):
    type: str = Field(..., description="Type of event, e.g. 'user_login'")
    timestamp: str = Field(..., description="Original event timestamp from agent/journal")
    hostname: str
    user: str
    method: str
    source_ip: str
    source_port: str
    raw_message: Optional[str] = None

    # optional metadata you can pass from agents later
    region: Optional[str] = None
    host_group: Optional[str] = None
    severity: Optional[str] = None  # 'low' | 'medium' | 'high'
    flagged: Optional[bool] = None


class LoginEventOut(BaseModel):
    id: int
    created_at: datetime
    event_timestamp: str
    hostname: str
    user: str
    method: str
    source_ip: str
    source_port: str
    raw_message: Optional[str]
    region: Optional[str]
    host_group: Optional[str]
    severity: Optional[str]
    flagged: bool

    class Config:
        from_attributes = True


class RotateTokenResponse(BaseModel):
    new_token: str
    created_at: datetime


# ----- middleware: access logging -----

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000

    logger.info(
        "%s %s %s %s %.2fms",
        request.client.host if request.client else "?",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response


# ----- token management helpers -----

def load_or_seed_token(db: Session) -> str:
    """
    Load the current API token from the DB.
    If none exists, seed it from LOGIN_ALERT_TOKEN env.
    """
    token_row = (
        db.query(ApiToken)
        .order_by(ApiToken.created_at.desc())
        .first()
    )

    if token_row:
        return token_row.token

    if not INITIAL_TOKEN_ENV:
        raise RuntimeError(
            "No API token found in DB and LOGIN_ALERT_TOKEN env is not set. "
            "Set LOGIN_ALERT_TOKEN for the first run."
        )

    logger.info("Seeding initial API token from LOGIN_ALERT_TOKEN env")
    token_row = ApiToken(token=INITIAL_TOKEN_ENV)
    db.add(token_row)
    db.commit()
    db.refresh(token_row)
    return token_row.token


def rotate_token(db: Session) -> ApiToken:
    """
    Generate and store a new token, return the row.
    """
    new_token = secrets.token_urlsafe(32)
    token_row = ApiToken(token=new_token)
    db.add(token_row)
    db.commit()
    db.refresh(token_row)
    return token_row


def verify_token(token: Optional[str]):
    if EXPECTED_TOKEN is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server not initialized with API token",
        )
    if token != EXPECTED_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def verify_admin_key(admin_key: Optional[str]):
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_API_KEY not configured",
        )
    if admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key",
        )


# ----- Slack fan-out -----

def send_to_slack(event: LoginEventIn):
    if not SLACK_WEBHOOK_URL:
        return

    text = (
        f":warning: *Login detected*\n"
        f"*Host*: `{event.hostname}`\n"
        f"*User*: `{event.user}`\n"
        f"*From*: `{event.source_ip}:{event.source_port}`\n"
        f"*Method*: `{event.method}`\n"
        f"*Event time*: `{event.timestamp}`"
    )

    payload = {"text": text}
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        logger.error("Failed to send Slack notification: %s", e)


# ----- startup hook -----

from sqlalchemy import text

@app.on_event("startup")
def startup_event():
    global EXPECTED_TOKEN
    db = SessionLocal()
    try:
        db.execute(text("PRAGMA journal_mode=WAL;"))
        EXPECTED_TOKEN = load_or_seed_token(db)
        logger.info("Loaded API token from DB")
    finally:
        db.close()


# ----- routes -----

@app.post("/login", status_code=201)
def ingest_login_event(
    payload: LoginEventIn,
    db: Session = Depends(get_db),
    x_login_alert_token: Optional[str] = Header(None),
):
    """
    Ingest a login event from an agent.

    Agents must send header: `X-Login-Alert-Token: <shared secret>`
    """
    verify_token(x_login_alert_token)

    db_event = LoginEvent(
        event_timestamp=payload.timestamp,
        hostname=payload.hostname,
        user=payload.user,
        method=payload.method,
        source_ip=payload.source_ip,
        source_port=payload.source_port,
        raw_message=payload.raw_message or "",
        region=payload.region,
        host_group=payload.host_group,
        severity=payload.severity,
        flagged=bool(payload.flagged) if payload.flagged is not None else False,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    send_to_slack(payload)

    return {"status": "ok", "id": db_event.id}


@app.get("/events", response_model=List[LoginEventOut])
def list_events(
    db: Session = Depends(get_db),
    user: Optional[str] = Query(None),
    hostname: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    host_group: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    flagged: Optional[bool] = Query(None),
    hours: int = Query(24, ge=1, le=168, description="Limit to events in last N hours"),
    limit: int = Query(100, ge=1, le=1000),
    x_admin_api_key: Optional[str] = Header(None),
):
    """
    Query recent login events.

    Protected by X-Admin-Api-Key header.
    """
    verify_admin_key(x_admin_api_key)

    cutoff = datetime.utcnow() - timedelta(hours=hours)
    q = db.query(LoginEvent).filter(LoginEvent.created_at >= cutoff)

    if user:
        q = q.filter(LoginEvent.user == user)
    if hostname:
        q = q.filter(LoginEvent.hostname == hostname)
    if region:
        q = q.filter(LoginEvent.region == region)
    if host_group:
        q = q.filter(LoginEvent.host_group == host_group)
    if severity:
        q = q.filter(LoginEvent.severity == severity)
    if flagged is not None:
        q = q.filter(LoginEvent.flagged == flagged)

    q = q.order_by(LoginEvent.created_at.desc()).limit(limit)
    return q.all()


@app.post("/admin/rotate-token", response_model=RotateTokenResponse)
def admin_rotate_token(
    db: Session = Depends(get_db),
    x_admin_api_key: Optional[str] = Header(None, convert_underscores=False),
):
    """
    Rotate the agent API token.

    Requires header: X-Admin-Api-Key: <admin secret>

    Returns the new token so you can roll it out to agents.
    """
    global EXPECTED_TOKEN

    verify_admin_key(x_admin_api_key)

    token_row = rotate_token(db)
    EXPECTED_TOKEN = token_row.token
    logger.info("API token rotated at %s", token_row.created_at.isoformat())

    return RotateTokenResponse(new_token=token_row.token, created_at=token_row.created_at)


@app.get("/healthz")
def health_check():
    return {"status": "ok"}
