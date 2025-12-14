# Serviço Systemd - Dashboard v7 (Porta 8502)

## ✅ CONFIGURADO PARA INICIAR AUTOMATICAMENTE!

O Dashboard v7 está agora configurado como serviço systemd e **iniciará automaticamente** em todos os reboots do servidor.

---

## 📋 Informações do Serviço

**Nome do Serviço:** `streamlit-dashboard-v7.service`

**Localização:** `/etc/systemd/system/streamlit-dashboard-v7.service`

**Status:** 🟢 Ativo e Habilitado

**PID Atual:** 42456

**Porta:** 8502

**URL Pública:** https://app2.cafemartins.pt

---

## 🔧 Comandos de Gestão

### Ver Status
```bash
sudo systemctl status streamlit-dashboard-v7.service
```

### Iniciar Serviço
```bash
sudo systemctl start streamlit-dashboard-v7.service
```

### Parar Serviço
```bash
sudo systemctl stop streamlit-dashboard-v7.service
```

### Reiniciar Serviço
```bash
sudo systemctl restart streamlit-dashboard-v7.service
```

### Recarregar após editar código
```bash
sudo systemctl restart streamlit-dashboard-v7.service
```

### Desativar Início Automático (NÃO RECOMENDADO)
```bash
sudo systemctl disable streamlit-dashboard-v7.service
```

### Reativar Início Automático
```bash
sudo systemctl enable streamlit-dashboard-v7.service
```

---

## 📊 Ver Logs

### Logs em Tempo Real
```bash
sudo journalctl -u streamlit-dashboard-v7.service -f
```

### Últimas 50 Linhas
```bash
sudo journalctl -u streamlit-dashboard-v7.service -n 50
```

### Logs desde Hoje
```bash
sudo journalctl -u streamlit-dashboard-v7.service --since today
```

### Logs com Erros
```bash
sudo journalctl -u streamlit-dashboard-v7.service -p err
```

---

## 🔄 Configuração do Serviço

```ini
[Unit]
Description=Streamlit Dashboard v7 - Café Martins (Despesify Integration + Custos REAIS)
After=network.target mariadb.service
Wants=mariadb.service

[Service]
Type=simple
User=jorge
WorkingDirectory=/home/jorge/Documentos/Streamlit
ExecStart=/home/jorge/Documentos/Streamlit/venv/bin/streamlit run dashboard_v7.py --server.port=8502 --server.address=0.0.0.0 --server.headless=true
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

Environment="PATH=/home/jorge/Documentos/Streamlit/venv/bin:/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=multi-user.target
```

### Dependências
- **After:** Inicia depois de `network.target` e `mariadb.service`
- **Wants:** Prefere que MariaDB esteja ativo (para Despesify)
- **Restart:** Reinicia automaticamente se crashar
- **RestartSec:** Espera 10 segundos antes de reiniciar

---

## 🎯 Comportamento após Reboot

### O que acontece quando o servidor reinicia:

1. ✅ Sistema operativo inicia
2. ✅ Rede fica ativa
3. ✅ MariaDB inicia (Despesify)
4. ✅ **Dashboard v7 inicia automaticamente na porta 8502**
5. ✅ Nginx proxy funciona (app2.cafemartins.pt)
6. ✅ Dashboard acessível com autenticação

**Tempo estimado:** ~30-60 segundos após boot

---

## 🆚 Comparação: Antes vs Depois

### ❌ Antes (Processo Manual)
```bash
# Precisava executar manualmente após cada reboot:
nohup streamlit run dashboard_v7.py --server.port 8502 &
```

**Problemas:**
- ❌ Não iniciava após reboot
- ❌ Podia parar sem reiniciar
- ❌ Difícil de monitorizar
- ❌ Logs dispersos

### ✅ Depois (Serviço Systemd)
```bash
# Inicia automaticamente!
# Para gerir:
sudo systemctl restart streamlit-dashboard-v7
```

