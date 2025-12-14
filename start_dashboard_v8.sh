#!/bin/bash
# Script de inicialização do Dashboard v8 Streamlit - Café Martins
# Dashboard V8: Carregamento ULTRA-RÁPIDO do MariaDB (10-50x mais rápido!)
# Integração Despesify (custos REAIS) + Autenticação
# PORTA 8502 (substituindo V7)

cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
exec streamlit run dashboard_v8.py --server.port=8502 --server.address=0.0.0.0 --server.headless=true
