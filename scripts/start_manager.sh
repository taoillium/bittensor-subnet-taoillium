#!/bin/bash
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

cd $CURRENT_DIR/../
echo "Running manager"



python -m manage.main
# uvicorn manage.main:app --reload (for development)
# uvicorn manage.main:app (for production)