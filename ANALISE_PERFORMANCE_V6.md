# Análise de Performance - Dashboard v6 (Café Martins)

**Data da Análise:** 2025-11-14  
**Arquivo:** `/home/jorge/Documentos/Streamlit/dashboard_v6.py`  
**Tamanho:** 3.462 linhas de código

---

## 1. PRINCIPAIS OPERAÇÕES LENTAS IDENTIFICADAS

### 1.1 Carregamento de Dados

| Linha | Função | Tipo | Impacto | Status Cache |
|-------|--------|------|--------|-------------|
| 196-202 | `carregar_dados()` | Carregamento integrado com custos | CRÍTICO - Chamado na linha 1433 | **CACHEADO** (TTL 1800s) |
| 781-824 | `carregar_dados_santa_casa()` | Carregamento CSV Santa Casa | ALTO - Conversão de números | **CACHEADO** (TTL 1800s) |
| 827-845 | `carregar_objetivos()` | Carregamento de CSV | MÉDIO - Não cacheado | **NÃO CACHEADO** |

**Observações Críticas:**
- A função `carregar_dados()` usa `DataLoaderV5()` que integra dados de múltiplas fontes
- Em `carregar_dados_santa_casa()` (linha 814): 44 chamadas `.apply(converter_numero)` em loop - **POTENCIAL GARGALO**
- `carregar_objetivos()` é chamada na linha 1282 e **NÃO está cacheada** - deveria estar

---

## 2. OPERAÇÕES DE TRANSFORMAÇÃO E LOOPING

### Iterações Custosas Identificadas (44 total)

| Linha | Tipo | Descrição | Frequência |
|-------|------|-----------|-----------|
| 685 | `.iterrows()` | Loop em análise_rent para exportação Excel | 1 vez por relatório |
| 1291 | `.iterrows()` | Loop em vendas_por_jogo (Santa Casa) | 1 vez por tab |
| 1737 | `.iterrows()` | Loop nas 8 categorias top | Em cada visualização |
| 2599 | `.iterrows()` | Loop em vendas_mes_cat para heatmap | Em cada visualização |
| 3130 | `.iterrows()` | Loop top_rent para display | 1 vez por tab |
| 3149 | `.iterrows()` | Loop bottom_rent para display | 1 vez por tab |

**Aplicações (38 ocorrências):**
- Linhas 469, 990, 999, 1037, 1046, 1143, 1144, 1201-1204, 1269-1273, 1763, 1791, 1881, 1912-1913, 1955, 1965, 2028, 2054, 2091, 2105, 2317, 2342, 2358, 2367, 2490, 2540, 2549, 2574-2578

**Exemplo de código ineficiente (linha 814):**
```python
for col in numeric_cols:
    if col in df.columns:
        def converter_numero(val):
            val_str = str(val)
            if ',' in val_str:
                val_str = val_str.replace('.', '').replace(',', '.')
            try:
                return float(val_str)
            except:
                return 0.0
        
        df[col] = df[col].apply(converter_numero)  # SLOW!
```

---

## 3. GRÁFICOS RENDERIZADOS

### Contagem Total de Gráficos

- **Chamadas `st.plotly_chart()`:** 41 ocorrências
- **Criações `fig = px.*`:** 21+ criações diretas
- **Gráficos Plotly `go.Figure()`:** 20+ criações
- **Gráficos Excel (openpyxl):** 3 gráficos por relatório

### Distribuição por Tab

| Tab | Gráficos | Descrição |
|-----|----------|-----------|
| Tab 1 - Visão Geral | ~8 gráficos | Métricas, categorias, produtos, evolução |
| Tab 2 - Por Categoria | ~6 gráficos | Subcategorias, produtos, evolução |
| Tab 3 - Análise Temporal | ~5 gráficos | Evolução diária, semanal, mensal, trimestral |
| Tab 4 - Análise Comparativa | ~4 gráficos | YoY, MoM, crescimento |
| Tab 5 - Distribuição de Vendas | ~3 gráficos | Pizza, dispersão, tabelas |
| Tab 6 - Análise de Ticket Médio | ~3 gráficos | Distribuição, fonte, categoria |
| Tab 7 - Análise de Rentabilidade | ~5 gráficos | Custos, margens, produtos top |
| Tab 8 - Break-Even & Análise | ~2 gráficos | Waterfall, margem de segurança |
| Tab 9 - Análise Detalhada Rentabilidade | ~3 gráficos | Margem, scatter, tabelas |
| Tab 10 - Exportação | Botões (Excel + CSV) | - |
| Tab 11 - Jogos Santa Casa | ~4 gráficos | Vendas, distribuição, objetivos |

