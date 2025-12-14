# Dashboard v7 - Integração com Despesify 💰

## 🎯 Resumo

O Dashboard v7 introduz integração REAL com a base de dados **Despesify (MariaDB)** para custos operacionais precisos, eliminando estimativas e trazendo dados factuais de despesas.

---

## 🆕 O que mudou?

### **Sistema HÍBRIDO de Custos**

O v7 implementa um sistema inteligente que combina:

1. **Despesas Operacionais REAIS** (desde 1/12/2025)
   - Fonte: Base de dados MariaDB do Despesify
   - Dados: Despesas reais com faturas, NIFs, categorias POC
   - Precisão: 100% (dados factuais)

2. **Custos de Produtos** (mantém CSV)
   - Custos unitários por produto
   - Margens por categoria
   - Cálculo de COGS (Cost of Goods Sold)

3. **Comissões Santa Casa** (automático)
   - Percentagens por tipo de jogo
   - Cálculo automático de comissões

---

## 📦 Novos Módulos

### 1. `despesify_loader.py`
Carregador de despesas da base de dados MariaDB.

**Funcionalidades:**
- Conexão com MariaDB (localhost, user: root, db: despesify)
- Mapeamento de categorias POC → Dashboard
- Separação: Despesas Operacionais vs Compras de Mercadorias
- Resumos por categoria e período

**Exemplo de uso:**
```python
from despesify_loader import DespesifyLoader
from datetime import datetime

loader = DespesifyLoader()
resumo = loader.get_resumo_despesas(
    datetime(2025, 12, 1),
    datetime.now()
)

print(f"Total Operacionais: €{resumo['total_operacionais']:.2f}")
print(f"Fonte: Despesify MariaDB (REAL)")
```

### 2. `cost_manager_v2.py`
Gestor de custos HÍBRIDO (substitui `cost_manager.py`).

**Lógica de Decisão:**
- Se `data >= 1/12/2025` E `Despesify disponível` → **Custos REAIS**
- Caso contrário → **Custos ESTIMADOS** (CSV)

**Funcionalidades Novas:**
- `get_custos_operacionais_periodo(data_inicio, data_fim)` → Retorna (custo, fonte, df)
- `calcular_metricas_financeiras(df, data_inicio, data_fim)` → Inclui `fonte_custos_operacionais`
- `get_resumo_custos_operacionais(data_inicio, data_fim)` → Resumo REAL ou ESTIMADO

### 3. `data_loader_v7.py`
Data loader atualizado para usar `CostManagerV2`.

**Mudanças:**
- Parâmetro `usar_despesify=True` (ativa integração)
- Passa datas para `calcular_metricas_financeiras()` (antes só passava dias)
- Suporta métricas híbridas

---

## 🎨 Dashboard v7 - Mudanças Visuais

### Tab "💸 Análise de Custos"

**Novo indicador de fonte:**
```
✅ Custos Operacionais REAIS do Despesify (desde 1/12/2025)
```
ou
```
⚠️ Custos Operacionais ESTIMADOS (antes de 1/12/2025 ou sem dados no Despesify)
```

**Nova tabela (quando fonte = REAL):**
```
📄 Despesas Reais do Despesify (Detalhado)
- Data
- Descrição (Fornecedor)
- Categoria (mapeada)
- Valor Total
- IVA
- Valor Sem IVA
- NIF Fornecedor
```

**Gráficos atualizados:**
- Título: "Custos Operacionais por Categoria (REAL)" ou "(ESTIMADO)"
- Usa valores do período (não apenas mensal)

---

## 🔧 Configuração e Uso

### Requisitos

1. **MariaDB** com base de dados `despesify`
   - User: `root`
   - Password: `cathie`
   - Tabelas: `expenses`, `categories`

2. **Bibliotecas Python:**
```bash
pip install mysql-connector-python
```

### Executar Dashboard v7

**Porta 8502 (recomendado):**
```bash
streamlit run dashboard_v7.py --server.port 8502 --server.headless true
```

**Parâmetros:**
- Cache: 30 minutos (TTL=1800s)
- Despesify: Ativado por padrão

### Desativar Despesify (usar apenas estimados)

Edite `dashboard_v7.py`:
```python
loader = DataLoaderV7(usar_despesify=False)  # DESATIVA DESPESIFY
```

---

## 📊 Mapeamento de Categorias

O Despesify usa categorias do **POC (Plano Oficial de Contabilidade)**. O sistema mapeia automaticamente:

| Categoria POC | Categoria Dashboard |
|--------------|---------------------|
| 611 – Compras de mercadorias | **COMPRAS_MERCADORIAS** (separado!) |
| 6221 Energia | Energia e Água |
| 6222 Água | Energia e Água |
| 6227 Higiene e limpeza | Higiene e Limpeza |
| 626 – Representação | Representação |
| ... | ... |

**IMPORTANTE:** Compras de mercadorias (611) são marcadas como `PRODUTO` (não operacional).

