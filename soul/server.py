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
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import soul
from soul import appraise, respond
from soul.agent.attuned_agent import AttunedAgent
from soul.engine.appraiser import SoulAppraiser
from soul.engine.harmonizer import BluntnessAuditor, ResponseHarmonizer
from soul.schemas.appraisal import SubjectAppraisalResult

# Initialize FastAPI App
app = FastAPI(
    title="Soul Engine API",
    description="Fast System 1 Cognitive Appraisal & Anti-Bluntness Harmonization API for AI Agents",
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

# Singletons
_appraiser = SoulAppraiser()
_auditor = BluntnessAuditor()
_harmonizer = ResponseHarmonizer(auditor=_auditor)
_agent = AttunedAgent(appraiser=_appraiser)


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


# --- Endpoints ---

@app.get("/", tags=["Info"])
def root():
    return {
        "service": "Soul Engine API",
        "version": soul.__version__,
        "status": "online",
        "system_one_latency_target": "<1.0ms",
        "endpoints": {
            "appraise": "POST /v1/appraise",
            "harmonize": "POST /v1/harmonize",
            "respond": "POST /v1/respond",
            "openai_proxy": "POST /v1/chat/completions",
            "models": "GET /v1/models",
            "docs": "/docs",
        },
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
def appraise_endpoint(req: AppraiseRequest):
    """Executes sub-millisecond System 1 cognitive appraisal on text."""
    try:
        return _appraiser.appraise(req.text, subject_id=req.subject_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Appraisal error: {str(e)}")


@app.post("/v1/harmonize", response_model=HarmonizeResponse, tags=["Harmonization"])
def harmonize_endpoint(req: HarmonizeRequest):
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
def respond_endpoint(req: RespondRequest):
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
def openai_chat_completions(req: OpenAIChatRequest):
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
