# ✅ Migração V7 → V8 Completa

**Data:** 10/12/2025
**Status:** ✅ Concluída com Sucesso

---

## 🎯 **RESUMO:**

O Dashboard V7 (ficheiros) foi **substituído** pelo Dashboard V8 (MariaDB) na **porta 8502**.

---

## ✅ **O QUE FOI FEITO:**

### **1. Dashboard V8 Criado** 🚀
- ✅ `data_loader_v8.py` - Carregador MariaDB ultra-rápido
- ✅ `dashboard_v8.py` - Dashboard usando V8
- ✅ Performance: **11.4x mais rápido** com filtros
- ✅ Valores: **100% idênticos** ao V7 (€580,280.44)

### **2. Dados Históricos Importados** 📦
- ✅ 7,002 registos de 2023-2024 adicionados ao MariaDB
- ✅ Total: 10,994 registos POS Café (2023-2025)
- ✅ Script: `import_xlsx_historico_to_mariadb.py`

### **3. Correções Aplicadas** 🔧
- ✅ **POS-Outros:** Filtro `codigo = 50010` (apenas Totobola)
- ✅ **Santa Casa:** Usar `vendas_iliquidas` (não `valor` líquido)
- ✅ **Santa Casa:** Excluir `PRESTAÇÃO DE CONTAS`

### **4. Scripts Cron Atualizados** 🔄
- ✅ **export_pos_to_mariadb.py** - DELETE dinâmico (preserva histórico)
- ✅ **load_pos2_to_mariadb.py** - DELETE dinâmico (preserva histórico)
- ✅ **santa_casa_batch.py** - DELETE dinâmico (preserva histórico)
- ✅ **Adaptação automática:** Funciona em 2025, 2026, 2027, etc.

### **5. V7 Desativado / V8 Ativado na Porta 8502** ⚙️
- ✅ V7 parado e desabilitado
- ✅ V8 configurado para porta 8502 (em vez de 8505)
- ✅ Serviço systemd criado: `streamlit-dashboard-v8.service`
- ✅ Crontab atualizado: Reinicia V8 aos domingos 09:00

---

## 📊 **RESULTADO FINAL:**

### **Valores (100% idênticos):**
```
V7 (Ficheiros):  €580,280.44
V8 (MariaDB):    €580,280.44
Diferença:       €0.00 ✅
```

### **Performance:**
- **Carregamento total:** V8 tem mais dados mas é rápido
- **Com filtros (30 dias):** V8 é **11.4x mais rápido** (11.27s → 992ms)
- **Projeção (100k registos):** V8 seria **59.7x mais rápido**

### **Serviços Ativos:**
```
PID 476421: Dashboard V8 → Porta 8502 ✅
PID 989:    Dashboard Original → Porta 8501 (mantido)
```

---

## 🔧 **CONFIGURAÇÕES:**

### **Porta 8502 (V8 - PRODUÇÃO):**
- **URL Local:** http://localhost:8502
- **URL Externa:** http://app2.cafemartins.pt
- **Serviço:** `streamlit-dashboard-v8.service`
- **Script:** `/home/jorge/Documentos/Streamlit/start_dashboard_v8.sh`
- **Autostart:** ✅ Habilitado (systemd)

### **Scripts de Dados (MariaDB):**
| Script | Horário | Tabela | Comportamento |
|--------|---------|--------|---------------|
| export_pos_to_mariadb.py | 22:05 diária | dados_dashboard | DELETE ano atual |
| load_pos2_to_mariadb.py | 21:55 diária | pos | DELETE ano atual |
| santa_casa_batch.py | 07:40 domingos | dados_santa_casa | DELETE ano atual |

**Todos preservam histórico automaticamente!** ✅

### **Crontab:**
```bash
# Reiniciar dashboards aos domingos 09:00
0 9 * * 0 /usr/bin/systemctl restart streamlit-santa-casa streamlit-dashboard-v8
```

---

## 📋 **COMANDOS ÚTEIS:**

