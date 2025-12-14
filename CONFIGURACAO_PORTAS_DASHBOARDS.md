# Configuração dos Dashboards - Café Martins

## 📊 Dashboards Ativos

### 1️⃣ Dashboard Original (Santa Casa)
- **Porta:** 8501
- **URL Interna:** http://localhost:8501
- **URL Pública:** https://app.cafemartins.pt
- **Ficheiro:** `dashboard_santa_casa.py`
- **Script Início:** `start_dashboard.sh`
- **Nginx Config:** `/etc/nginx/sites-available/streamlit`
- **Autenticação:** ✅ Sim (config.yaml)
- **Descrição:** Dashboard original com dados Santa Casa
- **Status:** 🟢 Ativo (PID 989)

---

### 2️⃣ Dashboard v7 (Integração Despesify)
- **Porta:** 8502
- **URL Interna:** http://localhost:8502
- **URL Pública:** https://app2.cafemartins.pt
- **Ficheiro:** `dashboard_v7.py`
- **Script Início:** `start_dashboard_v7.sh`
- **Nginx Config:** `/etc/nginx/sites-available/streamlit-v4`
- **Autenticação:** ✅ Sim (config.yaml)
- **Descrição:** Dashboard v7 com custos REAIS do Despesify + Editor de Custos
- **Status:** 🟢 Ativo (PID 40926)

**Funcionalidades Exclusivas v7:**
- ✅ Integração MariaDB (Despesify)
- ✅ Custos Operacionais REAIS (desde 1/12/2025)
- ✅ Sistema Híbrido (REAL + ESTIMADO)
- ✅ Editor de Custos Operacionais
- ✅ Tabela de Fornecedores (todas as despesas)
- ✅ Top 10 Fornecedores
- ✅ Separação automática: Produtos vs Operacionais

---

## 🔐 Autenticação

**Ficheiro:** `config.yaml`

**Credenciais:**
- **Utilizador:** jorge
- **Email:** jorge@cafemartins.pt
- **Password:** [hash bcrypt]

**Cookie:**
- Nome: `streamlit_auth_cookie`
- Validade: 30 dias
- Chave: `streamlit_dashboard_santa_casa_auth_key_2025`

---

## 🌐 Configuração Nginx

### app.cafemartins.pt (Porta 8501)
```nginx
server {
    listen 443 ssl http2;
    server_name app.cafemartins.pt;

    location / {
        proxy_pass http://127.0.0.1:8501;
        # ... headers websocket ...
    }
}
```

### app2.cafemartins.pt (Porta 8502)
```nginx
server {
    listen 443 ssl http2;
    server_name app2.cafemartins.pt;

    location / {
        proxy_pass http://127.0.0.1:8502;
        # ... headers websocket ...
    }
}
```

