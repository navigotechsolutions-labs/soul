"""Soul Python SDK Client — Pre-packaged 1-line client for Soul Engine.

Provides typed methods, automatic retries with exponential backoff, timeout
controls, and clean error handling for:
- System 1 Cognitive Appraisal (<2ms)
- Standalone & Contextual Anti-Bluntness Harmonization
- Human-POV & Slop Auditing
- OpenAI-compatible Attuned Chat Completions (with SSE streaming)
"""

import json
import os
import time
from typing import Any, Generator, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from soul.schemas.appraisal import SubjectAppraisalResult


class SoulAPIError(Exception):
    """Raised when the Soul Engine API returns an HTTP error."""

    def __init__(self, status_code: int, message: str, payload: Any = None):
        super().__init__(f"Soul API Error [{status_code}]: {message}")
        self.status_code = status_code
        self.message = message
        self.payload = payload


class SoulClient:
    """Official pre-packaged client for Soul Engine.
    
    Usage:
        import soul

        client = soul.SoulClient(api_key="soul_live_...")
        appraisal = client.appraise("I was just laid off with zero notice.")
        print(appraisal.adversity.primary_domain)
        
        # Standalone harmonization without user_message requirement
        harmonized = client.harmonize("Here are steps to solve your issue:\n1. Open docs")
        print(harmonized["harmonized_content"])
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 10.0,
        max_retries: int = 3,
    ):
        self.api_key = api_key or os.getenv("SOUL_API_KEY", "")
        self.base_url = (base_url or os.getenv("SOUL_BASE_URL", "https://soul.navigotechsolutions.com")).rstrip("/")
        self.timeout = timeout
        self.max_retries = max(0, max_retries)

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "soul-python-sdk/0.4.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-Soul-Key"] = self.api_key
        return headers

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[dict[str, Any]] = None,
        stream: bool = False,
    ) -> Any:
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode("utf-8") if data is not None else None
        headers = self._headers()

        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            req = Request(url, data=body, headers=headers, method=method)
            try:
                resp = urlopen(req, timeout=self.timeout)
                if stream:
                    return resp
                resp_bytes = resp.read()
                return json.loads(resp_bytes.decode("utf-8"))
            except HTTPError as e:
                err_body = e.read().decode("utf-8")
                try:
                    parsed_err = json.loads(err_body)
                    msg = parsed_err.get("detail", err_body)
                except Exception:
                    msg = err_body
                last_err = SoulAPIError(e.code, msg, err_body)

                # Retry on 429 (rate limit) or 5xx server errors
                if e.code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                    backoff = (2 ** attempt) * 0.25
                    time.sleep(backoff)
                    continue
                raise last_err
            except (URLError, TimeoutError) as e:
                last_err = e
                if attempt < self.max_retries:
                    backoff = (2 ** attempt) * 0.25
                    time.sleep(backoff)
                    continue
                raise ConnectionError(f"Failed to connect to Soul Engine at {url}: {e}")

        if last_err:
            raise last_err

    # --- Core SDK Methods ---

    def appraise(self, text: str, subject_id: Optional[str] = None) -> SubjectAppraisalResult:
        """Executes sub-2ms cognitive appraisal on text."""
        payload = {"text": text}
        if subject_id:
            payload["subject_id"] = subject_id
        res = self._request("POST", "/v1/appraise", payload)
        return SubjectAppraisalResult(**res)

    def harmonize(
        self,
        text: str,
        user_message: Optional[str] = None,
    ) -> dict[str, Any]:
        """Audits candidate text and harmonizes it if bluntness is detected.
        
        Accepts standalone text or contextual user_message.
        """
        payload: dict[str, Any] = {"draft_response": text}
        if user_message:
            payload["user_message"] = user_message
        return self._request("POST", "/v1/harmonize", payload)

    def audit(self, content: str, user_context: Optional[str] = None) -> dict[str, Any]:
        """Performs a comprehensive Human-POV, AI slop, and breathing room audit."""
        payload = {"content": content, "include_aesthetics": True}
        if user_context:
            payload["user_context"] = user_context
        return self._request("POST", "/v1/audit/human-feel", payload)

    def sanitize(self, text: str) -> str:
        """Removes AI buzzwords, replaces em-dashes, and strips emoji crutches."""
        res = self._request("POST", "/v1/sanitize/anti-slop", {"text": text})
        return res.get("sanitized", text)

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str = "soul-attuned",
        temperature: float = 0.7,
        max_tokens: int = 800,
        stream: bool = False,
    ) -> Any:
        """OpenAI-compatible chat completion with built-in emotional attunement.
        
        If stream=True, returns a generator yielding token chunks.
        """
        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        if not stream:
            return self._request("POST", "/v1/chat/completions", payload)

        raw_resp = self._request("POST", "/v1/chat/completions", payload, stream=True)

        def sse_generator() -> Generator[dict[str, Any], None, None]:
            buffer = ""
            for line in raw_resp:
                decoded = line.decode("utf-8")
                buffer += decoded
                while "\n\n" in buffer:
                    event, buffer = buffer.split("\n\n", 1)
                    event = event.strip()
                    if not event:
                        continue
                    if event.startswith("data: "):
                        data_part = event[6:].strip()
                        if data_part == "[DONE]":
                            return
                        try:
                            yield json.loads(data_part)
                        except json.JSONDecodeError:
                            continue

        return sse_generator()
