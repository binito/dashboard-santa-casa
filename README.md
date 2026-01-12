# 📊 Dashboards Café Martins - Sistema Completo

> Suite profissional de dashboards para análise de vendas do Café Martins e Jogos Santa Casa da Misericórdia.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-red.svg)
![MariaDB](https://img.shields.io/badge/MariaDB-10.5+-orange.svg)
![Status](https://img.shields.io/badge/Status-Produção-success.svg)

---

## 🎯 Visão Geral

Este repositório contém dois dashboards profissionais complementares:

### 🎲 Dashboard Santa Casa
**Análise completa de Jogos da Santa Casa da Misericórdia**
- 11 páginas de análise especializada
- Sistema de objetivos com previsões
- Comparações MoM, YoY e WoW
- Gestão de prémios e prestação de contas

📖 **[Ver documentação completa →](README_DASHBOARD_SANTA_CASA.md)**

### 🚀 Dashboard v8 (POS + Santa Casa)
**Dashboard ultra-rápido com MariaDB e custos reais**
- Integração MariaDB (10-50x mais rápido)
- Custos REAIS via Despesify
- 12 tabs de análise POS
- 8 tabs de Jogos Santa Casa integradas

📖 **[Ver documentação completa →](README_DASHBOARD_V8.md)**

---

## 🚀 Início Rápido

### Dashboard Santa Casa (Porta 8503)

```bash
cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
streamlit run dashboard_santa_casa.py --server.port 8503
```

**Acesso:** http://localhost:8503 ou https://app.cafemartins.pt

### Dashboard v8 (Porta 8502)

```bash
cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
streamlit run dashboard_v8.py --server.port 8502
```

**Acesso:** http://localhost:8502 ou https://dashboard.cafemartins.pt

---

## 📦 Instalação

### 1. Pré-requisitos

- Python 3.11+
- MariaDB 10.5+ (apenas para Dashboard v8)
- pip (gerenciador de pacotes)

### 2. Clonar/Acessar Repositório

```bash
cd /home/jorge/Documentos/Streamlit
```

### 3. Ambiente Virtual

```bash
# Criar (se não existir)
python3 -m venv venv

# Ativar
source venv/bin/activate
```

### 4. Instalar Dependências

```bash
# Dependências base
pip install streamlit pandas plotly numpy

# Autenticação
pip install streamlit-authenticator pyyaml

# Exportação Excel
pip install openpyxl

# MariaDB (apenas para v8)
pip install mysql-connector-python

# Despesify API (apenas para v8)
pip install requests
```

Ou via requirements.txt:
```bash
pip install -r requirements.txt
```

---

## 🗂️ Estrutura do Projeto

```
/home/jorge/Documentos/Streamlit/
├── 📊 Dashboards Principais
│   ├── dashboard_santa_casa.py          # Dashboard Santa Casa (porta 8503)
│   └── dashboard_v8.py                  # Dashboard v8 MariaDB (porta 8502)
│
├── 📚 Módulos de Suporte
│   ├── data_loader_v8.py                # Carregador MariaDB
│   ├── cost_manager_v2.py               # Gestão de custos + Despesify
│   └── product_categorizer.py           # Categorizador de produtos
│
├── ⚙️ Configuração
│   ├── config.yaml                      # Autenticação
│   ├── objetivos_semanais.json          # Objetivos Santa Casa
│   └── custos_estimados.json            # Custos estimados (fallback)
│
├── 📖 Documentação
│   ├── README.md                        # Este ficheiro
│   ├── README_DASHBOARD_SANTA_CASA.md   # Doc Dashboard Santa Casa
│   └── README_DASHBOARD_V8.md           # Doc Dashboard v8
│
├── 🐍 Ambiente Python
│   └── venv/                            # Ambiente virtual
│
└── 🗄️ Dados
    └── ../Santa casa/dados/
        └── dados_extracao.txt           # Dados Santa Casa
```

---

## 🔑 Funcionalidades Comparadas

| Funcionalidade | Dashboard Santa Casa | Dashboard v8 |
|----------------|----------------------|--------------|
| **Dados POS Café** | ❌ | ✅ MariaDB |
| **Jogos Santa Casa** | ✅ Completo (11 páginas) | ✅ Integrado (8 tabs) |
| **Custos REAIS** | ❌ | ✅ Despesify |
| **Custos Estimados** | ❌ | ✅ Editável |
| **Performance** | Rápido | Ultra-rápido (10-50x) |
| **Objetivos** | ✅ Sistema avançado | ✅ Básico |
| **Prestação de Contas** | ✅ Dedicada | ❌ |
| **Análise Semanal WoW** | ✅ | ✅ |
| **Comparações MoM/YoY** | ✅ | ✅ |
| **Heatmaps** | ✅ | ✅ |
| **Exportação Excel** | ✅ | ✅ Profissional |
| **Autenticação** | ✅ | ✅ |

---

## 🎯 Qual Dashboard Usar?

### Use Dashboard Santa Casa quando:
- ✅ Foco exclusivo em **Jogos Santa Casa**
- ✅ Necessitar de **prestação de contas** detalhada
- ✅ Quiser **sistema avançado de objetivos**
- ✅ Precisar de **análise semanal profunda** (WoW)
- ✅ Não necessitar de dados do POS

### Use Dashboard v8 quando:
- ✅ Necessitar **análise completa POS + Santa Casa**
- ✅ Quiser **performance ultra-rápida** (MariaDB)
- ✅ Precisar de **custos REAIS** (Despesify)
- ✅ Necessitar de **gestão de custos** editável
- ✅ Quiser **visão unificada do negócio**

---

## ⚙️ Configuração de Produção

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/dashboards-cafe-martins

# Dashboard Santa Casa (8503)
server {
    listen 80;
    server_name app.cafemartins.pt;

    location / {
        proxy_pass http://localhost:8503;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}

# Dashboard v8 (8502)
server {
    listen 80;
    server_name dashboard.cafemartins.pt;

    location / {
        proxy_pass http://localhost:8502;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### Systemd Services

#### Dashboard Santa Casa

```ini
# /etc/systemd/system/streamlit-santa-casa.service
[Unit]
Description=Dashboard Santa Casa Streamlit
After=network.target

[Service]
Type=simple
User=jorge
WorkingDirectory=/home/jorge/Documentos/Streamlit
ExecStart=/home/jorge/Documentos/Streamlit/venv/bin/streamlit run dashboard_santa_casa.py --server.port 8503 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Dashboard v8

```ini
# /etc/systemd/system/streamlit-v8.service
[Unit]
Description=Dashboard v8 Streamlit
After=network.target mariadb.service

[Service]
Type=simple
User=jorge
WorkingDirectory=/home/jorge/Documentos/Streamlit
ExecStart=/home/jorge/Documentos/Streamlit/venv/bin/streamlit run dashboard_v8.py --server.port 8502 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
```

### Ativar Serviços

```bash
# Dashboard Santa Casa
sudo systemctl enable streamlit-santa-casa
sudo systemctl start streamlit-santa-casa

# Dashboard v8
sudo systemctl enable streamlit-v8
sudo systemctl start streamlit-v8

# Verificar status
sudo systemctl status streamlit-santa-casa
sudo systemctl status streamlit-v8
```

---

## 🔧 Gestão dos Serviços

### Comandos Úteis

```bash
# Ver status de ambos
sudo systemctl status streamlit-santa-casa streamlit-v8

# Reiniciar
sudo systemctl restart streamlit-santa-casa
sudo systemctl restart streamlit-v8

# Ver logs
sudo journalctl -u streamlit-santa-casa -f
sudo journalctl -u streamlit-v8 -f

# Parar temporariamente
sudo systemctl stop streamlit-santa-casa
sudo systemctl stop streamlit-v8
```

### Parar Manualmente (sem systemd)

```bash
# Matar todos os processos Streamlit
pkill -f "streamlit run"

# Ou individualmente
pkill -f "streamlit run dashboard_santa_casa.py"
pkill -f "streamlit run dashboard_v8.py"

# Verificar portas
lsof -i :8502
lsof -i :8503
```

---

## 🗄️ Dados

### Jogos Santa Casa

**Localização:** `/home/jorge/Documentos/Santa casa/dados/dados_extracao.txt`

**Formato:** TSV (Tab Separated Values)

**Colunas:**
- Data (YYYY-MM-DD)
- Categoria
- Jogo
- Vendas ilíquidas (€)
- Remunerações (€)
- Prémios (€)
- Valor (€)
- Jogo Rececionado
- Qt Maços

### POS (Apenas v8)

**Localização:** MariaDB (`cafe_martins.pos_vendas`)

**Atualização:** Scripts cron diários (02:00)

**Queries:** Ver `data_loader_v8.py`

---

## 🐛 Troubleshooting

### Dashboard não inicia

```bash
# Verificar processos
ps aux | grep streamlit

# Verificar portas
lsof -i :8502
lsof -i :8503

# Limpar processos
pkill -f streamlit

# Tentar iniciar manualmente
cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
streamlit run dashboard_santa_casa.py --server.port 8503
```

### Erro "Module not found"

```bash
# Ativar ambiente
source venv/bin/activate

# Reinstalar dependências
pip install -r requirements.txt
```

### Dashboard lento

```bash
# Limpar cache Streamlit
rm -rf ~/.streamlit/cache

# Reiniciar serviços
sudo systemctl restart streamlit-santa-casa streamlit-v8
```

### MariaDB não conecta (v8)

```bash
# Verificar MariaDB
sudo systemctl status mariadb
sudo systemctl start mariadb

# Testar conexão
mysql -u usuario -p -h localhost
```

### Dados não atualizam

```bash
# Santa Casa: verificar arquivo
ls -la "/home/jorge/Documentos/Santa casa/dados/dados_extracao.txt"

# POS (v8): verificar cron
crontab -l | grep mariadb

# Limpar cache e reiniciar
pkill -f streamlit
cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
streamlit run dashboard_santa_casa.py --server.port 8503
```

---

## 📊 Atualização de Dados

### Dados Santa Casa (Manual)

1. Exportar dados do sistema Santa Casa
2. Substituir arquivo em:
   ```
   /home/jorge/Documentos/Santa casa/dados/dados_extracao.txt
   ```
3. Clicar **🔄 Reset Total** no dashboard
4. Ou reiniciar serviço:
   ```bash
   sudo systemctl restart streamlit-santa-casa
   ```

### Dados POS (Automático - v8)

Scripts cron executam diariamente às 02:00:
```bash
# Ver configuração
crontab -l

# Forçar atualização manual
python3 /caminho/para/sync_to_mariadb.py
```

---

## 📈 Performance

### Benchmarks

| Métrica | Dashboard Santa Casa | Dashboard v8 |
|---------|----------------------|--------------|
| Tempo de load | ~5-8s | ~2-3s |
| Uso de memória | ~400MB | ~350MB |
| Filtro por data | ~1s | ~0.5s |
| Mudança de página | Instantâneo | Instantâneo |
| Exportação Excel | ~5s | ~4s |

---

## 🔐 Segurança

- ✅ Autenticação via `streamlit-authenticator`
- ✅ Senhas com hash bcrypt
- ✅ Sessões com timeout configurável
- ✅ HTTPS via Nginx (em produção)
- ✅ Credenciais MariaDB protegidas
- ✅ API keys em variáveis de ambiente

### Configuração de Autenticação

Edite `config.yaml`:
```yaml
credentials:
  usernames:
    admin:
      email: admin@cafemartins.pt
      name: Administrador
      password: $2b$12$...  # Hash bcrypt
cookie:
  expiry_days: 30
  key: chave_aleatoria_segura
  name: streamlit_auth
```

Gerar hash de senha:
```python
import streamlit_authenticator as stauth
hashed = stauth.Hasher(['minhasenha']).generate()
print(hashed[0])
```

---

## 📞 Suporte

### Documentação Detalhada

- 📖 [README Dashboard Santa Casa](README_DASHBOARD_SANTA_CASA.md)
- 📖 [README Dashboard v8](README_DASHBOARD_V8.md)

### Logs

```bash
# Logs Streamlit
tail -f ~/.streamlit/logs/streamlit.log

# Logs systemd
sudo journalctl -u streamlit-santa-casa -n 100
sudo journalctl -u streamlit-v8 -n 100

# Logs MariaDB (v8)
sudo tail -f /var/log/mysql/error.log
```

### Contacto

Para questões ou problemas:
1. Consultar documentação específica
2. Verificar logs
3. Consultar seção Troubleshooting
4. Contactar administrador do sistema

---

## 📝 Changelog

### Janeiro 2026

**Dashboard Santa Casa:**
- ✅ Formato de moeda português (X€)
- ✅ Renomeação "Valor Líquido" → "💎 Total Prestações"
- ✅ Keys únicas em gráficos Plotly
- ✅ Melhoria cálculo SWLY (semanas ISO)
- ✅ Performance mensal por ciclos semanais

**Dashboard v8:**
- ✅ Integração MariaDB (10-50x mais rápido)
- ✅ Custos REAIS via Despesify
- ✅ Editor de custos estimados
- ✅ 12 tabs análise POS
- ✅ 8 tabs Jogos Santa Casa

**Documentação:**
- ✅ README principal atualizado
- ✅ README Dashboard Santa Casa criado
- ✅ README Dashboard v8 criado

---

## 🛠️ Tecnologias

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.11+ | Linguagem base |
| Streamlit | 1.50+ | Framework web |
| Pandas | 2.3+ | Manipulação de dados |
| Plotly | 6.3+ | Gráficos interativos |
| MariaDB | 10.5+ | Banco de dados (v8) |
| NumPy | Latest | Cálculos numéricos |
| OpenPyXL | 3.1+ | Exportação Excel |
| Streamlit-Authenticator | Latest | Autenticação |
| PyYAML | Latest | Configuração |
| Requests | Latest | API Despesify (v8) |

---

## 📄 Licença

Este projeto é de uso interno do Café Martins. Todos os direitos reservados.

---

## 🎯 Roadmap

### Próximas Funcionalidades

- [ ] Dashboard móvel responsivo
- [ ] Notificações push de alertas
- [ ] Integração WhatsApp para relatórios
- [ ] Machine Learning para previsões avançadas
- [ ] API REST para integração com outros sistemas
- [ ] Dashboard em tempo real (WebSocket)
- [ ] App mobile nativo (Flutter)

---

**Desenvolvido com ❤️ para o Café Martins**

**Powered by:**
- 🐍 Python
- 🎈 Streamlit
- 📊 Plotly
- 🗄️ MariaDB
- 💰 Despesify
