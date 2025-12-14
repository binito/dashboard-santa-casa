#!/bin/bash
# Script de inicialização do Dashboard Streamlit - Santa Casa (app.cafemartins.pt)

cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
exec streamlit run dashboard_santa_casa.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
