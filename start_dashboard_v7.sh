#!/bin/bash
# Script de inicialização do Dashboard v7 Streamlit - Café Martins (app2.cafemartins.pt)
# Dashboard com integração Despesify (custos REAIS) + Autenticação

cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
exec streamlit run dashboard_v7.py --server.port=8502 --server.address=0.0.0.0 --server.headless=true
