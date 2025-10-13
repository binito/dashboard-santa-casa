#!/bin/bash
# Script de inicialização do Dashboard Streamlit

cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
exec streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
