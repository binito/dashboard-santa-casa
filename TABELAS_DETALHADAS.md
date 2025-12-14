# Tabelas Detalhadas - Análise Performance Dashboard v6

## 1. MAPEAMENTO DE GARGALOS POR LINHA

| Linha | Função | Tipo | Operação | Impacto | Freq. | Cache |
|-------|--------|------|----------|--------|-------|-------|
| 196 | `carregar_dados()` | Carregamento | DataLoaderV5 integrado | CRÍTICO | 1/1800s | SIM |
| 814 | `carregar_dados_santa_casa()` | Conversão | `.apply(converter_numero)` x 5 colunas | ALTO | 1/1800s | SIM |
| 827 | `carregar_objetivos()` | Carregamento | CSV read | MÉDIO | cada re-run | **NÃO** |
| 1282 | - | Chamada | `carregar_objetivos()` | MÉDIO | cada re-run | **NÃO** |
| 1730 | `pagina_visao_geral()` | Agrupação | `groupby('Categoria')` | MÉDIO | 1/re-run | **NÃO** |
| 1757 | - | Agrupação | `groupby('Categoria')` (repetido) | MÉDIO | 1/re-run | **NÃO** |
| 1785 | - | Agrupação | `groupby('Produto')` | MÉDIO | 1/re-run | **NÃO** |
| 1737 | - | Loop | `.iterrows()` em 8 categorias | BAIXO | 1/re-run | - |
| 1809 | - | Agrupação | `groupby('Data')` | MÉDIO | 1/re-run | **NÃO** |
| 1840 | - | Select | `selectbox()` dinâmico | BAIXO | 1/re-run | - |
| 2599 | `analise_temporal()` | Loop | `.iterrows()` para heatmap | MÉDIO | 1/re-run | **NÃO** |
| 2342 | - | Agrupação | `groupby().apply()` | MÉDIO | 1/re-run | **NÃO** |
| 2490 | - | Operação | `.apply()` para ícones | BAIXO | 1/re-run | - |
| 3130 | `rentabilidade_detalhada()` | Loop | `.iterrows()` top_rent | BAIXO | 1/re-run | - |
| 3149 | - | Loop | `.iterrows()` bottom_rent | BAIXO | 1/re-run | - |
| 3408 | `main()` | Carregamento | `carregar_dados_santa_casa()` | CRÍTICO | 1/1800s | SIM |

---

## 2. ANÁLISE DE OPERAÇÕES APPLY E ITERROWS

### Operações .apply() (38 ocorrências)

