#!/bin/bash

BASE_DIR="/home/jorge/Documentos/Streamlit"
cd "$BASE_DIR" || exit 1

source venv/bin/activate

exec python modern_dashboard_8504/server.py --host 0.0.0.0 --port 8504
