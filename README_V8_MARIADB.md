# 🚀 Dashboard v8 - Ultra-Rápido com MariaDB

## 📋 **Índice**
1. [Visão Geral](#visão-geral)
2. [Comparação V7 vs V8](#comparação-v7-vs-v8)
3. [Performance - Benchmarks](#performance---benchmarks)
4. [Arquitetura](#arquitetura)
5. [Instalação e Uso](#instalação-e-uso)
6. [Scripts de Carregamento](#scripts-de-carregamento)
7. [Tabelas do MariaDB](#tabelas-do-mariadb)
8. [FAQ](#faq)

---

## 🎯 **Visão Geral**

O **Dashboard v8** é a nova versão do dashboard do Café Martins que carrega dados **diretamente do MariaDB**, substituindo o carregamento lento de ficheiros (.xlsx, .csv, .txt).

### **Principais Vantagens**

✅ **11.4x mais rápido** com filtros de data
✅ **Escalabilidade** - suporta milhões de registos
✅ **Dados sempre atualizados** via scripts cron
✅ **Zero desperdício** - filtra na query SQL (WHERE)
✅ **Queries otimizadas** com índices compostos
✅ **Integração com Despesify** mantida (custos reais)

---

## 📊 **Comparação V7 vs V8**

| Característica | V7 (Ficheiros) | V8 (MariaDB) |
|----------------|----------------|--------------|
| **Carregamento** | 11.27s | 992ms |
| **Performance** | Lenta com volume | Escala linearmente |
| **Filtros** | Pós-carregamento | Na query (WHERE) |
| **Desperdício** | 96.8% dos dados | 0% |
| **Escalabilidade** | <20k registos | Milhões |
| **Cache** | Cacheia tudo | Cacheia apenas filtrado |
| **Índices** | Não aplicável | 6 índices otimizados |

---

## ⚡ **Performance - Benchmarks**

### **Teste 1: Filtro de 30 dias**

```
📅 Período: 09/11/2025 - 09/12/2025

V7 (Ficheiros):
  • Carrega: 12,680 registos
  • Usa: 401 registos
  • Desperdício: 96.8%
  • Tempo: 11.27s

V8 (MariaDB):
  • Carrega: 948 registos (filtrados na query)
  • Desperdício: 0%
  • Tempo: 992ms

🚀 GANHO: V8 é 11.4x mais rápido!
```

### **Projeção com 100k Registos**

```
V7: 88.90s
V8: 1.49s

🚀 V8 seria 59.7x mais rápido!
```

### **Uso Real (Cache 30 min)**

Com cache de 30 minutos (48 carregamentos/dia):

| Versão | Tempo/dia | Tempo/mês |
|--------|-----------|-----------|
| V7 | 541s (9min) | 16,230s (4.5h) |
| V8 | 48s (48s) | 1,440s (24min) |
| **Economia** | **493s/dia** | **14,790s/mês** |

---

## 🏗️ **Arquitetura**

### **Fluxo de Dados V8**

```
┌─────────────────────────────────────────────────────────────┐
│                    CARREGAMENTO DIÁRIO                       │
│                   (Scripts Cron - NÃO TOCAR!)                │
└──────────────┬──────────────┬──────────────┬────────────────┘
               │              │              │
               ▼              ▼              ▼
   ┌───────────────┐ ┌────────────┐ ┌──────────────────┐
   │ 22:05 diária  │ │ 21:55      │ │ 07:40 domingos   │
   │ export_pos    │ │ load_pos2  │ │ santa_casa_batch │
   │ _to_mariadb   │ │ _to_mariadb│ │                  │
   └───────┬───────┘ └─────┬──────┘ └────────┬─────────┘
           │               │                 │
           ▼               ▼                 ▼
   ┌──────────────────────────────────────────────┐
   │         MariaDB - Database: dashboard        │
   ├──────────────────────────────────────────────┤
   │  • dados_dashboard (POS Café)    - 3,992     │
   │  • pos (POS Outros)              - 10,694    │
   │  • dados_santa_casa (Jogos)      - 3,364     │
   │                                               │
   │  Índices Otimizados:                         │
   │    - idx_data (todas as tabelas)             │
   │    - idx_produto, idx_codigo                 │
   │    - idx_data_produto (composto) ⭐          │
   └──────────────┬───────────────────────────────┘
                  │
                  ▼
        ┌───────────────────┐
        │  DataLoaderV8     │
        │  (data_loader_v8) │
        └─────────┬─────────┘
                  │
    Queries SQL Otimizadas (WHERE, BETWEEN)
                  │
                  ▼
        ┌────────────────────┐
        │  CostManagerV2     │
        │  (Despesify)       │
        └─────────┬──────────┘
                  │
                  ▼
        ┌────────────────────┐
        │  Dashboard v8      │
        │  Porta: 8505       │
        │  Cache: 30 min     │
        └────────────────────┘
```

### **Componentes Principais**

#### **1. data_loader_v8.py** 🆕
- Carrega dados diretamente do MariaDB
- Aplica filtros na query SQL (WHERE)
- 11.4x mais rápido com filtros
- Compatível com interface V7

#### **2. dashboard_v8.py** 🆕
- Interface idêntica ao V7
- Usa DataLoaderV8 internamente
- Porta: 8505
- Cache de 30 minutos

#### **3. cost_manager_v2.py**
- Mantido do V7
- Calcula custos reais (Despesify)
- Comissões Santa Casa

#### **4. Scripts de Carregamento** ⚠️ **NÃO TOCAR!**
- `export_pos_to_mariadb.py` (22:05 diária)
- `load_pos2_to_mariadb.py` (21:55 diária)
- `santa_casa_batch.py` (07:40 domingos)

---

## 🚀 **Instalação e Uso**

### **Requisitos**

- MariaDB instalado e configurado
- Python 3.11+
- Bibliotecas: `mysql-connector-python`, `pandas`, `streamlit`

### **Iniciar Dashboard V8**

```bash
cd /home/jorge/Documentos/Streamlit
./start_dashboard_v8.sh
```

Ou manualmente:

```bash
cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
streamlit run dashboard_v8.py --server.port=8505 --server.headless=true
```

### **Acesso**

- **Local:** http://localhost:8505
- **Externo:** http://app2.cafemartins.pt (via Nginx)

### **Testar Performance**

```bash
# Benchmark simples
venv/bin/python3 data_loader_v8.py

# Benchmark V7 vs V8
venv/bin/python3 benchmark_v7_vs_v8.py

# Benchmark com filtros (REAL)
venv/bin/python3 benchmark_filtros_v7_vs_v8.py
```

---

## 🔄 **Scripts de Carregamento**

### ⚠️ **IMPORTANTE: NÃO MODIFICAR ESTES SCRIPTS!**

Os dados são carregados automaticamente para o MariaDB via **cron**:

### **1. export_pos_to_mariadb.py**

```cron
5 22 * * * /home/jorge/web_scrapper/export_pos_to_mariadb_cron.sh
```

- **Tabela:** `dados_dashboard`
- **Fonte:** POS Café (web scraping Zonesoft)
- **Método:** TRUNCATE + INSERT
- **Registos:** ~4,000

### **2. load_pos2_to_mariadb.py**

```cron
55 21 * * * /home/jorge/web_scrapper/load_pos2_to_mariadb.sh
```

- **Tabela:** `pos`
- **Fonte:** Ficheiros CSV em `/home/jorge/Documentos/pos/pos_2/`
- **Método:** TRUNCATE + INSERT
- **Registos:** ~10,000

### **3. santa_casa_batch.py**

```cron
40 7 * * 0 /usr/bin/python3 "/home/jorge/Vscode/Santa Casa/santa_casa_batch.py"
```

- **Tabela:** `dados_santa_casa`
- **Fonte:** PDFs em `/home/jorge/Documentos/Santa casa/pdf/`
- **Método:** TRUNCATE + INSERT
- **Registos:** ~3,000
- **Frequência:** Domingos 07:40

---

## 📊 **Tabelas do MariaDB**

### **Database:** `dashboard`

| Tabela | Registos | Colunas Principais | Índices |
|--------|----------|-------------------|---------|
| `dados_dashboard` | 3,992 | data, codigo, produto, quantidade, valor_total | idx_data, idx_codigo, idx_produto, idx_data_produto |
| `pos` | 10,694 | data, codigo, designacao, qtd, val_total | idx_data, idx_codigo, idx_designacao, idx_data_codigo |
| `dados_santa_casa` | 3,364 | data, categoria, jogo, valor | idx_data, idx_categoria, idx_jogo |

### **Configuração do MariaDB**

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'cathie',
    'database': 'dashboard'
}
```

### **Índices Compostos Adicionados**

```sql
-- Otimização para queries com filtros múltiplos
CREATE INDEX idx_data_produto ON dados_dashboard(data, produto);
CREATE INDEX idx_data_codigo ON pos(data, codigo);
```

---

## 💡 **FAQ**

### **1. Posso usar V7 e V8 ao mesmo tempo?**

✅ **SIM!** V7 (porta 8502) e V8 (porta 8505) podem rodar simultaneamente.

### **2. V8 substitui V7 completamente?**

✅ **SIM**, para produção recomenda-se V8. Mantém V7 apenas para backup/comparação.

### **3. Como atualizar os dados?**

Os dados são atualizados **automaticamente** pelos scripts cron:
- POS Café e Outros: **diariamente às 21:55 e 22:05**
- Santa Casa: **domingos às 07:40**

### **4. Posso filtrar por categoria/produto?**

✅ **SIM!** V8 aceita filtros opcionais:

```python
loader = DataLoaderV8()

# Filtrar por data
df = loader.carregar_tudo_integrado_com_custos(
    data_inicio=datetime(2025, 11, 1),
    data_fim=datetime(2025, 11, 30)
)
```

### **5. V8 funciona com Despesify?**

✅ **SIM!** CostManagerV2 está integrado:

```python
loader = DataLoaderV8(usar_despesify=True)
```

### **6. Como adicionar mais dados?**

1. Os scripts cron carregam automaticamente
2. Para carregar manualmente:
   ```bash
   cd /home/jorge/web_scrapper
   ./export_pos_to_mariadb_cron.sh
   ./load_pos2_to_mariadb.sh
   ```

### **7. Como fazer backup do MariaDB?**

```bash
# Backup completo
mysqldump -u root -p'cathie' dashboard > backup_dashboard_$(date +%Y%m%d).sql

# Restaurar
mysql -u root -p'cathie' dashboard < backup_dashboard_20251210.sql
```

### **8. V8 consome mais memória?**

❌ **NÃO!** V8 consome **MENOS** memória porque:
- Carrega apenas dados filtrados
- Cache armazena menos registos
- MariaDB faz garbage collection automático

---

## 🎯 **Quando Usar V8 vs V7**

### **✅ Use V8 quando:**

- Dashboards com **filtros de data/categoria**
- Volume > 20k registos
- Consultas frequentes (cache otimizado)
- Análises de períodos específicos
- Queries complexas (multi-filtro)

### **⚠️ Use V7 quando:**

- Precisa carregar **TUDO sempre**
- Volume muito pequeno (<5k registos)
- Ficheiros locais sem MariaDB
- Ambiente de desenvolvimento/teste

---

## 📈 **Roadmap Futuro**

### **Próximas Melhorias**

- [ ] Normalizar campo `data` em `dados_santa_casa` (VARCHAR → DATE)
- [ ] Adicionar coluna `categoria` pré-calculada nas tabelas
- [ ] Cache distribuído (Redis)
- [ ] API REST para queries externas
- [ ] Dashboard em tempo real (WebSockets)

---

## 📞 **Suporte**

**Documentação Completa:**
- [README_V7_DESPESIFY.md](README_V7_DESPESIFY.md) - Dashboard V7
- [COMPARACAO_DASHBOARDS.md](COMPARACAO_DASHBOARDS.md) - Comparação geral
- [MANUAL_INSTALACAO_SETUP_COMPLETO.md](MANUAL_INSTALACAO_SETUP_COMPLETO.md) - Setup completo

**Logs:**
```bash
# Logs dos scripts cron
tail -f /home/jorge/web_scrapper/mariadb_cron.log
tail -f /home/jorge/web_scrapper/load_pos2.log
```

---

## ✅ **Checklist de Implementação**

- [x] data_loader_v8.py criado
- [x] dashboard_v8.py criado
- [x] start_dashboard_v8.sh criado
- [x] Índices otimizados adicionados
- [x] Benchmarks executados
- [x] Documentação completa
- [x] Scripts cron funcionando
- [x] Integração Despesify mantida
- [ ] Testes em produção
- [ ] Migração completa V7 → V8

---

**Data de Criação:** 10/12/2025
**Versão:** 8.0.0
**Autor:** Jorge Martins + Claude Code
**Última Atualização:** 10/12/2025

---

> **💡 Dica:** Execute `venv/bin/python3 benchmark_filtros_v7_vs_v8.py` para ver a diferença de performance ao vivo!