### **Gerenciar Serviço V8:**
```bash
# Status
sudo systemctl status streamlit-dashboard-v8

# Reiniciar
sudo systemctl restart streamlit-dashboard-v8

# Parar
sudo systemctl stop streamlit-dashboard-v8

# Iniciar
sudo systemctl start streamlit-dashboard-v8

# Ver logs
sudo journalctl -u streamlit-dashboard-v8 -f
```

### **Verificar Porta:**
```bash
# Ver processo na porta 8502
lsof -i :8502

# Ver todas portas Streamlit
ss -tlnp | grep 850
```

### **Testar Carregamento:**
```bash
cd /home/jorge/Documentos/Streamlit
venv/bin/python3 -c "
from data_loader_v8 import DataLoaderV8
loader = DataLoaderV8()
df = loader.carregar_tudo_integrado_com_custos()
print(f'Total: €{df[\"Valor\"].sum():,.2f}')
"
```

---

## 🔄 **ROLLBACK (se necessário):**

### **Voltar para V7:**
```bash
# 1. Parar V8
sudo systemctl stop streamlit-dashboard-v8
sudo systemctl disable streamlit-dashboard-v8

# 2. Habilitar V7
sudo systemctl enable streamlit-dashboard-v7
sudo systemctl start streamlit-dashboard-v7

# 3. Atualizar crontab (V8 → V7)
crontab -e
# Mudar: streamlit-dashboard-v8 → streamlit-dashboard-v7
```

**⚠️ Mas NÃO recomendo! V8 é superior em todos os aspectos.**

---

## 📚 **DOCUMENTAÇÃO:**

| Ficheiro | Descrição |
|----------|-----------|
| [README_V8_MARIADB.md](README_V8_MARIADB.md) | Documentação técnica completa |
| [SUMARIO_DASHBOARD_V8.md](SUMARIO_DASHBOARD_V8.md) | Resumo executivo |
| [INICIO_RAPIDO_V8.md](INICIO_RAPIDO_V8.md) | Guia de início rápido |
| [CORRECOES_V8_PROBLEMAS.md](CORRECOES_V8_PROBLEMAS.md) | Problemas resolvidos |
| [SCRIPTS_CRON_ATUALIZADOS.md](SCRIPTS_CRON_ATUALIZADOS.md) | Scripts cron adaptados |
| [MIGRACAO_V7_PARA_V8_COMPLETA.md](MIGRACAO_V7_PARA_V8_COMPLETA.md) | Este ficheiro |

---

## ✅ **CHECKLIST FINAL:**

- [x] Dashboard V8 criado e testado
- [x] Dados históricos importados (2023-2024)
- [x] Valores V7 = V8 (€580,280.44)
- [x] Scripts cron adaptados (preservam histórico)
- [x] V7 desativado (porta 8502 liberada)
- [x] V8 configurado na porta 8502
- [x] Serviço systemd criado e habilitado
- [x] Crontab atualizado (V5 → V8)
- [x] Cache limpo
- [x] Documentação completa criada
- [x] Testado e funcionando ✅

---

## 🎉 **MIGRAÇÃO COMPLETA!**

```
┌─────────────────────────────────────────────────────────────┐
│                    ANTES (V7)                               │
│  Porta: 8502 | Fonte: Ficheiros | Performance: Lenta       │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    MIGRAÇÃO V7 → V8
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    DEPOIS (V8)                              │
│  Porta: 8502 | Fonte: MariaDB | Performance: 11.4x         │
│  Valores: Idênticos | Histórico: Preservado | Auto: ✅     │
└─────────────────────────────────────────────────────────────┘
```

**Dashboard V8 em produção! 🚀**

---

**Acesso:**
- **Local:** http://localhost:8502
- **Externa:** http://app2.cafemartins.pt

**Performance:**
- ⚡ 11.4x mais rápido com filtros
- 📊 Valores 100% corretos
- 🔄 Scripts cron adaptados automaticamente
- 🎯 Pronto para 2026, 2027, 2028...

---

**Criado por:** Jorge Martins + Claude Code
**Data:** 10/12/2025
**Status:** ✅ Produção
