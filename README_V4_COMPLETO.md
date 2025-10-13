# 📊 Dashboard v4 - Análise Profissional Completa

## 🎯 Visão Geral

O **Dashboard v4** é uma plataforma profissional de análise de vendas com **categorização inteligente de produtos** e **métricas avançadas**. Analisa automaticamente:

- ☕ **Cafés** (Café, Galão, Chá, etc.)
- 🍺 **Cervejas** (Mini, Média, Caneca, Especiais, etc.)
- 🍷 **Vinhos** (Tinto, Branco, Porto, Moscatel, etc.)
- 🍸 **Aperitivos** (Martini, Kir, Ricard, etc.)
- 🥃 **Digestivos** (Aguardente, Brandy, Whisky, Licores, etc.)
- 🥤 **Refrigerantes** (Sumos, Ice Tea, Energéticos, etc.)
- 💧 **Águas** (Natural, com Gás, com Sabor, etc.)
- 🍰 **Alimentação** (Pastelaria, Snacks, Chocolates, etc.)
- 🎲 **Jogos Santa Casa** (Euromilhões, Totoloto, Raspadinhas, etc.)

## 🚀 Início Rápido

```bash
cd /home/jorge/Documentos/Streamlit
streamlit run dashboard_v4.py
```

**URL:** http://localhost:8501

## 📁 Arquitetura do Sistema

### Módulos Principais

```
dashboard_v4.py              # Dashboard principal (interface Streamlit)
├─ data_loader_v4.py        # Carregamento e integração de dados
├─ product_categorizer.py   # Categorização inteligente de produtos
├─ pos/pos_1/*.xlsx         # Vendas de café (Excel)
└─ pos/pos_2/*.csv          # Outros produtos (CSV)
```

### Fluxo de Dados

```
Fontes de Dados
    ↓
DataLoaderV4 (carrega dados)
    ↓
ProductCategorizer (categoriza automaticamente)
    ↓
Dashboard v4 (apresenta análises)
```

## 🎨 Interface do Dashboard

### Filtros Laterais (Sidebar)

| Filtro | Descrição | Tipo |
|--------|-----------|------|
| **Período** | Data início e fim | Date Range |
| **Categorias** | Selecionar categorias específicas | Multiselect |
| **Subcategorias** | Dependente das categorias | Multiselect |
| **Fonte** | POS-Café, POS-Outros, Santa Casa | Multiselect |
| **Dias Úteis** | Excluir fins de semana | Checkbox |

### Métricas Principais (Topo)

4 KPIs principais com **comparação ao período anterior**:

1. 💰 **Total de Vendas** (€)
2. 📊 **Média Diária** (€/dia)
3. 🎯 **Ticket Médio** (€/transação)
4. 📈 **Taxa de Crescimento** (% vs mês anterior)

## 📑 Tabs Profissionais

### Tab 1: 📊 Visão Geral

**O que mostra:**
- KPIs resumidos por categoria com ícones
- Distribuição de vendas (gráfico de pizza)
- Top 10 produtos mais vendidos
- Evolução temporal de vendas

**Para quê serve:**
- Visão rápida do negócio
- Identificar principais fontes de receita
- Monitorar tendências gerais

---

### Tab 2: ☕ Análise por Categoria

**O que mostra:**
- Seletor de categoria específica
- 4 métricas da categoria (Total, Média, Transações, % do Total)
- Top 10 subcategorias
- Top 20 produtos da categoria
- Gráficos de distribuição e evolução

**Para quê serve:**
- Análise profunda de cada categoria
- Identificar produtos estrela
- Otimizar mix de produtos

**Exemplo de uso:**
> "Quero ver quais tipos de cerveja vendem mais"
> → Seleciona categoria **CERVEJAS**
> → Vê que "Cerveja Mini" e "Imperial" dominam
> → Identifica oportunidades em cervejas especiais

---

### Tab 3: 📈 Análise Temporal

