#!/usr/bin/env bash
# ==============================================================================
# Soul Engine — One-Click Deploy & Launch Script for VPS / Web Panels
# ==============================================================================
set -e

echo "🚀 [1/4] Updating repository from origin/main..."
if [ -d ".git" ]; then
    git pull origin main
else
    echo "Cloning latest Soul Engine repository..."
    git clone https://github.com/navigotechsolutions-labs/soul.git .
fi

echo "📦 [2/4] Installing / Updating Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -e .
python3 -m pip install fastapi uvicorn rich pydantic numpy

echo "🔑 [3/4] Ensuring secure environment settings..."
if [ -z "$SOUL_JWT_SECRET" ]; then
    export SOUL_JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "Generated SOUL_JWT_SECRET=$SOUL_JWT_SECRET"
fi
export SOUL_REQUIRE_AUTH=${SOUL_REQUIRE_AUTH:-1}
export PORT=${PORT:-8000}

echo "⚡ [4/4] Launching Soul Engine Server on 0.0.0.0:${PORT}..."
echo "--------------------------------------------------------"
echo "🌐 API Base URL:      http://0.0.0.0:${PORT}"
echo "🖥️ Web Dashboard:     http://0.0.0.0:${PORT}/dashboard"
echo "📖 Swagger API Docs:  http://0.0.0.0:${PORT}/docs"
echo "--------------------------------------------------------"

# Launch via Uvicorn
exec python3 serve.py --host 0.0.0.0 --port "${PORT}"
