#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Iniciando Dashboard V9 (Otimizado + Novadis) ===${NC}"

# Diretório base
BASE_DIR="/home/jorge/Documentos/Streamlit"
cd $BASE_DIR

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se as dependências estão instaladas
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "Instalando dependências..."
    pip install -r requirements.txt
fi

# Executar dashboard
echo -e "${GREEN}A iniciar aplicação...${NC}"
streamlit run dashboard_v9.py --server.port=8502 --server.address=0.0.0.0 --server.headless=true