**O que mostra:**
- Granularidade: Diária / Semanal / Mensal
- Vendas por dia da semana
- Heatmap (categoria vs dia da semana)
- Vendas por hora (se disponível)
- Análise mensal e trimestral
- Sazonalidade

**Para quê serve:**
- Identificar padrões temporais
- Otimizar horários de trabalho
- Planejar inventário
- Detectar sazonalidade

**Insights típicos:**
- Sexta-feira vende 30% mais que segunda
- Cervejas vendem mais ao fim de semana
- Cafés têm pico entre 9h-11h

---

### Tab 4: 🎯 Performance & KPIs

**O que mostra:**
- Taxa de crescimento por categoria
- Top 10 e Bottom 10 performers
- **Análise de Pareto (80/20)**
- Correlação entre categorias (heatmap)
- Índice de diversificação (HHI)

**Para quê serve:**
- Identificar categorias em crescimento/declínio
- Aplicar regra 80/20 (80% das vendas vêm de 20% dos produtos)
- Detectar produtos correlacionados
- Avaliar diversificação do negócio

**Métricas Profissionais:**

**Taxa de Crescimento:**
- Compara cada categoria com período anterior
- Verde = crescimento, Vermelho = declínio

**Análise de Pareto:**
- Identifica os 20% de produtos que geram 80% da receita
- Ajuda a focar nos produtos-chave

**Correlação:**
- Produtos vendidos em conjunto (ex: café + pastelaria)
- Oportunidades de cross-selling

**HHI (Índice Herfindahl-Hirschman):**
- Mede concentração do negócio
- 0 = muito diversificado
- 10000 = muito concentrado
- Ideal: 1500-2500

---

### Tab 5: 💰 Análise Financeira

**O que mostra:**
- Faturamento total por categoria
- Faturamento médio por transação
- Ticket médio por categoria
- **Gráfico Waterfall** (contribuições)
- **Projeção de faturamento** (30 dias)

**Para quê serve:**
- Análise financeira detalhada
- Planeamento de receitas
- Identificar principais contribuidores
- Previsões de curto prazo

**Métricas Explicadas:**

**Gráfico Waterfall:**
- Mostra contribuição de cada categoria para o total
- Visualiza cascata de valores
- Identifica pilares do faturamento

**Projeção Linear:**
- Baseada em tendência histórica
- Projeção para próximos 30 dias
- Útil para planeamento financeiro

---

### Tab 6: 📊 Comparação & Benchmarks

**O que mostra:**
- Scatter plot: Volume vs Valor Médio
- Performance por fonte de dados
- Benchmarks detalhados
- Sazonalidade comparativa
- Performance relativa normalizada

**Para quê serve:**
- Comparar diferentes categorias
- Benchmarking entre fontes
- Identificar outliers
- Análise competitiva interna

**Quadrantes do Scatter:**
- **Alto Volume + Alto Valor** = Estrelas ⭐
- **Alto Volume + Baixo Valor** = Vacas Leiteiras 🐄
- **Baixo Volume + Alto Valor** = Oportunidades 💎
- **Baixo Volume + Baixo Valor** = Revisar ⚠️

---

### Tab 7: 📑 Dados Detalhados

**O que mostra:**
- Tabela interativa completa
- Opções de agrupamento (Categoria, Subcategoria, Produto, Fonte, Data)
- Estatísticas resumidas
- Exportação CSV e Excel

**Para quê serve:**
- Análise granular
- Exportação para análises externas
- Auditoria de dados
- Relatórios customizados

**Funcionalidades:**
- ✅ Agrupamento dinâmico
- ✅ Ordenação por qualquer coluna
- ✅ Estatísticas automáticas
- ✅ Exportação CSV
- ✅ Exportação Excel com múltiplas folhas

## 🎓 Como Usar - Casos de Uso

### Caso 1: Analisar Vendas de Cervejas

1. Ir para Tab **"☕ Análise por Categoria"**
2. Selecionar **CERVEJAS** no dropdown
3. Ver:
   - Total vendido em cervejas
   - Quais tipos vendem mais (Mini vs Média vs Caneca)
   - Evolução temporal
   - Top produtos