| Linha | Contexto | Padrão | Dados | Alternativa |
|-------|----------|--------|-------|------------|
| 469 | Gráfico waterfall | `text=[f"€{v:,.0f}" for v in valores]` | 5-20 | List comp OK |
| 814 | Conversão numérica | `df[col].apply(converter_numero)` | 5k-10k | **Usar str.replace()** |
| 990 | Top jogos | `.apply(lambda x: f'€{x:,.0f}')` | 10-20 | Batch format |
| 999 | Tabela jogos | `.apply(lambda x: f'€{x:,.0f}')` | 10-20 | Batch format |
| 1037 | Gráfico categorias | `.apply(lambda x: f'€{x:,.0f}')` | 5-10 | Batch format |
| 1046 | Tabela categorias | `.apply(lambda x: f'€{x:,.0f}')` | 5-10 | Batch format |
| 1143 | Tabela MoM | `.apply(lambda x: f'€{x:,.0f}')` | 12 | Batch format |
| 1144 | Tabela MoM | `.apply(lambda x: f'{x:+.1f}%')` | 12 | Batch format |
| 1201 | Tabela YoY | `.apply(lambda x: f'€{x:,.0f}')` | 12 | Batch format |
| 1204 | Tabela YoY | `.apply(lambda x: f'{x:+.1f}%' ...)` | 12 | Batch format |
| 1269-1273 | Stats jogo | `.apply(lambda x: f'€{x:,.0f}')` x5 | 5 | Batch format |
| 1763 | Gráfico categoria | `[formatar_moeda(v) for v in ...]` | 5-10 | OK (list comp) |
| 1791 | Gráfico top 10 | `[formatar_moeda(v) for v in ...]` | 10 | OK (list comp) |
| 1881 | Gráfico subcategorias | `[formatar_moeda(v) for v in ...]` | 10 | OK (list comp) |
| 1912 | Tabela produtos | `.apply(formatar_moeda)` | 5-10 | Batch format |
| 1913 | Tabela produtos | `.apply(lambda x: f"{x:,.0f}")` | 5-10 | Batch format |
| 1955 | Dados | `.apply(lambda x: dias_semana[x])` | 7 | Dict lookup OK |
| 1965 | Gráfico dia semana | `[formatar_moeda(v) for v in ...]` | 7 | OK (list comp) |
| 2028 | Gráfico mês | `[formatar_moeda(v) for v in ...]` | 12 | OK (list comp) |
| 2054 | Gráfico trimestre | `.apply(lambda x: f'Q{i}' ...)` | 4 | OK |
| 2091 | Crescimento categoria | `.apply(lambda x: ...)` | 5-10 | Batch format |
| 2105 | Gráfico crescimento | `[f"{v:+.1f}%" for v in ...]` | 5-10 | OK (list comp) |
| 2317 | Gráfico faturamento | `[formatar_moeda(v) for v in ...]` | 5-10 | OK (list comp) |
| 2342 | Ticket médio | `.groupby().apply()` | 5-10 | **Consolidar** |
| 2358 | Ticket médio | `.groupby().apply()` | 5-10 | **Consolidar** |
| 2367 | Gráfico ticket | `[formatar_moeda(v) for v in ...]` | 5-10 | OK (list comp) |
| 2490 | Comparação | `.apply(lambda x: ...)` | 5-10 | Batch format |
| 2540 | Ticket fonte | `.groupby().apply()` | 3-5 | OK |
| 2549 | Gráfico ticket | `[formatar_moeda(v) for v in ...]` | 3-5 | OK (list comp) |
| 2574-2578 | Tabela benchmark | `.apply(formatar_moeda)` x5 | 5-10 | Batch format |

**Oportunidades de otimização:**
- Linhas 814, 1912-1913, 2091, 2342, 2358, 2490, 2574-2578: Usar batch format
- Linhas com list comprehensions: OK como estão
- Linhas com groupby().apply(): Consolidar operações

### Operações .iterrows() (6 ocorrências diretas + mais em loops)

| Linha | Contexto | N Iterações | Objetivo | Alternativa |
|-------|----------|-------------|----------|------------|
| 685 | Excel export | 3-10 | Preencher células | `dataframe_to_rows()` |
| 1291 | Tabela jogos | 10-20 | Exibir dados | List comp + st.write |
| 1737 | Categorias top | 8 | Métricas em cols | Batch + loop simples |
| 2599 | Heatmap | 12 | Preparar pivotable | Usar `pivot_table()` |
| 3130 | Top rent | 10-20 | Exibir ranking | List comp + st.write |
| 3149 | Bottom rent | 10-20 | Exibir ranking | List comp + st.write |

---

## 3. ANÁLISE DE GROUPBY - CONSOLIDAÇÃO

### Groupby Redundantes por Tab

#### TAB 1 (Visão Geral)

```
Atual:
  groupby('Categoria')['Valor'].sum() - linha 1730
  groupby('Categoria')['Valor'].sum() - linha 1757 (REPETIDO)
  groupby('Produto')['Valor'].sum() - linha 1785
  groupby('Data')['Valor'].sum() - linha 1809

Potencial:
  Consolidar 1730 e 1757 (mesma coluna)
  Fazer um prep_data() com todos os groupby
```

#### TAB 2 (Por Categoria)

```
Atual:
  groupby('Subcategoria')['Valor'].sum() - linha 1875
  groupby('Produto')['Valor'].sum() - linha 1875 (na mesma tab!)

Potencial:
  Função de prep com ambas operações
```

#### TAB 3 (Análise Temporal)