**Vantagens:**
- ✅ Inicia automaticamente após reboot
- ✅ Reinicia se crashar
- ✅ Logs centralizados (journalctl)
- ✅ Gestão padronizada
- ✅ Dependências geridas (MariaDB)

---

## 📊 Serviços Streamlit Ativos

| Serviço | Porta | URL | Status | Auto-Start |
|---------|-------|-----|--------|------------|
| streamlit-santa-casa | 8501 | app.cafemartins.pt | 🟢 Ativo | ✅ Sim |
| **streamlit-dashboard-v7** | **8502** | **app2.cafemartins.pt** | **🟢 Ativo** | **✅ Sim** |
| streamlit-dashboard-v5 | - | - | ⚪ Desativado | ❌ Não |
| streamlit-dashboard | - | - | ⚪ Desativado | ❌ Não |

---

## 🔍 Verificação de Funcionamento

### Teste Rápido
```bash
# Ver se está a correr
sudo systemctl is-active streamlit-dashboard-v7.service

# Ver se está habilitado para boot
sudo systemctl is-enabled streamlit-dashboard-v7.service

# Testar acesso
curl -I http://localhost:8502
curl -I https://app2.cafemartins.pt
```

**Saída esperada:**
```
active
enabled
HTTP/1.1 200 OK
HTTP/2 200
```

---

## 🛠️ Troubleshooting

### Problema: Serviço falha ao iniciar

**Ver erro:**
```bash
sudo journalctl -u streamlit-dashboard-v7.service -n 50 --no-pager
```

**Causas comuns:**
1. Porta 8502 ocupada → `lsof -i:8502`
2. MariaDB não iniciou → `sudo systemctl status mariadb`
3. Ficheiro não existe → Verificar path no serviço
4. Permissões erradas → `ls -la /home/jorge/Documentos/Streamlit/dashboard_v7.py`

### Problema: Não inicia após reboot

**Verificar:**
```bash
# Está habilitado?
sudo systemctl is-enabled streamlit-dashboard-v7.service

# Reativar se necessário
sudo systemctl enable streamlit-dashboard-v7.service
```

### Problema: Crashou e não reiniciou

**Ver logs:**
```bash
sudo journalctl -u streamlit-dashboard-v7.service -p err --since "10 minutes ago"
```

**Forçar reinício:**
```bash
sudo systemctl restart streamlit-dashboard-v7.service
```

---

## 📝 Editar Configuração

### Se precisar alterar o serviço:

1. Editar ficheiro:
```bash
sudo nano /etc/systemd/system/streamlit-dashboard-v7.service
```

2. Recarregar configuração:
```bash
sudo systemctl daemon-reload
```

3. Reiniciar serviço:
```bash
sudo systemctl restart streamlit-dashboard-v7.service
```

---

## 🧪 Testar Reboot

### Para testar se funciona após reboot:

```bash
# 1. Verificar status atual
sudo systemctl status streamlit-dashboard-v7.service

# 2. Reiniciar servidor
sudo reboot

# 3. Após reboot, verificar novamente (via SSH)
sudo systemctl status streamlit-dashboard-v7.service

# 4. Testar acesso
curl -I https://app2.cafemartins.pt
```

**Deve estar automaticamente ativo!** ✅

---

## 📅 Data de Configuração

**Criado em:** 08/12/2025 15:45
**Última atualização:** 08/12/2025 15:46
**Versão:** v7.0.0 (Despesify Integration)

---

## ✅ Confirmação Final

- [x] Serviço criado: `/etc/systemd/system/streamlit-dashboard-v7.service`
- [x] Serviço habilitado: `systemctl enable`
- [x] Serviço ativo: PID 42456
- [x] Porta 8502: Acessível
- [x] Auto-start: Configurado
- [x] Logs: journalctl
- [x] Dependências: MariaDB configurado
- [x] Restart automático: Sim (10s)
- [x] URL pública: https://app2.cafemartins.pt ✅

**TUDO CONFIGURADO E FUNCIONAL!** 🎉

O dashboard v7 ficará sempre a correr na porta 8502, mesmo após reboots! 🚀
