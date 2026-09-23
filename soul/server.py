"""FastAPI Production REST API & Universal Emotional Intelligence Gateway for Soul Engine.

Provides ultra-fast sub-millisecond endpoints for:
- POST /v1/appraise: Fast System 1 cognitive stress, VAD affect, and feelings appraisal.
- POST /v1/harmonize: Anti-bluntness response inspection and empathetic transformation.
- POST /v1/respond: End-to-end emotionally attuned generation.
- POST /v1/chat/completions: Universal chat completions endpoint compatible with standard client tools.
- GET /health: Liveness and status check.
- GET /v1/models: Available models directory.
"""

import asyncio
import hashlib
import sqlite3
import time
import uuid
import secrets
import os
import json
import re
from pathlib import Path
from typing import Any, Literal, Optional

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, model_validator


import soul
from soul import appraise, respond
from soul.agent.attuned_agent import AttunedAgent
from soul.auth import (
    UserManager,
    create_access_token,
    decode_access_token,
    verify_google_token,
    default_email_service,
)
from soul.engine.api_key_manager import APIKeyManager
from soul.engine.appraiser import SoulAppraiser
from soul.engine.harmonizer import BluntnessAuditor, ResponseHarmonizer
from soul.schemas.appraisal import SubjectAppraisalResult