**Total aproximado: 43-50 gráficos por execução**

---

## 4. ANÁLISE DE CACHE

### Funções com Cache

```
✓ @st.cache_data(ttl=1800)
  - Linha 195: carregar_dados()
  - Linha 780: carregar_dados_santa_casa()
```

### Funções SEM Cache (Deveriam ter)

```
✗ Linha 827: carregar_objetivos()
  - Chamada em linha 1282
  - Chamada em várias tabs de Santa Casa
  - Recomendação: Adicionar @st.cache_data(ttl=3600)

✗ Linha 370: criar_grafico_pizza()
✗ Linha 393: criar_grafico_barras()
✗ Linha 418: criar_grafico_linha()
✗ Linha 439: criar_heatmap()
✗ Linha 461: criar_grafico_waterfall()
  - Estas funções são "helper" e recalculam em cada re-run
  - Não é crítico cachear, mas a filtragem dos dados poderia ser cacheada
```

### Problema: Re-execução sem Cache

- **Filtros alteram dados constantemente** → filtro_dados (linha 222) retorna novos DataFrames
- **Widgets interativos** (selectbox, multiselect) disparam re-runs
- Cada re-run recalcula todos os gráficos desde o início

---

## 5. DADOS CARREGADOS

### DataFrames Principais

| Nome | Origem | Linhas Aprox. | Colunas | Cache |
|------|--------|--------------|---------|-------|
| `df` (vendas) | `DataLoaderV5()` | 5.000-50.000* | 10+ (Data, Valor, Qtd, Categoria, etc.) | SIM (1800s) |
| `df_jogos` | CSV Santa Casa | 1.000-10.000* | 6+ (Data, Categoria, Vendas ilíquidas, Prémios, etc.) | SIM (1800s) |
| `df_objetivos` | CSV semanais | 10-50 | 2 (Jogo, Objetivo) | NÃO |

*Estimados - dependem de dados reais

### Transformações de Dados Dentro do Dashboard

1. **Filtro de dados** (linha 222-248): cópia + múltiplos filtros boolean
2. **Agrupamentos**: `groupby()` em ~30 locais diferentes
3. **Agregações**: `.sum()`, `.mean()`, `.count()`, `.agg()`
4. **Pivots**: Possíveis transformações de índice/colunas para heatmaps

---

## 6. RECOMENDAÇÕES DE OTIMIZAÇÃO

### Prioridade CRÍTICA (Implementar YA)

1. **Cachear função `carregar_objetivos()`** (Linha 827)
   ```python
   @st.cache_data(ttl=3600)
   def carregar_objetivos():
   ```
   - Ganho esperado: ~50-100ms por re-run
   - Facilidade: 1 linha
   - Impacto: MÉDIO

2. **Reescrever conversão numérica em Santa Casa** (Linha 814)
   ```python
   # INEFICIENTE (atual):
   df[col] = df[col].apply(converter_numero)
   
   # EFICIENTE (proposto):
   df[col] = pd.to_numeric(
       df[col].astype(str)
       .str.replace('.', '')
       .str.replace(',', '.'),
       errors='coerce'
   ).fillna(0)
   ```
   - Ganho esperado: ~200-500ms para 10k linhas
   - Facilidade: 2 minutos
   - Impacto: ALTO

3. **Consolidar cálculos de agregação** (Linhas 1730-1737 e similares)
   - Fazer groupby UMA VEZ e reutilizar
   - Evitar múltiplos `.groupby()` na mesma coluna
   - Ganho esperado: ~300-800ms por tab
   - Facilidade: 30 minutos
   - Impacto: ALTO

