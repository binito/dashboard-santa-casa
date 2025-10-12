#!/bin/bash
# Script para executar o Dashboard de Vendas - Santa Casa
# Automaticamente ativa o ambiente virtual e executa o Streamlit

cd /home/jorge/Documentos/Streamlit

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    pip install streamlit pandas plotly numpy scikit-learn openpyxl pyyaml streamlit-authenticator
else
    echo "✅ Ambiente virtual encontrado"
    source venv/bin/activate
fi

# Verificar dependências
echo ""
echo "🔍 Verificando dependências..."
python verificar_dependencias.py

# Se verificação passou, executar dashboard
if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Iniciando Dashboard..."
    echo "================================================"
    echo "📊 Dashboard de Vendas - Santa Casa"
    echo "🌐 Abrindo no navegador..."
    echo "================================================"
    echo ""
    streamlit run dashboard.py
else
    echo ""
    echo "❌ Erro: Algumas dependências estão faltando"
    echo "Execute: source venv/bin/activate && pip install -r requirements.txt"
fi