# Initialize FastAPI App
app = FastAPI(
    title="Soul Engine API",
    description="Fast System 1 Cognitive Appraisal, Anti-Bluntness SaaS & Universal Emotional Gateway",
    version=soul.__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS so any frontend, mobile app, or client can access the API
_cors_origins = [origin.strip() for origin in os.getenv(
    "SOUL_CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
).split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files directory for SaaS Frontend & Soul IDE
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def root(request: Request):
        """Serves Soul IDE for browser navigations or API directory JSON for API clients."""
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return FileResponse(str(STATIC_DIR / "index.html"))
        return {
            "service": "Soul Engine API",
            "version": soul.__version__,
            "status": "online",
            "endpoints": [
                "/v1/appraise",
                "/v1/harmonize",
                "/v1/respond",
                "/v1/chat/completions",
                "/v1/audit/human-pov",
                "/v1/sanitize/anti-slop",
                "/v1/anti-slop",
                "/ide",
            ],
            "ide_url": "/ide",
        }


    @app.get("/ide", include_in_schema=False)
    @app.get("/dashboard", include_in_schema=False)
    def serve_ide():
        """Serves the standalone Soul IDE developer application."""
        return FileResponse(str(STATIC_DIR / "index.html"))

    @app.get("/robots.txt", include_in_schema=False)
    def robots_txt():
        """Serves robots.txt for search engines and crawlers."""
        return FileResponse(str(STATIC_DIR / "robots.txt"), media_type="text/plain")

    @app.get("/sitemap.xml", include_in_schema=False)
    def sitemap_xml():
        """Serves sitemap.xml for search engines and crawlers."""
        return FileResponse(str(STATIC_DIR / "sitemap.xml"), media_type="application/xml")



# Singletons
_appraiser = SoulAppraiser()
_auditor = BluntnessAuditor()
_harmonizer = ResponseHarmonizer(auditor=_auditor)
_agent = AttunedAgent(appraiser=_appraiser)
_key_manager = APIKeyManager()
_user_manager = UserManager()
with sqlite3.connect(_key_manager.db_path) as _rate_limit_db:
    _rate_limit_db.execute(
        "CREATE TABLE IF NOT EXISTS rate_limit_events (bucket TEXT NOT NULL, requested_at REAL NOT NULL)"
    )
    _rate_limit_db.execute(
        "CREATE INDEX IF NOT EXISTS idx_rate_limit_events_bucket_time ON rate_limit_events(bucket, requested_at)"
    )


def _consume_rate_limit(bucket: str, limit: int, now: float) -> bool:
    """Atomically enforce a rolling per-identity window in the shared SQLite DB."""
    with sqlite3.connect(_key_manager.db_path, timeout=10) as conn:
        conn.execute("PRAGMA busy_timeout = 10000")
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM rate_limit_events WHERE requested_at <= ?", (now - 60.0,))
        count = conn.execute(
            "SELECT COUNT(*) FROM rate_limit_events WHERE bucket = ? AND requested_at > ?",
            (bucket, now - 60.0),
        ).fetchone()[0]
        if count >= limit:
            conn.rollback()
            return False
        conn.execute("INSERT INTO rate_limit_events(bucket, requested_at) VALUES (?, ?)", (bucket, now))
        conn.commit()
        return True


@app.middleware("http")
async def enforce_api_rate_limits(request: Request, call_next):
    if request.url.path.startswith("/v1/") and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            identity = auth_header[7:].strip()
        else:
            identity = request.headers.get("x-api-key", "")
        client_ip = request.client.host if request.client else "unknown"
        ip_fingerprint = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()

        path = request.url.path
        if path in {"/v1/auth/signup", "/v1/auth/login", "/v1/auth/google"}:
            checks = [(f"auth:{ip_fingerprint}", 20)]
        elif path == "/v1/auth/keys/generate":
            checks = [(f"keygen:{ip_fingerprint}", 10)]
        else:
            checks = [(f"api-ip:{ip_fingerprint}", 600)]
            if identity:
                identity_fingerprint = hashlib.sha256(identity.encode("utf-8")).hexdigest()
                checks.append((f"api-key:{identity_fingerprint}", 120))
            else:
                checks[0] = (f"api-ip:{ip_fingerprint}", 120)

        now = time.time()
        for bucket, limit in checks:
            allowed = await asyncio.to_thread(_consume_rate_limit, bucket, limit, now)
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Try again in one minute."},
                    headers={"Retry-After": "60"},
                )
    return await call_next(request)


def get_current_user(authorization: Optional[str] = Header(None)) -> dict[str, Any]:
    """Extracts and validates JWT Bearer access token for logged-in users."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication token required. Please sign in or pass Authorization: Bearer <jwt_token>"
        )
    token = authorization[7:].strip()
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Session expired or invalid token. Please sign in again.")
    
    user = _user_manager.get_user_by_id(payload["sub"])
    if not user or not user.get("is_active"):
        raise HTTPException(status_code=401, detail="User account not found or suspended.")
    return user


def get_current_client(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
) -> Optional[dict]:
    """Extracts and validates API key or Bearer token; enforces authentication if SOUL_REQUIRE_AUTH=1."""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    elif x_api_key:
        token = x_api_key.strip()

    require_auth = os.getenv("SOUL_REQUIRE_AUTH", "1").lower() in ("1", "true", "yes")

    if token:
        # Browser sessions use JWTs; SDK clients use revocable API keys.
        session = decode_access_token(token)
        if session and session.get("sub"):
            user = _user_manager.get_user_by_id(session["sub"])
            if user and user.get("is_active"):
                return user
        # Check user database first (User-created API keys)
        user_key_info = _user_manager.validate_api_key(token)
        if user_key_info:
            return user_key_info

        # Check self-service anonymous key manager
        if _key_manager.validate_key(token):
            _key_manager.record_usage(token)
            return _key_manager.get_key_info(token)
        elif require_auth:
            raise HTTPException(status_code=401, detail="Invalid or revoked Soul API key.")
    elif require_auth:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Generate a key or provide Authorization: Bearer <key>"
        )

    return None


# --- Request & Response Schemas ---

class AppraiseRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000, description="Text to appraise (maximum 20,000 characters)")
    subject_id: Optional[str] = Field(None, description="Optional subject identifier for session tracking")


class HarmonizeRequest(BaseModel):
    user_message: Optional[str] = Field(None, max_length=20000, description="Optional user message providing emotional context")
    draft_response: Optional[str] = Field(None, max_length=20000, description="Candidate response to audit and harmonize")
    text: Optional[str] = Field(None, max_length=20000, description="Alias for draft_response")
    content: Optional[str] = Field(None, max_length=20000, description="Alias for draft_response")
    appraisal: Optional[SubjectAppraisalResult] = Field(None, description="Pre-computed appraisal if already available")

    @model_validator(mode="after")
    def resolve_draft_content(self) -> "HarmonizeRequest":
        # Resolve whichever content field was supplied
        effective_draft = self.draft_response or self.text or self.content
        if not effective_draft or not effective_draft.strip():
            raise ValueError(
                "Either 'draft_response', 'text', or 'content' must be provided with at least 1 character."
            )
        self.draft_response = effective_draft.strip()
        return self



class HarmonizeResponse(BaseModel):
    harmonized_content: str = Field(..., description="The audited and softened empathetic response")
    was_harmonized: bool = Field(..., description="True if anti-bluntness intervention was applied")
    warmth_score: float = Field(..., description="Calculated warmth score of the response (0.0 to 1.0)")
    is_blunt: bool = Field(..., description="True if the raw draft was diagnosed as blunt or cold")
    empathy_demand: float = Field(..., description="Subject's empathy demand score")
    latency_ms: float = Field(..., description="Processing time in milliseconds")


class RespondRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=20000, description="Incoming user message (maximum 20,000 characters)")
    base_system_prompt: Optional[str] = Field(
        "You are a helpful and knowledgeable AI assistant.",
        description="Base instructions for the AI"
    )
    subject_id: Optional[str] = Field(None, description="Optional user or session identifier")


class RespondResponse(BaseModel):
    content: str = Field(..., description="Final empathetic, non-blunt response")
    raw_draft: str = Field(..., description="Raw generated candidate draft before harmonization")
    was_harmonized: bool = Field(..., description="True if response was modified by harmonizer")
    warmth_score: float = Field(..., description="Measured warmth score")
    appraisal: SubjectAppraisalResult = Field(..., description="System 1 appraisal of user input")
    execution_time_ms: float = Field(..., description="Total execution time in milliseconds")


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., max_length=20000)


class OpenAIChatRequest(BaseModel):
    model: Optional[str] = "soul-attuned"
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=50)
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(800, ge=1, le=32000)
    stream: Optional[bool] = False


class GenerateKeyRequest(BaseModel):
    client_name: str = Field(..., min_length=1, description="Your project name, organization, or developer name")
    email: Optional[str] = Field("", description="Optional contact email for developer notifications")


class GenerateKeyResponse(BaseModel):
    api_key: str = Field(..., description="Your secret API key. Store this securely.")
    key_prefix: str = Field(..., description="Public key identifier")
    client_name: str = Field(..., description="Registered project or developer name")
    tier: str = Field(..., description="Assigned tier (e.g. free)")
    created_at: float = Field(..., description="Unix timestamp of key generation")
    rate_limit: str = Field(..., description="Allowed requests per minute")
    message: str = Field(..., description="Instructions on how to use this key")


class UserSignupRequest(BaseModel):
    email: str = Field(..., min_length=3, description="User email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    full_name: Optional[str] = Field(None, description="Full name or developer alias")


class UserLoginRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)


class GoogleLoginRequest(BaseModel):
    token: str = Field(..., min_length=1, description="Google OAuth ID token or access token")


class SendOtpRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254, description="Email address to receive the 6-digit OTP code")


class VerifyOtpRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254, description="Email address being verified")
    code: str = Field(..., min_length=4, max_length=10, description="6-digit verification code")
    full_name: Optional[str] = Field(None, description="Optional name for first-time profile creation")


class CreateUserKeyRequest(BaseModel):
    name: Optional[str] = Field("Production Key", min_length=1, description="Friendly name for the API key")


# --- Endpoints ---

@app.get("/", tags=["Info"])
def root(accept: Optional[str] = Header(None)):
    """Serves the interactive SaaS Web Portal for browsers, or API metadata for JSON clients."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists() and accept and "text/html" in accept and "application/json" not in accept:
        return FileResponse(str(index_file))

    return {
        "service": "Soul Engine API",
        "version": soul.__version__,
        "status": "online",
        "system_one_latency_target": "<1.0ms",
        "endpoints": {
            "web_portal": "/dashboard",
            "signup": "POST /v1/auth/signup",
            "login": "POST /v1/auth/login",
            "otp_send": "POST /v1/auth/otp/send",
            "otp_verify": "POST /v1/auth/otp/verify",
            "google_login": "POST /v1/auth/google",
            "me": "GET /v1/auth/me",
            "list_keys": "GET /v1/keys",
            "create_key": "POST /v1/keys",
            "appraise": "POST /v1/appraise",
            "harmonize": "POST /v1/harmonize",
            "respond": "POST /v1/respond",
            "chat_completions": "POST /v1/chat/completions",
            "ratings": "POST /v1/ratings",
            "docs": "/docs",
        },
    }


@app.get("/dashboard", tags=["Web Portal"])
def dashboard():
    """Serves the interactive SaaS Web Portal."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "service": "Soul Engine API",
        "message": "Web portal file not found. Use REST endpoints directly."
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Serves the brand vector favicon."""
    fav = STATIC_DIR / "favicon.svg"
    if fav.exists():
        return FileResponse(str(fav), media_type="image/svg+xml")
    return FileResponse(str(STATIC_DIR / "index.html"))


# --- User Authentication & OAuth Endpoints ---

@app.post("/v1/auth/signup", tags=["User Authentication"])
def signup(req: UserSignupRequest):
    """Registers a new user account with email and password, returning a JWT session token."""
    try:
        user = _user_manager.create_user_with_email(
            email=req.email,
            password=req.password,
            full_name=req.full_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    token = create_access_token({"sub": user["id"], "email": user["email"], "tier": user["tier"]})
    return {
        "user": user,
        "access_token": token,
        "token_type": "bearer",
    }


@app.post("/v1/auth/login", tags=["User Authentication"])
def login(req: UserLoginRequest):
    """Authenticates with email and password, returning a JWT session token."""
    user = _user_manager.authenticate_user(email=req.email, password=req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token({"sub": user["id"], "email": user["email"], "tier": user["tier"]})
    # Remove password hash from response
    user_clean = {k: v for k, v in user.items() if k != "password_hash"}
    return {
        "user": user_clean,
        "access_token": token,
        "token_type": "bearer",
    }


@app.post("/v1/auth/google", tags=["User Authentication"])
def google_auth(req: GoogleLoginRequest):
    """Authenticates via Google OAuth token, auto-provisioning the user if needed."""
    profile = verify_google_token(req.token)
    if not profile:
        raise HTTPException(status_code=401, detail="Invalid or expired Google OAuth token.")

    user = _user_manager.find_or_create_google_user(
        email=profile["email"],
        full_name=profile.get("name", ""),
        avatar_url=profile.get("picture", ""),
        google_sub=profile.get("sub", ""),
    )

    token = create_access_token({"sub": user["id"], "email": user["email"], "tier": user["tier"]})
    return {
        "user": user,
        "access_token": token,
        "token_type": "bearer",
    }


@app.post("/v1/auth/otp/send", tags=["User Authentication"])
def send_otp_endpoint(req: SendOtpRequest):
    """Generates and dispatches a 6-digit verification code to the user's email."""
    email = req.email.strip().lower()
    if "@" not in email or "." not in email:
        raise HTTPException(status_code=400, detail="Invalid email address format.")

    # Generate 6-digit verification code
    code = "".join(secrets.choice("0123456789") for _ in range(6))

    # Store in database with 10-minute validity
    _user_manager.store_otp(email=email, code=code, validity_seconds=600)

    # Dispatch email
    result = default_email_service.send_otp_email(to_email=email, code=code, expires_in_minutes=10)

    response = {
        "status": "success",
        "message": f"6-digit verification code sent to {email}.",
        "expires_in_seconds": 600,
        "delivery_method": result.get("method"),
    }
    if result.get("dev_otp"):
        response["dev_otp_hint"] = result["dev_otp"]

    return response


@app.post("/v1/auth/otp/verify", tags=["User Authentication"])
def verify_otp_endpoint(req: VerifyOtpRequest):
    """Verifies the 6-digit email code and returns an authenticated JWT session."""
    email = req.email.strip().lower()
    is_valid = _user_manager.verify_otp(email=email, code=req.code)

    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired verification code. Please request a new code.",
        )

    user = _user_manager.find_or_create_otp_user(email=email, full_name=req.full_name)
    token = create_access_token({"sub": user["id"], "email": user["email"], "tier": user["tier"]})

    return {
        "status": "success",
        "user": user,
        "access_token": token,
        "token_type": "bearer",
    }


@app.get("/v1/auth/me", tags=["User Authentication"])
def get_me(user: dict = Depends(get_current_user)):
    """Returns the current authenticated user profile."""
    return user


# --- User API Key Lifecycle Endpoints ---

@app.get("/v1/keys", tags=["User API Keys"])
def list_user_keys(user: dict = Depends(get_current_user)):
    """Lists all active and revoked API keys belonging to the logged-in user."""
    return _user_manager.list_api_keys_for_user(user["id"])


@app.post("/v1/keys", tags=["User API Keys"])
def create_user_key(req: CreateUserKeyRequest, user: dict = Depends(get_current_user)):
    """Generates a new secret API key linked to the user's account."""
    return _user_manager.create_api_key_for_user(user_id=user["id"], key_name=req.name or "API Key")


@app.delete("/v1/keys/{key_id}", tags=["User API Keys"])
def revoke_user_key(key_id: str, user: dict = Depends(get_current_user)):
    """Permanently revokes an API key belonging to the user."""
    success = _user_manager.revoke_api_key_for_user(user_id=user["id"], key_id=key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found or does not belong to your account.")
    return {"status": "revoked", "key_id": key_id}


# --- Self-Service Quick Key Endpoints ---

@app.post("/v1/auth/keys/generate", response_model=GenerateKeyResponse, tags=["Self-Service API Keys"])
def generate_api_key(req: GenerateKeyRequest):
    """Generates a personal API key so anyone can integrate Soul into their app or pipeline."""
    key_info = _key_manager.generate_key(client_name=req.client_name, email=req.email or "")
    return GenerateKeyResponse(**key_info)


@app.get("/v1/auth/keys/info", tags=["Self-Service API Keys"])
def get_key_info(client: Optional[dict] = Depends(get_current_client)):
    """Retrieves usage statistics and tier info for your personal API key."""
    if not client:
        raise HTTPException(
            status_code=401,
            detail="No valid API key provided. Pass Authorization: Bearer <key> in headers."
        )
    return {
        "status": "active",
        "client": client,
    }


@app.get("/health", tags=["Info"])
def health():
    return {
        "status": "healthy",
        "version": soul.__version__,
        "timestamp": time.time(),
    }


@app.get("/v1/models", tags=["Universal Chat Gateway"])
def list_models():
    """Returns model directory compatible with standard chat clients and CLI tools."""
    return {
        "object": "list",
        "data": [
            {
                "id": "soul-attuned",
                "object": "model",
                "created": 1700000000,
                "owned_by": "soul-engine",
                "description": "System 1 Emotionally Attuned AI model with anti-bluntness protection",
            },
            {
                "id": "gpt-4o",
                "object": "model",
                "created": 1700000000,
                "owned_by": "soul-engine",
                "description": "Soul Attuned Proxy routing for gpt-4o",
            },
            {
                "id": "gpt-4",
                "object": "model",
                "created": 1700000000,
                "owned_by": "soul-engine",
                "description": "Soul Attuned Proxy routing for gpt-4",
            },
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": 1700000000,
                "owned_by": "soul-engine",
                "description": "Soul Attuned Proxy routing for gpt-3.5-turbo",
            },
            {
                "id": "claude-3-5-sonnet",
                "object": "model",
                "created": 1700000000,
                "owned_by": "soul-engine",
                "description": "Soul Attuned Proxy routing for Claude",
            },
            {
                "id": "soul-appraiser",
                "object": "model",
                "created": 1700000000,
                "owned_by": "soul-engine",
                "description": "Sub-millisecond affective perception & stress appraisal model",
            }
        ]
    }


@app.post("/v1/appraise", response_model=SubjectAppraisalResult, tags=["Appraisal"])
def appraise_endpoint(req: AppraiseRequest, client: Optional[dict] = Depends(get_current_client)):
    """Executes sub-millisecond System 1 cognitive appraisal on text."""
    try:
        return _appraiser.appraise(req.text, subject_id=req.subject_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Appraisal error: {str(e)}")


@app.post("/v1/harmonize", response_model=HarmonizeResponse, tags=["Harmonization"])
def harmonize_endpoint(req: HarmonizeRequest, client: Optional[dict] = Depends(get_current_client)):
    """Audits a candidate response and harmonizes it if bluntness is detected."""
    t0 = time.perf_counter()

    # Determine appraisal
    if req.appraisal:
        appraisal = req.appraisal
    elif req.user_message and req.user_message.strip():
        appraisal = _appraiser.appraise(req.user_message)
    else:
        # Default user_message to standalone draft context internally instead of failing with 400
        appraisal = _appraiser.appraise(req.draft_response)

    audit_result = _auditor.audit(req.draft_response, appraisal)
    harmonized_text, was_altered = _harmonizer.harmonize(req.draft_response, appraisal)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    return HarmonizeResponse(
        harmonized_content=harmonized_text,
        was_harmonized=was_altered,
        warmth_score=audit_result["warmth_score"],
        is_blunt=audit_result["is_blunt"],
        empathy_demand=appraisal.agent_guidance.empathy_demand,
        latency_ms=round(elapsed_ms, 2),
    )


@app.post("/v1/respond", response_model=RespondResponse, tags=["Agent"])
def respond_endpoint(req: RespondRequest, client: Optional[dict] = Depends(get_current_client)):
    """Generates an emotionally attuned, anti-blunt response from scratch."""
    t0 = time.perf_counter()
    agent_resp = _agent.respond(
        user_message=req.message,
        base_system_prompt=req.base_system_prompt or "You are a helpful and knowledgeable AI assistant.",
        subject_id=req.subject_id,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    return RespondResponse(
        content=agent_resp.content,
        raw_draft=agent_resp.raw_draft,
        was_harmonized=agent_resp.was_harmonized,
        warmth_score=agent_resp.warmth_score,
        appraisal=agent_resp.appraisal,
        execution_time_ms=round(elapsed_ms, 2),
    )


@app.post("/v1/chat/completions", tags=["Universal Chat Gateway"])
def universal_chat_completions(req: OpenAIChatRequest, client: Optional[dict] = Depends(get_current_client)):
    """Universal chat completions gateway endpoint.
    
    Any standard chat client, terminal CLI, or SDK can point base_url to this server
    using a Soul API Key (`soul_live_...`) to receive emotionally attuned, non-blunt responses.
    Supports native Server-Sent Events (SSE) streaming when stream=true.
    """
    if not req.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty.")

    # Preserve the full conversation as context. The last user message remains
    # the direct request; earlier turns are included in the system context.
    system_prompt = "You are a helpful and knowledgeable AI assistant."
    user_messages = [msg for msg in req.messages if msg.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="At least one user message is required.")
    system_messages = [msg.content for msg in req.messages if msg.role == "system"]
    if system_messages:
        system_prompt = "\n\n".join(system_messages)
    user_message = user_messages[-1].content
    conversation = [
        {"role": msg.role, "content": msg.content}
        for msg in req.messages
        if msg.role in ("user", "assistant")
    ]

    # Run attuned response with dynamic model routing
    t0 = time.perf_counter()
    resp = _agent.respond(
        user_message=user_message,
        base_system_prompt=system_prompt,
        model_name=req.model,
        conversation=conversation,
        temperature=req.temperature if req.temperature is not None else 0.7,
        max_tokens=req.max_tokens if req.max_tokens is not None else 800,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    chat_id = f"chatcmpl-soul-{uuid.uuid4().hex[:12]}"
    now_ts = int(time.time())

    # Native Server-Sent Events (SSE) Streaming Support
    if req.stream:
        async def event_stream():
            # Initial chunk (assistant role)
            initial_chunk = {
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": now_ts,
                "model": req.model or "soul-attuned",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant"},
                        "finish_reason": None,
                    }
                ],
            }
            yield f"data: {json.dumps(initial_chunk)}\n\n"

            # Stream words/tokens incrementally with natural pacing for interactive UIs
            # Splits preserving whitespace so reconstruction is verbatim
            content = resp.content
            tokens = re.findall(r"\S+\s*|\s+", content) if content else [""]
            
            for token in tokens:
                chunk = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": now_ts,
                    "model": req.model or "soul-attuned",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": token},
                            "finish_reason": None,
                        }
                    ],
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                # Natural typing cadence (sub-millisecond to 10ms pacing)
                await asyncio.sleep(0.008)

            # Final stop chunk with soul metadata attached
            stop_chunk = {
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": now_ts,
                "model": req.model or "soul-attuned",
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop",
                    }
                ],
                "soul_meta": {
                    "adversity_domain": resp.appraisal.adversity.primary_domain.value,
                    "appraisal_stance": resp.appraisal.adversity.appraisal_stance.value,
                    "was_harmonized": resp.was_harmonized,
                    "warmth_score": resp.warmth_score,
                    "empathy_demand": resp.appraisal.agent_guidance.empathy_demand,
                    "latency_ms": round(elapsed_ms, 2),
                }
            }
            yield f"data: {json.dumps(stop_chunk)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )


    return {
        "id": chat_id,
        "object": "chat.completion",
        "created": now_ts,
        "model": req.model or "soul-attuned",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": resp.content,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": len(user_message.split()),
            "completion_tokens": len(resp.content.split()),
            "total_tokens": len(user_message.split()) + len(resp.content.split()),
        },
        "soul_meta": {
            "adversity_domain": resp.appraisal.adversity.primary_domain.value,
            "adversity_score": resp.appraisal.adversity.adversity_score,
            "empathy_demand": resp.appraisal.agent_guidance.empathy_demand,
            "recommended_tone": resp.appraisal.agent_guidance.recommended_tone,
            "was_harmonized": resp.was_harmonized,
            "warmth_score": resp.warmth_score,
            "latency_ms": round(elapsed_ms, 2),
        },
    }


class HumanFeelAuditRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=20000, description="Text to audit (maximum 20,000 characters)")
    user_context: Optional[str] = Field(None, max_length=20000, description="Optional user prompt providing emotional context")
    include_aesthetics: Optional[bool] = Field(True, description="Whether to check CSS/colors for AI tropes")


class SanitizeSlopRequest(BaseModel):
    text: Optional[str] = Field(None, max_length=20000, description="Text containing patterns to sanitize")
    content: Optional[str] = Field(None, max_length=20000, description="Alternative field for text content")
    draft_response: Optional[str] = Field(None, max_length=20000, description="Alternative field for draft response")


@app.post("/v1/audit/human-pov", tags=["Human Experience"])
@app.post("/v1/audit/human-feel", tags=["Human Experience"])
def audit_human_pov_endpoint(req: HumanFeelAuditRequest, client: Optional[dict] = Depends(get_current_client)):
    """Audits AI responses, UI copy, or code for AI slop, emojis-as-icons, em-dashes, and palettes."""
    from soul import audit_human_feel
    try:
        report = audit_human_feel(
            content=req.content,
            user_context=req.user_context,
            include_aesthetics=req.include_aesthetics if req.include_aesthetics is not None else True
        )
        return report.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Human audit error: {str(e)}")


@app.post("/v1/sanitize/anti-slop", tags=["Human Experience"])
@app.post("/v1/anti-slop", tags=["Human Experience"])
def sanitize_slop_endpoint(req: SanitizeSlopRequest, client: Optional[dict] = Depends(get_current_client)):
    """Eradicates AI buzzwords, replaces em-dashes, and strips emoji crutches for human cadence."""
    from soul import sanitize_slop
    raw_text = req.text or req.content or req.draft_response
    if not raw_text:
        raise HTTPException(status_code=400, detail="Must provide 'text', 'content', or 'draft_response'.")
    try:
        sanitized = sanitize_slop(raw_text)
        return {"original": raw_text, "sanitized": sanitized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sanitization error: {str(e)}")


# --- Community Ratings & Reviews Endpoints ---

class SubmitRatingRequest(BaseModel):
    score: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    author_name: Optional[str] = Field(None, max_length=100, description="Your name or company handle")
    feedback: Optional[str] = Field(None, max_length=1000, description="Optional thoughts, review, or suggestions")


@app.post("/v1/ratings", tags=["Community"])
def submit_rating_endpoint(req: SubmitRatingRequest, request: Request):
    """Submits a community rating (1-5 stars) and feedback for Soul Engine."""
    user_id = None
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        payload = decode_access_token(auth_header[7:].strip())
        if payload:
            user_id = payload.get("sub")

    result = _user_manager.submit_rating(
        score=req.score,
        author_name=req.author_name,
        feedback=req.feedback,
        user_id=user_id,
    )
    return {"status": "success", "rating": result}


@app.get("/v1/ratings", tags=["Community"])
def get_ratings_endpoint():
    """Fetches aggregate community rating score and recent user reviews."""
    return _user_manager.get_ratings_summary()