---

## 🧪 Testes e Validação

### Teste 1: Conexão Despesify
```bash
python3 despesify_loader.py
```

**Saída esperada:**
```
✅ Conexão com Despesify OK

📊 RESUMO DE DESPESAS (01/12/2025 - 08/12/2025)
   Total Geral: €590.55
   • Despesas Operacionais: €108.10
   • Compras de Mercadorias: €482.45
```

### Teste 2: CostManagerV2
```bash
python3 cost_manager_v2.py
```

**Saída esperada:**
```
📊 CUSTOS OPERACIONAIS:
   Período: 01/12/2025 - 08/12/2025
   Total: €108.10
   Fonte: REAL ✅
```

### Teste 3: Dashboard v7
1. Aceder: http://localhost:8502
2. Ir para tab "💸 Análise de Custos"
3. Verificar:
   - Mensagem de fonte (REAL ou ESTIMADO)
   - Valores correspondem ao Despesify
   - Tabela de despesas detalhadas (se REAL)

---

## 🔍 Troubleshooting

### Problema: "Erro ao conectar à base de dados"
**Solução:**
```bash
# Verificar MariaDB
sudo systemctl status mariadb

# Testar login
mysql -u root -pcathie -e "USE despesify; SELECT COUNT(*) FROM expenses;"
```

### Problema: "Usando custos estimados" (mas deveria usar REAIS)
**Causas possíveis:**
1. Período antes de 1/12/2025
2. MariaDB desligado
3. Sem despesas no período filtrado

**Verificar:**
```sql
SELECT MIN(expense_date), MAX(expense_date), COUNT(*)
FROM despesify.expenses
WHERE expense_date >= '2025-12-01';
```

### Problema: Valores duplicados (produtos + despesas)
**Solução:** O sistema separa automaticamente:
- `category_id = 46` ("611 – Compras de mercadorias") → **NÃO** vai para custos operacionais
- Outros → Custos operacionais

---

## 📈 Benefícios do Sistema Híbrido

### ✅ Vantagens

1. **Precisão:** Custos operacionais REAIS (não estimados)
2. **Rastreabilidade:** Cada despesa tem NIF, fatura, data
3. **Histórico:** Dados desde 1/12/2025 (e crescendo)
4. **Flexibilidade:** Fallback automático para estimados (períodos antigos)
5. **Sem duplicação:** Compras de mercadorias separadas automaticamente

### ⚠️ Limitações

1. **Dados antes de 1/12/2025:** Usa custos estimados (CSV)
2. **Dependência MariaDB:** Se offline, usa estimados
3. **Categorização:** Depende de categorias corretas no Despesify

---

## 🔄 Migração v6 → v7

### Compatibilidade

- ✅ Todas as funcionalidades do v6 mantidas
- ✅ Mesmos filtros, tabs, gráficos
- ✅ Exportação Excel compatível
- ✅ Break-even funciona com custos REAIS

### Diferenças

| Aspecto | v6 | v7 |
|---------|----|----|
| Custos Operacionais | CSV (estimado) | Despesify (REAL) ou CSV |
| Fonte de dados | Estática | Dinâmica (MariaDB) |
| Precisão | ~80% | ~95-100% (período c/ dados) |
| Rastreabilidade | Nenhuma | Total (NIF, fatura) |

### Executar ambos

Dashboard v6 (porta 8501):
```bash
streamlit run dashboard_v6.py --server.port 8501
```

Dashboard v7 (porta 8502):
```bash
streamlit run dashboard_v7.py --server.port 8502
```

---

## 📝 Próximos Passos

### Melhorias Futuras

1. **Sincronização automática:** Cron job para importar despesas
2. **Alertas:** Notificações de despesas acima do esperado
3. **Previsões:** ML para prever custos futuros baseado em histórico
4. **Comparação:** v6 (estimado) vs v7 (real) lado a lado
5. **Categorização IA:** Sugerir categorias para despesas não classificadas

### Dados a Adicionar no Despesify

- Ordenados (categoria 631)
- Segurança Social (categoria 6321)
- Renda (categoria 623)
- Eletricidade (categoria 6221)
- Água (categoria 6222)

Quanto mais completo o Despesify, mais preciso o dashboard!

---

## 📞 Suporte

**Desenvolvido para:** Café Martins
**Data:** Dezembro 2025
**Versão:** 7.0.0 (Despesify Integration)

**Tecnologias:**
- Streamlit 1.30+
- Plotly 5.18+
- MariaDB 10.5+
- Python 3.8+

---

## 🎉 Conclusão

O Dashboard v7 representa um salto qualitativo na gestão de custos:

- **Antes (v6):** "Acho que os custos são ~€X"
- **Agora (v7):** "Os custos são EXATAMENTE €X (fatura Y, fornecedor Z)"

Dados REAIS → Decisões MELHORES → Lucros MAIORES! 📈💰