**Certificados SSL:** Wildcard `*.cafemartins.pt` (Let's Encrypt)

---

## 🚀 Inicialização

### Iniciar Dashboard v7 (Porta 8502)
```bash
cd /home/jorge/Documentos/Streamlit
./start_dashboard_v7.sh
```

ou

```bash
nohup /home/jorge/Documentos/Streamlit/venv/bin/streamlit run dashboard_v7.py \
  --server.port 8502 \
  --server.headless true > dashboard_v7_8502.log 2>&1 &
```

### Parar Dashboard v7
```bash
lsof -ti:8502 | xargs -r kill -9
```

### Ver Log
```bash
tail -f dashboard_v7_8502.log
```

---

## 📦 Dependências

### Python (venv)
- streamlit
- pandas
- plotly
- mysql-connector-python ⭐ (NOVO - para Despesify)
- streamlit-authenticator
- pyyaml
- bcrypt

### Base de Dados
- **MariaDB:** despesify
  - Host: localhost
  - User: root
  - Password: cathie
  - Tabelas: expenses, categories

---

## 🔧 Manutenção

### Reiniciar Serviços
```bash
# Parar todos os dashboards
lsof -ti:8501,8502 | xargs -r kill -9

# Iniciar Dashboard Original (8501)
cd /home/jorge/Documentos/Streamlit
./start_dashboard.sh &

# Iniciar Dashboard v7 (8502)
cd /home/jorge/Documentos/Streamlit
./start_dashboard_v7.sh &

# Reiniciar Nginx
sudo systemctl restart nginx
```

### Verificar Status
```bash
# Ver processos Streamlit
ps aux | grep streamlit

# Ver portas ocupadas
lsof -i:8501
lsof -i:8502

# Testar URLs
curl -I http://localhost:8501
curl -I http://localhost:8502
```

### Logs
```bash
# Dashboard Original
tail -f /home/jorge/Documentos/Streamlit/nohup.out

# Dashboard v7
tail -f /home/jorge/Documentos/Streamlit/dashboard_v7_8502.log

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 📋 Checklist de Verificação

Após restart do servidor:

- [ ] Dashboard Original (8501) está ativo?
- [ ] Dashboard v7 (8502) está ativo?
- [ ] Nginx está a correr?
- [ ] app.cafemartins.pt acessível?
- [ ] app2.cafemartins.pt acessível?
- [ ] Autenticação funciona?
- [ ] MariaDB está a correr?
- [ ] Despesify acessível?

---

## 🆘 Troubleshooting

### Problema: Dashboard não inicia
```bash
# Verificar log
tail -30 dashboard_v7_8502.log

# Verificar porta ocupada
lsof -i:8502

# Verificar permissões
ls -la dashboard_v7.py
chmod +x start_dashboard_v7.sh
```

### Problema: "Module not found: mysql"
```bash
# Instalar no venv
source venv/bin/activate
pip install mysql-connector-python
```

### Problema: Erro de autenticação
```bash
# Verificar config.yaml
cat config.yaml

# Regenerar password hash (se necessário)
python3 -c "import bcrypt; print(bcrypt.hashpw('sua_password'.encode(), bcrypt.gensalt()).decode())"
```

### Problema: Não conecta ao Despesify
```bash
# Testar conexão MariaDB
mysql -u root -pcathie -e "USE despesify; SELECT COUNT(*) FROM expenses;"

# Verificar serviço MariaDB
sudo systemctl status mariadb
```

---

## 📊 Comparação v6 vs v7

| Feature | v6 | v7 |
|---------|----|----|
| **Porta** | 8502 (antes) | 8502 (agora) |
| **Custos Operacionais** | CSV Estimados | **REAIS (Despesify)** ✅ |
| **Editor de Custos** | ❌ Não | **✅ Sim** |
| **Fornecedores** | ❌ Não | **✅ Tabela Completa** |
| **Integração DB** | ❌ Não | **✅ MariaDB** |
| **Autenticação** | ✅ Sim | ✅ Sim |
| **Rastreabilidade** | ❌ Não | **✅ NIF + Faturas** |

---

## 📅 Histórico de Alterações

### 2025-12-08
- ✅ Substituído v6 por v7 na porta 8502
- ✅ Adicionada integração Despesify
- ✅ Criado editor de custos operacionais
- ✅ Adicionada tabela de fornecedores
- ✅ Mantida autenticação com config.yaml
- ✅ Criado script `start_dashboard_v7.sh`

---

## 📞 Suporte

**Desenvolvido para:** Café Martins
**Data Implementação:** 08/12/2025
**Versão Dashboard:** v7.0.0 (Despesify Integration)

**Stack:**
- Streamlit 1.30+
- Plotly 5.18+
- MariaDB 10.5+
- Python 3.11
- Nginx 1.18+
- Let's Encrypt SSL

---

## ✅ Status Atual (08/12/2025 15:42)

| Dashboard | Porta | URL | Status | PID |
|-----------|-------|-----|--------|-----|
| Original | 8501 | app.cafemartins.pt | 🟢 Online | 989 |
| **v7** | **8502** | **app2.cafemartins.pt** | **🟢 Online** | **40926** |

**Tudo operacional!** ✅
