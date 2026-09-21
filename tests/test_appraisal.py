"""Tests for Unified Master Appraisal and Agent Middleware."""

import time
import pytest
from soul import appraise
from soul.adapters.agent_middleware import AgentEmpathyMiddleware
from soul.schemas.appraisal import SubjectAppraisalResult


def test_schema_locked_json_serialization():
    text = "I'm feeling somewhat overwhelmed by the workload, but taking it one step at a time."
    res = appraise(text)

    assert isinstance(res, SubjectAppraisalResult)
    json_str = res.model_dump_json()
    assert "adversity" in json_str
    assert "sentiment" in json_str
    assert "agent_guidance" in json_str


def test_sub_50ms_system_one_speed():
    text = "Short sentence testing latency of System 1 appraisal."
    # Warmup
    _ = appraise(text)

    start = time.perf_counter()
    res = appraise(text)
    latency_ms = (time.perf_counter() - start) * 1000.0

    # System 1 execution time should be under 50ms locally
    assert latency_ms < 50.0
    assert res.execution_time_ms < 50.0


def test_agent_middleware_directive():
    middleware = AgentEmpathyMiddleware()
    text = "I failed my certification exam after studying for six months. I feel like an absolute fraud."
    
    appraisal, directive = middleware.process_incoming_message(text)

    assert appraisal.adversity.adversity_score > 0.40
    assert appraisal.agent_guidance.empathy_demand > 0.50
    assert "[SYSTEM 1 AFFECTIVE PERCEPTION]" in directive
    assert "Empathy Demand" in directive