**Ação:** Ajustar stock com base nos dados

---

### Caso 2: Identificar Dias de Pico

1. Ir para Tab **"📈 Análise Temporal"**
2. Ver gráfico "Vendas por Dia da Semana"
3. Identificar dias com mais vendas
4. Ver heatmap para padrões por categoria

**Ação:** Escalar equipe nos dias de pico

---

### Caso 3: Aplicar Regra 80/20

1. Ir para Tab **"🎯 Performance & KPIs"**
2. Rolar até "Análise de Pareto"
3. Ver quais produtos geram 80% das vendas
4. Identificar os 20% de produtos-chave

**Ação:** Focar inventário e promoções nos produtos-chave

---

### Caso 4: Projetar Receitas

1. Ir para Tab **"💰 Análise Financeira"**
2. Ver "Projeção de Faturamento"
3. Analisar tendência e projeção
4. Exportar dados para planeamento

**Ação:** Planeamento financeiro baseado em dados

---

### Caso 5: Comparar Categorias

1. Ir para Tab **"📊 Comparação & Benchmarks"**
2. Ver scatter plot
3. Identificar categorias em cada quadrante
4. Analisar performance relativa

**Ação:** Estratégias diferenciadas por quadrante

## 📊 Dados Atuais

### Estatísticas (atualizado 13/10/2025)

| Categoria | Registos | Total (€) | % do Total |
|-----------|----------|-----------|------------|
| 🍺 **CERVEJAS** | 2.306 | 27.152,70 | 28,2% |
| ☕ **CAFETARIA** | 931 | 22.233,50 | 23,1% |
| 🍸 **APERITIVOS** | 1.488 | 6.495,00 | 6,7% |
| 🥤 **REFRIGERANTES** | 609 | 1.484,90 | 1,5% |
| 💧 **ÁGUAS** | 977 | 1.446,60 | 1,5% |
| 🥃 **DIGESTIVOS** | 642 | 1.097,75 | 1,1% |
| 🍰 **ALIMENTAÇÃO** | 612 | 835,60 | 0,9% |
| 🍷 **VINHOS** | 529 | 805,20 | 0,8% |
| 📦 **OUTROS** | 557 | 880,17 | 0,9% |
| 🎲 **JOGOS SANTA CASA** | 533 | 33.878,04 | 35,2% |
| **TOTAL** | **9.184** | **96.309,46** | **100%** |

### Período de Dados

- **Café (POS-1):** 2023-01-02 a 2025-05-31
- **Outros (POS-2):** 2024-01-02 a 2025-10-13
- **Total:** 9.184 transações

## 🔧 Configuração Técnica

### Requisitos

```bash
streamlit >= 1.30
pandas >= 2.0
plotly >= 5.18
numpy >= 1.24
openpyxl >= 3.1
scikit-learn >= 1.3
```

### Instalação

```bash
cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
pip install -r requirements.txt
```

### Performance

- **Cache de dados:** 30 minutos
- **Tempo de carregamento:** ~3-5 segundos
- **Memória:** ~200MB
- **Otimizado para:** até 100.000 registos

## 🎨 Personalização

### Adicionar Nova Categoria

Editar [product_categorizer.py](product_categorizer.py):

```python
'NOVA_CATEGORIA': {
    'subcategorias': {
        'Subcategoria 1': ['palavra1', 'palavra2'],
        'Subcategoria 2': ['palavra3', 'palavra4']
    },
    'cor': '#HEX_COLOR',
    'icone': '🎯'
}
```

### Ajustar Cores

Editar CSS no [dashboard_v4.py](dashboard_v4.py) na secção `st.markdown("""<style>...`)

### Adicionar Métricas

Criar nova função e adicionar na tab desejada:

```python
def minha_metrica(df):
    # Cálculos
    return resultado

# Usar na tab
with tab_x:
    resultado = minha_metrica(df_filtrado)
    st.metric("Nova Métrica", resultado)
```