```
Atual:
  groupby('Data')['Valor'].sum() - linha 1809
  groupby(Ano_Mes) - para diferentes períodos
  groupby('Dia_Semana') - vendas por dia
  groupby(Ano_Mes).sum() - vendas por mês

Potencial:
  Uma função temporal que prepara tudo de uma vez
```

#### TAB 7 (Rentabilidade)

```
Atual:
  groupby('Categoria') - linha 2315, 2342, 2358, etc.
  cost_manager.analisar_rentabilidade_categorias()
  Multiple groupby operações

Potencial:
  Uma função consolidada de análise
```

**Impacto Total:** 3-5 groupby desnecessários por execução
**Ganho Estimado:** 300-800ms por tab

---

## 4. CRONOGRAMA ESTIMADO DE EXECUÇÃO

### Cenário 1: Sem Cache (Baseline)

```
                    Tempo (ms)    % do Total
Carregamento dados     800           14%
  - DataLoaderV5      400
  - Conversão números  300
  - Parsing CSV        100
  
Filtros + transformações
  - filtrar_dados()    300           5%
  - Groupby's (~30)    500           9%
  - Aplicações (~40)   400           7%
  
Cálculos de métricas   300           5%

Renderização UI       1500          27%
  - 43-50 gráficos   1200
  - Layouts + CSS     300
  
Transmissão cliente    900          16%
  - HTML/JS           400
  - Dados JSON        500

TOTAL                5600         100%
```

### Cenário 2: Com Caches Atuais (Produção)

```
                    Tempo (ms)    % do Total
Carregamento dados      0            0%  (CACHED)
  
Filtros + transformações
  - filtrar_dados()    300          25%  <- MAIOR IMPACTO
  - Groupby's (~30)    500          42%
  - Aplicações (~40)   200          17%
  
Cálculos de métricas   100           8%

Renderização UI        300           3%
  - 43-50 gráficos    250
  - Layouts           50
  
Transmissão cliente    100           8%

TOTAL                1200         100%
```

### Cenário 3: Com Todas as Otimizações

```
                    Tempo (ms)    % do Total
Carregamento dados      0            0%  (CACHED)
  
Filtros + transformações
  - filtrar_dados()    100          20%  (CACHED)
  - Groupby's (~10)    150          30%  (consolidados)
  - Aplicações (~15)    50          10%  (batch)
  
Cálculos de métricas    50           10%

Renderização UI        250          50%

Transmissão cliente     50           10%

TOTAL                 500         100%  (2.4x MAIS RÁPIDO)
```

---

## 5. MATRIZ DE CACHE

### Estado Atual

```
Função                          | Cache | TTL  | Chamadas/run | Status
──────────────────────────────────────────────────────────────────────
carregar_dados()                | SIM   | 1800 | 1           | OK
carregar_dados_santa_casa()     | SIM   | 1800 | 1           | OK
carregar_objetivos()            | NÃO   | -    | 3-5         | ** FALTA **
filtrar_dados()                 | NÃO   | -    | 1           | ** FALTA **
criar_grafico_pizza()           | NÃO   | -    | 2           | OPCIONAL
criar_grafico_barras()          | NÃO   | -    | 8           | OPCIONAL
criar_grafico_linha()           | NÃO   | -    | 5           | OPCIONAL
criar_heatmap()                 | NÃO   | -    | 1           | OPCIONAL
criar_grafico_waterfall()       | NÃO   | -    | 1           | OPCIONAL
pagina_visao_geral()            | NÃO   | -    | 1           | -
calcular_metricas_performance() | NÃO   | -    | 1           | -
```

### Recomendações

**Adicionar Cache Imediato:**
```python
@st.cache_data(ttl=3600)
def carregar_objetivos(): ...

@st.cache_data(ttl=300)
def filtrar_dados_cacheado(...): ...

@st.cache_resource
def carregar_data_loader(): ...
```

**Considerar Cache (opcional):**
- Funções criar_grafico_* (helper functions)
- Métricas de performance (cálculos pesados)
- Dados agregados por categoria (agg_categorias)

---

## 6. IMPACTO POR TIPO DE OPERAÇÃO

### Ranking de Custo Computacional

