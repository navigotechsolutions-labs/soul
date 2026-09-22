"""Standalone Runner for the Soul Engine Production REST API.

Usage:
    python serve.py
    python serve.py --port 8000 --host 0.0.0.0 --reload
"""

import argparse
import sys
import uvicorn

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Start the Soul Engine REST API Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    print(f"\n================================================================================")
    print(f"🚀 Soul Engine Production REST API Server on http://{args.host}:{args.port}")
    print(f"🖥️  Web Dashboard:             http://localhost:{args.port}/dashboard")
    print(f"📖 Interactive Swagger Docs:  http://localhost:{args.port}/docs")
    print(f"⚡ Universal Chat Gateway:     http://localhost:{args.port}/v1/chat/completions")
    print(f"================================================================================\n")

    uvicorn.run(
        "soul.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
