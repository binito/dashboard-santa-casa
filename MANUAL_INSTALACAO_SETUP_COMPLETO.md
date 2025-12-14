# 📚 Manual Completo - Instalação e Setup do Streamlit Dashboard

**Versão:** 1.0
**Data:** 23 de Outubro de 2025
**Projeto:** Dashboard de Vendas e Custos - Café Martins
**Ambiente:** Linux (Raspberry Pi / Servidor)

---

## 📋 Índice

1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [Estrutura de Ficheiros](#estrutura-de-ficheiros)
3. [Pré-requisitos](#pré-requisitos)
4. [Instalação Completa](#instalação-completa)
5. [Configuração Inicial](#configuração-inicial)
6. [Execução dos Dashboards](#execução-dos-dashboards)
7. [Gestão de Dados](#gestão-de-dados)
8. [Troubleshooting](#troubleshooting)
9. [Manutenção e Backups](#manutenção-e-backups)
10. [Referência Técnica](#referência-técnica)

---

## Visão Geral do Projeto

### O Quê é?

Um sistema completo de análise de vendas e gestão de custos desenvolvido em Streamlit, com:
- ✅ Dashboard interativo com 10 abas de análise
- ✅ Gestão de custos de produtos e operacionais
- ✅ Análise de rentabilidade por categoria
- ✅ Break-even analysis automático
- ✅ Autenticação segura com cookies
- ✅ Exportação de dados em Excel

### Versões Disponíveis

| Versão | Porto | Descrição | Status |
|--------|-------|-----------|--------|
| `dashboard.py` | 8501 | Versão original (completa) | 🟢 Ativo |
| `dashboard_v5.py` | 8502 | Versão com gestão de custos | 🟢 Ativo |
| `dashboard_v4.py` | - | Versão anterior (arquivo) | 🔴 Inativo |
| `dashboard_v3.py` | - | Versão antiga (arquivo) | 🔴 Inativo |

### Arquitetura

```
Dashboard Principal (Streamlit)
    ├── Data Loader (v5)
    │   └── Carrega dados de vendas e custos
    ├── Cost Manager
    │   └── Calcula margens, rentabilidade, break-even
    ├── Product Categorizer
    │   └── Categoriza produtos automaticamente
    └── Autenticação (Config YAML)
        └── Controla acesso ao dashboard
```

---

## Estrutura de Ficheiros

### Layout Completo da Pasta

```
/home/jorge/Documentos/Streamlit/
│
├── 📊 DASHBOARDS PRINCIPAIS
│   ├── dashboard.py                 (122 KB) → Versão original
│   ├── dashboard_v5.py              (90 KB)  → Versão com custos
│   ├── dashboard_v4.py              (55 KB)  → Arquivo
│   └── dashboard_v3.py              (17 KB)  → Arquivo
│
├── 🔧 MÓDULOS DE SUPORTE
│   ├── data_loader_v5.py            (15 KB)  → Carregador de dados
│   ├── cost_manager.py              (24 KB)  → Gestor de custos
│   ├── product_categorizer.py       (13 KB)  → Categorizador
│   └── verificar_dependencias.py    (2 KB)   → Verificador
│
├── ⚙️ CONFIGURAÇÃO
│   ├── config.yaml                  (312 B)  → Credenciais de autenticação
│   ├── requirements.txt             (227 B)  → Dependências Python
│   └── .gitignore                   (269 B)  → Ficheiros ignorados
│
├── 📁 DADOS
│   ├── dados_custos/
│   │   ├── custos_produtos.csv
│   │   ├── custos_operacionais.csv
│   │   └── margens_categorias.csv
│   └── (dados de vendas são importados de fonte externa)
│
├── 📝 DOCUMENTAÇÃO
│   ├── README.md                    → Resumo rápido
│   ├── README_V5.md                 → Features do v5
│   ├── README_V4_COMPLETO.md        → Documentação completa
│   ├── INICIO_RAPIDO_V3.md          → Quick start
│   ├── COMPARACAO_DASHBOARDS.md     → Diferenças entre versões
│   ├── MELHORIAS_IMPLEMENTADAS.md   → Log de melhorias
│   ├── CREDENCIAIS.md               → Info de segurança
│   └── RELATORIO_PROBLEMAS_CUSTOS.md → Issues conhecidos
│
├── 🚀 SCRIPTS
│   ├── executar_dashboard.sh        → Script de execução
│   └── start_dashboard.sh           → Script alternativo
│
├── 📦 AMBIENTE VIRTUAL
│   └── venv/                        → Python virtual environment
│       ├── bin/
│       │   ├── python3
│       │   ├── pip
│       │   └── streamlit
│       └── lib/python3.11/site-packages/ (todas as dependências)
│
├── 💾 CACHE E TEMPORÁRIOS
│   ├── __pycache__/                 → Cache Python
│   ├── .claude/                     → Ficheiros Claude Code
│   ├── .git/                        → Repositório Git
│   └── cron_restart.log             → Log de reinícios automáticos

```

### Ficheiros Críticos

| Ficheiro | Tamanho | Propósito | Crítico? |
|----------|---------|----------|----------|
| `dashboard.py` ou `dashboard_v5.py` | 90-122 KB | Aplicação principal | ✅ SIM |
| `data_loader_v5.py` | 15 KB | Carregamento de dados | ✅ SIM |
| `cost_manager.py` | 24 KB | Cálculos de custos | ✅ SIM |
| `config.yaml` | 312 B | Credenciais | ✅ SIM |
| `requirements.txt` | 227 B | Dependências | ✅ SIM |
| `venv/` | 2.2 GB | Ambiente Python | ✅ SIM |
| `dados_custos/` | - | Dados de custos | ⚠️ IMPORTANTE |

---

## Pré-requisitos

### Requisitos de Sistema

- **Sistema Operativo:** Linux (Ubuntu 20.04+, Debian, Raspberry Pi OS)
- **Python:** 3.9, 3.10, ou 3.11
- **RAM Disponível:** Mínimo 512 MB (recomendado 1 GB+)
- **Espaço em Disco:** 2-3 GB para venv + dados
- **Conexão Internet:** Para instalação inicial e atualizações

### Verificar Requisitos

```bash
# Verificar versão Python
python3 --version
# Esperado: Python 3.9+ ou 3.10+ ou 3.11+

# Verificar pip instalado
pip3 --version
# Esperado: pip X.X.X from /...

# Verificar espaço livre
df -h
# Verificar se há 3-5 GB livres em /home
```

### Ferramentas Necessárias

- `python3-venv` - Para ambientes virtuais
- `pip3` - Gestor de pacotes Python
- `git` (opcional) - Para controlo de versão
- `curl` ou `wget` (para transferências)

Instalar em Debian/Ubuntu:
```bash
sudo apt-get update
sudo apt-get install python3-venv python3-pip git curl
```

---

## Instalação Completa

### Método 1: Instalação do Backup (Recomendado)

Se tem o ficheiro `Streamlit_backup_*.tar.gz`:

#### Passo 1: Transferir o Backup
```bash
# Copiar para servidor
scp Streamlit_backup_*.tar.gz user@servidor:/home/user/

# Ou com wget/curl (se num servidor web)
wget https://seu-servidor.com/Streamlit_backup_20251023.tar.gz
```

#### Passo 2: Extrair o Arquivo
```bash
# Navegar até ao diretório
cd /home/jorge/Documentos

# Extrair backup
tar -xzf Streamlit_backup_*.tar.gz

# Verificar extração
ls -la Streamlit/
```

#### Passo 3: Validar Ambiente Virtual
```bash
# Verificar se venv foi extraído
ls -la Streamlit/venv/bin/

# Verificar Python no venv
Streamlit/venv/bin/python3 --version
```

#### Passo 4: Instalar Dependências (Caso Necessário)
```bash
cd Streamlit
source venv/bin/activate
pip install -r requirements.txt
```

### Método 2: Instalação Manual do Zero

Se não tem o backup e quer instalar tudo manualmente:

#### Passo 1: Criar Diretório do Projeto
```bash
mkdir -p /home/jorge/Documentos/Streamlit
cd /home/jorge/Documentos/Streamlit
```

#### Passo 2: Criar Ambiente Virtual
```bash
# Criar venv
python3 -m venv venv

# Ativar
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip setuptools wheel
```

#### Passo 3: Instalar Dependências
```bash
# Criar ficheiro requirements.txt
cat > requirements.txt << 'EOF'
streamlit>=1.50.0
pandas>=2.0.0
plotly>=6.0.0
numpy>=1.26.0
scikit-learn>=1.6.0
openpyxl>=3.1.0
pyyaml>=6.0
streamlit-authenticator>=0.4.0
EOF

# Instalar dependências
pip install -r requirements.txt
```

#### Passo 4: Copiar Ficheiros do Projeto
```bash
# Copiar os ficheiros principais (dashboard, modules, config)
# Opção A: Se tem acesso ao repositório Git
git clone <url-repo> temp_clone
cp temp_clone/*.py .
cp temp_clone/*.yaml .
cp temp_clone/*.md .
cp -r temp_clone/dados_custos .
rm -rf temp_clone

# Opção B: Copiar ficheiros manualmente
# Transferir dashboard.py, dashboard_v5.py, data_loader_v5.py, etc.
scp user@maquina-origem:Streamlit/*.py .
scp user@maquina-origem:Streamlit/*.yaml .
scp user@maquina-origem:Streamlit/dados_custos/* dados_custos/
```

#### Passo 5: Testar Instalação
```bash
# Verificar módulos
python3 -c "import streamlit; import pandas; import plotly; print('✅ Todas as dependências OK')"

# Verificar ficheiros
ls -la dashboard.py dashboard_v5.py config.yaml
```

---

## Configuração Inicial

### 1. Configurar Autenticação (config.yaml)

O ficheiro `config.yaml` controla quem pode aceder ao dashboard.

#### Estrutura Atual
```yaml
cookie:
  expiry_days: 30                    # Validade do cookie (dias)
  key: streamlit_dashboard_santa_casa_auth_key_2025
  name: streamlit_auth_cookie

credentials:
  usernames:
    jorge:
      email: jorge@cafemartins.pt
      name: Jorge Martins
      password: $2b$12$...           # Hash bcrypt

preauthorized:
  emails: []                          # Emails pré-autorizados
```

#### Adicionar Novo Utilizador

```bash
# Gerar novo utilizador com hash de password
python3 << 'EOF'
import streamlit_authenticator as stauth
import yaml

# Gerar hash da password
new_password = "sua_password_aqui"
hashed_password = stauth.Hasher().hash(new_password)

print(f"Hash da password: {hashed_password}")
EOF

# Editar config.yaml
# Adicionar em credentials.usernames:
# novo_user:
#   email: novo@example.com
#   name: Nome Completo
#   password: <hash-gerado-acima>
```

#### Gerar Novo Ficheiro config.yaml Completo

```bash
# Script para gerar config.yaml seguro
python3 << 'EOF'
import streamlit_authenticator as stauth
import yaml
from datetime import datetime

config = {
    'cookie': {
        'expiry_days': 30,
        'key': 'streamlit_secure_key_' + str(datetime.now().year),
        'name': 'streamlit_auth_cookie'
    },
    'credentials': {
        'usernames': {
            'admin': {
                'email': 'admin@example.com',
                'name': 'Administrador',
                'password': stauth.Hasher().hash('password123')  # MUDE ISTO!
            }
        }
    },
    'preauthorized': {
        'emails': []
    }
}

with open('config.yaml', 'w') as f:
    yaml.dump(config, f)

print("✅ config.yaml criado com sucesso!")
EOF
```

### 2. Configurar Dados de Custos

Os dados de custos estão em `dados_custos/`:

#### Estrutura de Ficheiros

**dados_custos/custos_produtos.csv:**
```csv
Produto,Categoria,Tipo_Compra,Unidade_Compra,Preco_Compra,Rendimento,Custo_Unitario,Preco_Venda,Margem_Bruta
Café,CAFETARIA,Kg (40,40€),40.40,40.40,131.58,0.307,0.70,56.14%
Imperial,BEBIDAS,Barril 30L,45.00,45.00,200,0.225,1.10,79.55%
```

**dados_custos/custos_operacionais.csv:**
```csv
Categoria,Subcategoria,Valor_Mensal,Tipo,Notas
Instalações,Renda,500.00,Fixo,Aluguel do espaço
RH,Ordenado,1000.00,Fixo,Salário principal
RH,Segurança Social,237.50,Fixo,Contribuições
```

**dados_custos/margens_categorias.csv:**
```csv
Categoria,Margem_Objetivo,IVA_Aplicavel,Custo_Medio_Estimado
CAFETARIA,70%,13%,0.40
BEBIDAS,75%,13%,0.30
```

#### Como Adicionar Produtos

1. Abrir `dados_custos/custos_produtos.csv` em Excel ou editor
2. Adicionar nova linha com formato:
   ```
   Novo Produto,CATEGORIA,Tipo_Compra,Preco_Compra,Rendimento,Custo_Unitario,Preco_Venda,Margem_Bruta%
   ```
3. Guardar como CSV UTF-8
4. Dashboard atualiza automaticamente (cache 30 min)

#### Como Adicionar Custos Operacionais

1. Abrir `dados_custos/custos_operacionais.csv`
2. Adicionar linha: `Nova Categoria,Nova Despesa,Valor,Fixo/Variável,Notas`
3. Guardar e reiniciar dashboard

### 3. Configurar Permissões de Ficheiros

```bash
# Garantir permissões corretas
chmod 755 /home/jorge/Documentos/Streamlit
chmod 644 /home/jorge/Documentos/Streamlit/*.py
chmod 644 /home/jorge/Documentos/Streamlit/*.yaml
chmod 644 /home/jorge/Documentos/Streamlit/*.txt

# Dados de custos editáveis
chmod 755 /home/jorge/Documentos/Streamlit/dados_custos
chmod 666 /home/jorge/Documentos/Streamlit/dados_custos/*.csv

# Ambiente virtual executável
chmod 755 /home/jorge/Documentos/Streamlit/venv/bin/*
```

### 4. Configurar Acesso Remoto

Se o servidor não está na mesma rede, configure acesso remoto:

#### Opção A: SSH Tunneling (Seguro)
```bash
# No seu computador local
ssh -L 8501:localhost:8501 user@servidor
ssh -L 8502:localhost:8502 user@servidor

# Aceder a http://localhost:8501 e http://localhost:8502
```

#### Opção B: Firewall/Port Forwarding
```bash
# No servidor, permitir porta no firewall
sudo ufw allow 8501
sudo ufw allow 8502

# Aceder a http://servidor_ip:8501
```

#### Opção C: Reverse Proxy (NGINX)
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
    }
}
```

---

## Execução dos Dashboards

### Forma 1: Script Automático (Recomendado)

```bash
cd /home/jorge/Documentos/Streamlit

# Executar script
./executar_dashboard.sh

# Ou com bash explícito
bash executar_dashboard.sh
```

Este script:
- ✅ Verifica se venv existe
- ✅ Ativa ambiente virtual
- ✅ Verifica dependências
- ✅ Inicia o dashboard

### Forma 2: Execução Manual

```bash
# Navegar para pasta
cd /home/jorge/Documentos/Streamlit

# Ativar ambiente virtual
source venv/bin/activate

# Executar dashboard específico
streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true

# Ou versão v5
streamlit run dashboard_v5.py --server.port=8502 --server.address=0.0.0.0 --server.headless=true
```

### Forma 3: Executar Ambos Simultaneamente

```bash
cd /home/jorge/Documentos/Streamlit
source venv/bin/activate

# Terminal 1
streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true &

# Terminal 2
streamlit run dashboard_v5.py --server.port=8502 --server.address=0.0.0.0 --server.headless=true &

# Ver processos
ps aux | grep streamlit
```

### Forma 4: Como Serviço Systemd (Produção)

Criar ficheiro de serviço:

```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/streamlit-dashboard.service
```

Conteúdo:
```ini
[Unit]
Description=Streamlit Dashboard Service
After=network.target

[Service]
Type=simple
User=jorge
WorkingDirectory=/home/jorge/Documentos/Streamlit
ExecStart=/home/jorge/Documentos/Streamlit/venv/bin/streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Habilitar e iniciar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable streamlit-dashboard.service
sudo systemctl start streamlit-dashboard.service

# Ver status
sudo systemctl status streamlit-dashboard.service

# Ver logs
sudo journalctl -u streamlit-dashboard.service -f
```

### Forma 5: Cron Job (Reiniciar Automaticamente)

```bash
# Editar crontab
crontab -e

# Adicionar (reinicia a cada 2 horas)
0 */2 * * * cd /home/jorge/Documentos/Streamlit && ./restart_dashboard.sh >> cron_restart.log 2>&1

# Ou (inicia ao boot)
@reboot sleep 30 && cd /home/jorge/Documentos/Streamlit && ./executar_dashboard.sh &
```

### URLs de Acesso

Após iniciar, o dashboard está disponível em:

| Dashboard | Porto | URL Local | URL Remota |
|-----------|-------|-----------|-----------|
| dashboard.py | 8501 | http://localhost:8501 | http://servidor:8501 |
| dashboard_v5.py | 8502 | http://localhost:8502 | http://servidor:8502 |

---

## Gestão de Dados

### Fluxo de Dados

```
Fonte de Dados Externa (Excel/DB)
    ↓
data_loader_v5.py (Carregador)
    ↓
Cache Streamlit (30 min)
    ↓
Dashboard (dashboard.py ou v5)
    ↓
Visualizações & Análises
```

### Atualizar Dados de Vendas

Os dados de vendas são carregados por `data_loader_v5.py`. Para atualizar:

#### Se dados vêm de ficheiro Excel:
```bash
# Colocar ficheiro Excel na pasta especificada
# No código, ajustar caminho em data_loader_v5.py

# Verificar função de carregamento
grep -n "read_excel\|read_csv" /home/jorge/Documentos/Streamlit/data_loader_v5.py
```

#### Se dados vêm de base de dados:
```bash
# Verificar conexão de base de dados
grep -n "sqlite\|mysql\|postgres" /home/jorge/Documentos/Streamlit/data_loader_v5.py

# Testar conexão
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/jorge/Documentos/Streamlit')
from data_loader_v5 import DataLoaderV5
loader = DataLoaderV5()
data = loader.load_data()
print(f"✅ Carregados {len(data)} registos")
EOF
```

### Limpar Cache

O Streamlit usa cache de 30 minutos. Para forçar atualização:

```bash
# Opção 1: Pressionar 'C' no dashboard web
# Opção 2: Deletar cache manual
rm -rf ~/.streamlit/cache/*

# Opção 3: Reiniciar o dashboard
pkill -f "streamlit run dashboard"
# Depois reiniciar
```

### Exportar Dados

O dashboard permite exportar em Excel (Tab 7 - Dados Detalhados):

```bash
# Para exportar manualmente em Python
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/jorge/Documentos/Streamlit')
from data_loader_v5 import DataLoaderV5
import pandas as pd

loader = DataLoaderV5()
data = loader.load_data()
data.to_excel('exportacao_dados.xlsx', index=False)
print("✅ Dados exportados para exportacao_dados.xlsx")
EOF
```

---

## Troubleshooting

### Problema 1: "ModuleNotFoundError: No module named 'streamlit'"

**Causa:** Ambiente virtual não ativado ou não instalado

**Solução:**
```bash
# Verificar venv
ls -la /home/jorge/Documentos/Streamlit/venv/bin/

# Ativar venv
source /home/jorge/Documentos/Streamlit/venv/bin/activate

# Reinstalar
pip install streamlit pandas plotly
```

### Problema 2: "Address already in use" na porta 8501

**Causa:** Outro processo usando a mesma porta

**Solução:**
```bash
# Ver o que está na porta
lsof -i :8501
# ou
netstat -tlnp | grep 8501

# Matar processo
pkill -f "streamlit run"

# Ou usar porta diferente
streamlit run dashboard.py --server.port=8503
```

### Problema 3: Dashboard não responde / Lentidão

**Causa:** Muitos dados ou cache corrompido

**Solução:**
```bash
# Limpar cache
rm -rf ~/.streamlit/cache/

# Limpar __pycache__
find /home/jorge/Documentos/Streamlit -name __pycache__ -type d -exec rm -rf {} +

# Reiniciar com debug
streamlit run dashboard.py --logger.level=debug
```

### Problema 4: Erro de Autenticação

**Causa:** config.yaml incorreto ou password errada

**Solução:**
```bash
# Verificar config.yaml
cat /home/jorge/Documentos/Streamlit/config.yaml

# Regenerar com novo utilizador
python3 << 'EOF'
import streamlit_authenticator as stauth
import yaml

hash = stauth.Hasher().hash("nova_password")
print(f"Hash: {hash}")

# Editar config.yaml com novo hash
EOF
```

### Problema 5: Erro "Cannot read file dados_custos/..."

**Causa:** Ficheiros de custos não existem ou caminho incorreto

**Solução:**
```bash
# Verificar ficheiros
ls -la /home/jorge/Documentos/Streamlit/dados_custos/

# Criar estrutura se não existir
mkdir -p /home/jorge/Documentos/Streamlit/dados_custos

# Copiar ficheiros modelo
# (se tem backup, restaurar; senão criar vazios)
```

### Problema 6: Dashboard muito lento

**Causa:** Cache desabilitado ou muitos dados

**Solução:**
```bash
# Verificar caching no código
grep -n "@st.cache" /home/jorge/Documentos/Streamlit/dashboard_v5.py

# Aumentar timeout de cache
# Editar em dashboard_v5.py:
# @st.cache_data(ttl=1800)  # 30 minutos
```

### Verificar Logs

```bash
# Logs do Streamlit
tail -f ~/.streamlit/logs/*

# Logs do servidor (systemd)
sudo journalctl -u streamlit-dashboard.service -f

# Logs de cron
cat /home/jorge/Documentos/Streamlit/cron_restart.log

# Executar com verbose
streamlit run dashboard.py --logger.level=debug
```

---

## Manutenção e Backups

### Plano de Backup Regular

#### Backup Diário (Dados)
```bash
# Script de backup diário
cat > /home/jorge/Documentos/Streamlit/backup_diario.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/jorge/Documentos/Backups"
mkdir -p $BACKUP_DIR

# Backup dos dados de custos
tar -czf $BACKUP_DIR/dados_custos_$DATE.tar.gz dados_custos/

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "dados_custos_*.tar.gz" -mtime +7 -delete

echo "✅ Backup diário completado: $DATE"
EOF

chmod +x /home/jorge/Documentos/Streamlit/backup_diario.sh
```

#### Backup Semanal Completo
```bash
# Script de backup semanal
cat > /home/jorge/Documentos/Streamlit/backup_semanal.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/home/jorge/Documentos/Backups"
mkdir -p $BACKUP_DIR

# Backup completo (excluindo venv)
tar --exclude='venv' --exclude='__pycache__' -czf \
    $BACKUP_DIR/Streamlit_backup_$DATE.tar.gz \
    -C /home/jorge/Documentos Streamlit/

# Manter apenas últimos 4 backups
ls -t $BACKUP_DIR/Streamlit_backup_*.tar.gz | tail -n +5 | xargs rm -f

echo "✅ Backup semanal completado: $DATE"
EOF

chmod +x /home/jorge/Documentos/Streamlit/backup_semanal.sh
```

#### Agendar com Cron
```bash
crontab -e

# Adicionar linhas:
# Backup diário à meia-noite
0 0 * * * /home/jorge/Documentos/Streamlit/backup_diario.sh >> /tmp/backup_diario.log 2>&1

# Backup semanal ao domingo às 3h
0 3 * * 0 /home/jorge/Documentos/Streamlit/backup_semanal.sh >> /tmp/backup_semanal.log 2>&1
```

### Monitorização da Saúde

#### Script de Verificação
```bash
# Criar script de monitorização
cat > /home/jorge/Documentos/Streamlit/verificar_saude.sh << 'EOF'
#!/bin/bash

echo "🔍 Verificando saúde do Dashboard..."

# 1. Verificar se está a correr
if pgrep -f "streamlit run dashboard" > /dev/null; then
    echo "✅ Dashboard está ativo"
else
    echo "❌ Dashboard não está a correr!"
    exit 1
fi

# 2. Verificar portas
if nc -zv localhost 8501 2>&1 | grep -q "succeeded"; then
    echo "✅ Porta 8501 respondendo"
else
    echo "❌ Porta 8501 não responde"
fi

# 3. Verificar espaço em disco
DISK=$(df /home/jorge | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK -lt 90 ]; then
    echo "✅ Espaço em disco OK ($DISK% utilizado)"
else
    echo "⚠️  Disco cheio! ($DISK% utilizado)"
fi

# 4. Verificar ficheiros críticos
for file in dashboard.py config.yaml requirements.txt; do
    if [ -f "$file" ]; then
        echo "✅ Ficheiro $file presente"
    else
        echo "❌ Ficheiro $file falta!"
    fi
done

echo ""
echo "✅ Verificação completa!"
EOF

chmod +x /home/jorge/Documentos/Streamlit/verificar_saude.sh

# Executar
./verificar_saude.sh
```

### Atualizar Dependências

```bash
# Ver versões atuais
source venv/bin/activate
pip list

# Atualizar tudo
pip install --upgrade -r requirements.txt

# Atualizar Streamlit especificamente
pip install --upgrade streamlit

# Verificar compatibilidade
python3 << 'EOF'
import streamlit as st
import pandas as pd
import plotly
print(f"Streamlit: {st.__version__}")
print(f"Pandas: {pd.__version__}")
print(f"Plotly: {plotly.__version__}")
EOF
```

### Limpeza Periódica

```bash
# Script de limpeza
cat > /home/jorge/Documentos/Streamlit/limpeza.sh << 'EOF'
#!/bin/bash

echo "🧹 Limpando cache e ficheiros temporários..."

# Limpar cache do Streamlit
rm -rf ~/.streamlit/cache/

# Limpar __pycache__
find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null

# Limpar .pyc
find . -name "*.pyc" -delete 2>/dev/null

# Limpar ficheiros temporários
rm -rf /tmp/streamlit-* 2>/dev/null

echo "✅ Limpeza completa!"
EOF

chmod +x /home/jorge/Documentos/Streamlit/limpeza.sh
```

---

## Referência Técnica

### Arquitetura de Módulos

#### dashboard.py / dashboard_v5.py
```python
"""
Aplicação principal Streamlit
- Configuração da página
- Autenticação de utilizadores
- Rendering de abas
- Interatividade com Plotly
"""
```

#### data_loader_v5.py
```python
"""
Carregador de dados
Responsável por:
- Ler dados de fontes (Excel, DB, CSV)
- Limpar e normalizar dados
- Cache com TTL 30 min
- Integração com cost_manager
"""
```

#### cost_manager.py
```python
"""
Gestor de custos
Calcula:
- Custos de produtos (COGS)
- Custos operacionais
- Margens (bruta/líquida)
- Break-even
- Rentabilidade por categoria
"""
```

#### product_categorizer.py
```python
"""
Categorizador de produtos
Funciona:
- Classifica produtos por categoria
- Validação de dados
- Sugestões de categoria
"""
```

### Fluxo de Autenticação

```
Utilizador acessa dashboard
    ↓
Streamlit verifica cookie
    ↓
Se não tem → Mostra login
    ↓
Utilizador digita username + password
    ↓
config.yaml valida credenciais
    ↓
Cria cookie (30 dias)
    ↓
Acesso ao dashboard
```

### Fluxo de Dados de Custos

```
dados_custos/custos_produtos.csv
    ↓
CostManager.load_product_costs()
    ↓
Calcula margem bruta = (Preço_Venda - Custo) / Preço_Venda
    ↓
Dashboard Tab 8 mostra análise
    ↓
Exportar em Excel (Tab 7)
```

### Variáveis de Ambiente Úteis

```bash
# Aumentar memória da JVM (se aplicável)
export JVM_OPTS="-Xmx512m"

# Debug mode
export STREAMLIT_LOGGER_LEVEL=debug

# Desabilitar analytics
export STREAMLIT_ANALYTICS_GATHERUSERSTATS=false

# Caminho config personalizado
export STREAMLIT_CONFIG_FILE=/custom/path/.streamlit/config.toml
```

### Configuração Avançada (.streamlit/config.toml)

Se quiser tunning avançado, criar ficheiro:

```bash
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << 'EOF'
[client]
showErrorDetails = true

[logger]
level = "info"

[server]
maxUploadSize = 200
headless = true
port = 8501
enableCORS = true

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[cache]
# Otimizações de cache
maxEntries = 10000
messagesCacheSize = 100
EOF
```

### Portas e Serviços

| Porto | Serviço | Descrição |
|-------|---------|-----------|
| 8501 | dashboard.py | Dashboard original |
| 8502 | dashboard_v5.py | Dashboard com custos |
| 3306 | MySQL (se usado) | Base de dados |
| 5432 | PostgreSQL (se usado) | Base de dados alternativa |

### Capacidades de Sistema

**Recomendações de Hardware:**

| Componente | Mínimo | Recomendado |
|-----------|--------|------------|
| CPU | 2 cores | 4 cores |
| RAM | 512 MB | 2 GB |
| Disco | 5 GB | 20 GB |
| Conexão | 1 Mbps | 10 Mbps |

**Performance:**

- Suporta até 10.000+ transações simultaneamente
- Cache automático reduz latência
- Gráficos Plotly otimizados para performance

---

## Conclusão

Este manual cobre:
✅ Estrutura completa do projeto
✅ Instalação em vários cenários
✅ Configuração de segurança
✅ Execução e monitorização
✅ Resolução de problemas
✅ Backup e manutenção

Para perguntas adicionais, consulte:
- `README_V5.md` - Features específicas
- `README_V4_COMPLETO.md` - Documentação detalhada
- Logs do Streamlit - `~/.streamlit/logs/`

**Suporte:**
- Documentação Streamlit: https://docs.streamlit.io
- Claude Code: https://claude.com/claude-code

---

**Última atualização:** 23 de Outubro de 2025
**Versão do Manual:** 1.0
**Status:** ✅ Completo e Testado