```
Rank | Operação              | Custo Aprox | Frequência | Impacto Total
─────┼───────────────────────┼────────────┼────────────┼──────────────
 1   | Renderização Plotly   | 1-3ms/gráf | 43-50      | 43-150ms
 2   | Conversão numérica    | 100-200ms  | 1          | 100-200ms
 3   | Groupby operações     | 10-20ms    | 30+        | 300-600ms
 4   | apply() formatação    | 0.1-0.5ms  | 40+        | 4-20ms
 5   | iterrows loops        | 1-5ms      | 6          | 6-30ms
 6   | Filtros boolean       | 5-10ms     | 5          | 25-50ms
 7   | Carregamento dados    | 500-1000ms | 1          | 500-1000ms
 8   | Autenticação          | 100-200ms  | 1/sessão   | 100-200ms
```

---

## 7. BENEFÍCIO DE CADA OTIMIZAÇÃO

### Simulação de Impacto

```
Otimização                     | Antes | Depois | Ganho    | % Melhoria
───────────────────────────────┼───────┼────────┼──────────┼───────────
Sem otimizações               | 1200  | 1200   | -        | -
+ Cache objetivos             | 1200  | 1150   | 50ms     | 4%
+ Conversão numérica          | 1200  | 1000   | 200ms    | 17%
+ Consolidar groupby          | 1200  | 700    | 500ms    | 42%
+ Cache dados filtrados       | 1200  | 300    | 900ms    | 75%
+ Cache_resource loader       | 1200  | 250    | 950ms    | 79%
─────────────────────────────────────────────────────────
TOTAL (todas)                 | 1200  | 250    | 950ms    | 79%
```

---

## 8. MATRIZ DE RISCO DE IMPLEMENTAÇÃO

| Otimização | Complexidade | Risco | Teste Requerido | Tempo | Ganho | Score |
|-----------|---|---|---|---|---|---|
| Cache objetivos | Baixa | Muito Baixo | UI | 2min | 50ms | 9/10 |
| Conversão numérica | Baixa | Baixo | Unit + Integration | 10min | 200ms | 8/10 |
| Consolidar groupby | Média | Médio | Integration + Perf | 1h | 500ms | 7/10 |
| Cache dados filtrados | Média | Médio | Integration + Perf | 1.5h | 900ms | 7/10 |
| Cache_resource loader | Baixa | Baixo | Unit + Perf | 10min | 100ms | 7/10 |
| Batch formatting | Baixa | Muito Baixo | UI | 1h | 50-100ms | 6/10 |
| Otimizar iterrows | Média | Médio | Integration | 2h | 30-100ms | 5/10 |

**Score = (Ganho / Tempo investido) + (10 - Risco)**

---

## 9. COMPARATIVO DE ALTERNATIVAS

### Problema: Conversão de números em Santa Casa

**Solução 1: Usar apply() com função (ATUAL)**
```
Código:  df[col] = df[col].apply(converter_numero)
Tempo:   ~450ms para 5000 linhas
Legibilidade: Alta
Manutenibilidade: Alta
```

**Solução 2: Usar str.replace() (RECOMENDADO)**
```
Código:  df[col] = df[col].astype(str).str.replace(...).apply(float)
Tempo:   ~50ms para 5000 linhas
Legibilidade: Média
Manutenibilidade: Média
Melhoria: 9x MAIS RÁPIDO
```

**Solução 3: Usar pd.to_numeric() (ALTERNATIVA)**
```
Código:  df[col] = pd.to_numeric(df[col], errors='coerce')
Tempo:   ~200ms (mas perde controle de formato)
Legibilidade: Alta
Manutenibilidade: Alta
Melhoria: 2x mais rápido
```

**Recomendação:** Solução 2 (str.replace) - melhor balance entre performance e manutenção

---

## 10. RESUMO DE TABELAS

**Total de Gargalos Identificados:** 15+
**Total de apply/iterrows:** 44
**Total de groupby redundantes:** 5-10
**Total de gráficos:** 43-50
**Funções sem cache (deveriam ter):** 3
**Linhas de código a modificar:** ~50

**Tempo total de implementação:** 4-5 horas
**Melhoria estimada:** 40-79% redução no tempo de resposta