## 📞 Suporte & Troubleshooting

### Dashboard não carrega?

```bash
# Verificar processos
ps aux | grep streamlit

# Limpar e reiniciar
pkill -f streamlit
streamlit run dashboard_v4.py
```

### Dados não aparecem?

```bash
# Testar carregamento
python3 data_loader_v4.py

# Verificar ficheiros
ls -lh /home/jorge/Documentos/pos/pos_1/
ls -lh /home/jorge/Documentos/pos/pos_2/
```

### Erro de categorização?

```bash
# Testar categorizador
python3 product_categorizer.py
```

### Performance lenta?

- Reduzir intervalo de datas nos filtros
- Selecionar menos categorias
- Limpar cache: Barra lateral → "Clear cache"

## 🚀 Próximas Melhorias Sugeridas

### Curto Prazo
- [ ] Adicionar alertas automáticos (vendas abaixo do esperado)
- [ ] Gráficos comparativos YoY (Year over Year)
- [ ] Análise de margem de lucro por categoria
- [ ] Dashboard mobile-friendly

### Médio Prazo
- [ ] Integração com sistema de inventário
- [ ] Previsões com Machine Learning (ARIMA, Prophet)
- [ ] Relatórios agendados por email
- [ ] API REST para integração

### Longo Prazo
- [ ] Análise de comportamento de clientes
- [ ] Segmentação RFM (Recency, Frequency, Monetary)
- [ ] Análise de cestas de compras (Market Basket)
- [ ] Dashboard em tempo real (WebSocket)

## 📚 Recursos Adicionais

### Documentação

- [Dashboard Original](dashboard.py) - Dashboard inicial (Jogos Santa Casa)
- [Dashboard v3](dashboard_v3.py) - Versão intermediária
- [Comparação Dashboards](COMPARACAO_DASHBOARDS.md) - Comparativo de versões
- [Início Rápido v3](INICIO_RAPIDO_V3.md) - Guia rápido

### Tutoriais

**Análise Básica (5 min):**
1. Abrir dashboard
2. Ver métricas principais
3. Explorar Tab "Visão Geral"

**Análise Intermediária (15 min):**
1. Filtrar por categoria
2. Analisar padrões temporais
3. Identificar top produtos

**Análise Avançada (30 min):**
1. Análise de Pareto
2. Correlações entre categorias
3. Projeções financeiras
4. Exportar relatórios

## ✨ Diferenciais do Dashboard v4

| Funcionalidade | v3 | v4 |
|----------------|----|----|
| Categorização Automática | ❌ | ✅ |
| Subcategorias Detalhadas | ❌ | ✅ |
| Análise de Pareto | ❌ | ✅ |
| Projeções Financeiras | ❌ | ✅ |
| Correlação entre Categorias | ❌ | ✅ |
| Gráfico Waterfall | ❌ | ✅ |
| Heatmaps | ❌ | ✅ |
| Exportação Excel | CSV | CSV + Excel |
| Número de Tabs | 4 | 7 |
| Métricas | Básicas | Avançadas |

## 🏆 Conclusão

O **Dashboard v4** é uma ferramenta **profissional e completa** para análise de vendas, oferecendo:

✅ **Categorização inteligente** de produtos
✅ **10 categorias** e dezenas de subcategorias
✅ **7 tabs** de análise especializada
✅ **30+ métricas** e KPIs profissionais
✅ **15+ gráficos** interativos
✅ **Filtros avançados** e personalizáveis
✅ **Exportação** completa (CSV + Excel)
✅ **Performance otimizada** com cache
✅ **Design profissional** e intuitivo

---

**Desenvolvido com:** Python 🐍 | Streamlit 🎈 | Plotly 📊 | Pandas 🐼

**Versão:** 4.0
**Data:** 13/10/2025
**Status:** ✅ Produção

**Dashboard Online:** http://localhost:8501 🚀
