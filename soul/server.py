"""FastAPI Production REST API & OpenAI-Compatible Gateway for Soul Engine.

Provides ultra-fast sub-millisecond endpoints for:
- POST /v1/appraise: Fast System 1 cognitive stress, VAD affect, and feelings appraisal.
- POST /v1/harmonize: Anti-bluntness response inspection and empathetic transformation.
- POST /v1/respond: End-to-end emotionally attuned generation.
- POST /v1/chat/completions: OpenAI-compatible drop-in proxy endpoint.
- GET /health: Liveness and status check.
- GET /v1/models: OpenAI-compatible models list.
"""

import time
import uuid
import os
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

import soul
from soul import appraise, respond
from soul.agent.attuned_agent import AttunedAgent
from soul.auth import (
    UserManager,
    create_access_token,
    decode_access_token,
    verify_google_token,
)
from soul.engine.api_key_manager import APIKeyManager
from soul.engine.appraiser import SoulAppraiser
from soul.engine.harmonizer import BluntnessAuditor, ResponseHarmonizer
from soul.schemas.appraisal import SubjectAppraisalResult

# Initialize FastAPI App
app = FastAPI(
    title="Soul Engine API",
    description="Fast System 1 Cognitive Appraisal, Anti-Bluntness SaaS & OpenAI Proxy Gateway",
    version=soul.__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS so any frontend, mobile app, or client can access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files directory for SaaS Frontend
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Singletons
_appraiser = SoulAppraiser()
_auditor = BluntnessAuditor()
_harmonizer = ResponseHarmonizer(auditor=_auditor)
_agent = AttunedAgent(appraiser=_appraiser)
_key_manager = APIKeyManager()
_user_manager = UserManager()


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

    require_auth = os.getenv("SOUL_REQUIRE_AUTH", "0") in ("1", "true", "True")

    if token:
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
    text: str = Field(..., min_length=1, description="The user message or conversation state to appraise")
    subject_id: Optional[str] = Field(None, description="Optional subject identifier for session tracking")


class HarmonizeRequest(BaseModel):
    user_message: Optional[str] = Field(None, description="Original user message providing emotional context")
    draft_response: str = Field(..., min_length=1, description="Candidate AI response to audit and harmonize")
    appraisal: Optional[SubjectAppraisalResult] = Field(None, description="Pre-computed appraisal if already available")


class HarmonizeResponse(BaseModel):
    harmonized_content: str = Field(..., description="The audited and softened empathetic response")
    was_harmonized: bool = Field(..., description="True if anti-bluntness intervention was applied")
    warmth_score: float = Field(..., description="Calculated warmth score of the response (0.0 to 1.0)")
    is_blunt: bool = Field(..., description="True if the raw draft was diagnosed as blunt or cold")
    empathy_demand: float = Field(..., description="Subject's empathy demand score")
    latency_ms: float = Field(..., description="Processing time in milliseconds")


class RespondRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Incoming user message")
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
    role: str
    content: str


class OpenAIChatRequest(BaseModel):
    model: Optional[str] = "soul-attuned"
    messages: list[ChatMessage] = Field(..., min_length=1)
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 800
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
            "google_login": "POST /v1/auth/google",
            "me": "GET /v1/auth/me",
            "list_keys": "GET /v1/keys",
            "create_key": "POST /v1/keys",
            "appraise": "POST /v1/appraise",
            "harmonize": "POST /v1/harmonize",
            "respond": "POST /v1/respond",
            "openai_proxy": "POST /v1/chat/completions",
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
        # For testing / demo purposes if an invalid or demo token is passed:
        if req.token in ("demo_google_token", "test_google_token"):
            profile = {
                "email": "demo.google.user@navigotechsolutions.com",
                "name": "Navigo Google User",
                "picture": "",
                "sub": "demo-google-sub-12345",
            }
        else:
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


@app.get("/v1/models", tags=["OpenAI Compatible"])
def list_models():
    """Returns OpenAI-compatible model list."""
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
    elif req.user_message:
        appraisal = _appraiser.appraise(req.user_message)
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'user_message' or 'appraisal' must be provided for contextual audit."
        )

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


@app.post("/v1/chat/completions", tags=["OpenAI Compatible"])
def openai_chat_completions(req: OpenAIChatRequest, client: Optional[dict] = Depends(get_current_client)):
    """OpenAI-compatible drop-in proxy endpoint.
    
    Any client using standard OpenAI SDK can point base_url to this server
    and receive emotionally attuned, non-blunt responses automatically.
    """
    if not req.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty.")

    # Extract user message and optional system message
    system_prompt = "You are a helpful and knowledgeable AI assistant."
    user_message = ""

    for msg in req.messages:
        if msg.role == "system":
            system_prompt = msg.content
        elif msg.role == "user":
            user_message = msg.content

    if not user_message:
        user_message = req.messages[-1].content

    # Run attuned response
    t0 = time.perf_counter()
    resp = _agent.respond(
        user_message=user_message,
        base_system_prompt=system_prompt,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    chat_id = f"chatcmpl-soul-{uuid.uuid4().hex[:12]}"
    now_ts = int(time.time())

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