### Prioridade ALTA (Implementar em breve)

4. **Reduzir número de gráficos ativos**
   - Usar `st.tabs()` (já está implementado)
   - Gráficos são renderizados mesmo em tabs não visíveis
   - Solução: Usar `st.plotly_chart(..., use_container_width=True)` está bem feito
   - Ganho esperado: ~500-1000ms (eliminar re-render de tabs invisíveis)
   - Dificuldade: MÉDIA (requer refactoring)
   - Impacto: MÉDIO-ALTO

5. **Cachear dados filtrados intermediários**
   ```python
   @st.cache_data(ttl=300)
   def obter_dados_filtrados(hash_dos_filtros):
       # Calcular dados filtrados uma única vez
       return dados_processados
   ```
   - Ganho esperado: ~1-2 segundos
   - Dificuldade: MÉDIA
   - Impacto: ALTO

6. **Usar `st.cache_resource` para DataLoaderV5**
   ```python
   @st.cache_resource
   def carregar_loader():
       return DataLoaderV5()
   ```
   - Reutilizar a mesma instância
   - Ganho esperado: ~100-200ms
   - Dificuldade: BAIXA
   - Impacto: MÉDIO

### Prioridade MÉDIA (Otimizações menores)

7. **Eliminar conversão de Data repetida** (Linha 575, 513, etc.)
   - Fazer uma vez no carregamento

8. **Batch processing para loops**.iterrows()**
   - Usar operações vetorizadas do NumPy/Pandas
   - Ganho esperado: ~100-300ms por loop

9. **Simplificar formatação (formatar_moeda)**
   - Função chamada 40+ vezes por render
   - Considerar aplicar em batch antes de render

---

## 7. ANÁLISE RESUMIDA DE PERFORMANCE

### Cronograma Estimado de Execução (Sem Otimizações)

```
Carregamento de dados:        ~500-1000ms  (cacheado)
Filtros e transformações:     ~300-800ms
Cálculo de métricas:          ~200-400ms
Renderização de 43+ gráficos: ~1500-3000ms  ← GARGALO PRINCIPAL
Renderização do layout:       ~200-300ms
───────────────────────────────────────────
TOTAL (primeiro load):        ~2700-5500ms

Re-run com filtro diferente:  ~800-1500ms  (dados cacheados)
```

### Com Otimizações Recomendadas

```
Esperado após implementar recomendações:
- Cache de objetivos:         -50ms
- Conversão numérica:         -200-500ms
- Consolidação de groupby:    -300-800ms
- Dados filtrados cacheados:  -400-1000ms
───────────────────────────────────────────
TOTAL esperado:               ~1700-2700ms (primeira vez)
                              ~400-800ms (re-runs)
```

**Melhoria esperada: 40-50% de redução no tempo de resposta**

---

## 8. CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Adicionar `@st.cache_data` a `carregar_objetivos()`
- [ ] Reescrever conversão numérica em `carregar_dados_santa_casa()`
- [ ] Consolidar cálculos `.groupby()` redundantes
- [ ] Implementar cache para dados filtrados intermediários
- [ ] Usar `@st.cache_resource` para DataLoaderV5
- [ ] Revisar e eliminar loops `.iterrows()` desnecessários
- [ ] Testes de performance com `streamlit run --logger.level=debug`
- [ ] Monitorar tempo de execução com `st.write(f"Tempo: {time.time() - start}")

---

## 9. CONCLUSÕES

O dashboard **v6** é funcional mas tem **potencial significativo de otimização**:

- ✓ Cache está bem implementado para dados principais
- ✓ Layout com tabs reduz visualização de gráficos
- ✗ 43+ gráficos podem ser pesados em conexões lentas
- ✗ Conversão numérica ineficiente (Santa Casa)
- ✗ Múltiplos `.groupby()` na mesma coluna
- ✗ `carregar_objetivos()` não cacheada

**Recomendação:** Implementar as 3 primeiras prioridades CRÍTICAS para ganho imediato de 30-40% em performance.

