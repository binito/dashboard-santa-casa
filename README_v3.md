# Dashboard v3 - Análise Integrada de Vendas

## 📋 Visão Geral

O **Dashboard v3** é uma evolução do dashboard anterior, agora integrando dados de **três fontes diferentes**:

1. **Jogos Santa Casa** - Dados originais do dashboard anterior
2. **Vendas de Café** - Dados dos ficheiros Excel em `/home/jorge/Documentos/pos/pos_1`
3. **Outros Produtos** - Dados dos ficheiros CSV em `/home/jorge/Documentos/pos/pos_2` (focado em Totobola, categorizado como "Outros")

## 🚀 Como Utilizar

### Iniciar o Dashboard v3

```bash
cd /home/jorge/Documentos/Streamlit
source venv/bin/activate  # Se ainda não estiver ativado
streamlit run dashboard_v3.py
```

O dashboard estará disponível em: http://localhost:8501

### Manter o Dashboard Antigo (Recomendado)

O dashboard original (`dashboard.py`) **não foi alterado** e continua totalmente funcional:

```bash
streamlit run dashboard.py
```

## 📁 Estrutura de Ficheiros

```
/home/jorge/Documentos/Streamlit/
├── dashboard.py              # Dashboard original (intacto)
├── dashboard_v3.py           # Nova versão com dados integrados
├── data_loader_v3.py         # Módulo de carregamento de dados
└── README_v3.md             # Esta documentação

/home/jorge/Documentos/pos/
├── pos_1/
│   ├── 2023.xlsx            # Vendas de café 2023
│   ├── 2024.xlsx            # Vendas de café 2024
│   └── 2025.xlsx            # Vendas de café 2025
└── pos_2/
    ├── Mapas_Artigos-20241231.csv   # Outros produtos (2024)
    └── Mapas_Artigos-20251013.csv   # Outros produtos (2025)
```

## 🔧 Componentes Técnicos

### 1. `data_loader_v3.py`

Módulo responsável por carregar e processar dados de todas as fontes:

#### Classe `DataLoaderV3`

**Métodos principais:**

- `carregar_dados_santa_casa()` - Carrega dados dos jogos Santa Casa
- `carregar_vendas_cafe()` - Carrega vendas de café dos ficheiros Excel
- `carregar_outros_produtos()` - Carrega dados de outros produtos dos CSV
- `carregar_todos_dados()` - Carrega e retorna dados de todas as fontes
- `get_resumo_dados()` - Retorna resumo estatístico dos dados

**Exemplo de uso:**

```python
from data_loader_v3 import DataLoaderV3

loader = DataLoaderV3()
dados = loader.carregar_todos_dados()

# Acessar dados específicos
df_santa_casa = dados['santa_casa']
df_cafe = dados['cafe']
df_outros = dados['outros']
```

### 2. `dashboard_v3.py`

Dashboard Streamlit com análise integrada:

**Funcionalidades:**

- 📊 **Métricas Principais**: Total de vendas, média diária, dias com vendas, melhor dia
- 📈 **Análise por Fonte**: Comparação entre as três fontes de dados
- 📅 **Evolução Temporal**: Análise diária, semanal e mensal
- 🎯 **Análise Comparativa**: Gráficos comparativos entre fontes
- 📑 **Dados Detalhados**: Visualização e exportação de dados

**Filtros disponíveis:**

- Fonte de dados (Santa Casa / Café / Outros)
- Período (seleção de intervalo de datas)

## 📊 Dados Carregados

### Vendas de Café (pos_1)

**Fonte:** Ficheiros Excel (2023.xlsx, 2024.xlsx, 2025.xlsx)

**Estrutura:**
- Data de venda
- Código do produto
- Nome do produto
- Família/Subfamília
- Quantidade
- Valor Total (com IVA)

**Período coberto:** 2023-01-02 a 2025-05-31

**Total de registos:** 8.651

**Total vendas:** €62.431,42

### Outros Produtos - Totobola (pos_2)

**Fonte:** Ficheiros CSV (Mapas_Artigos-*.csv)

**Estrutura:**
- Data de venda
- Código (filtrado: 50010 = Totobola)
- Designação
- Quantidade
- Preço/Unidade
- Valor Total

**Nota:** Conforme solicitado, apenas as vendas da "Tab Totobola" são incluídas e categorizadas como "Outros" no dashboard.

**Período coberto:** 2024-01-02 a 2025-10-13

**Total de registos:** 533

**Total vendas:** €33.878,04

### Jogos Santa Casa

**Fonte:** Ficheiros TXT em `dados_vendas/`

**Nota:** Atualmente não há dados disponíveis nesta pasta. O dashboard está preparado para integrá-los quando estiverem disponíveis.

## 🎨 Visualizações Disponíveis

### Tab 1: Análise Comparativa
- Vendas mensais por fonte (gráfico de barras agrupadas)
- Distribuição de valores por fonte (box plot)

### Tab 2: Análise Temporal
- Vendas por dia da semana (gráfico de barras empilhadas)
- Vendas por trimestre (gráfico de barras agrupadas)

### Tab 3: Top Vendas
- Top 10 dias com mais vendas
- Top 10 meses com mais vendas
- Evolução diária do melhor mês

### Tab 4: Dados Detalhados
- Tabela completa de dados filtrados
- Opção de exportação para CSV

## 🔄 Próximos Passos

### Para integrar ao dashboard principal:

1. **Testar o dashboard v3** completamente
2. **Verificar todas as funcionalidades**
3. **Se tudo estiver OK:**
   - Fazer backup do dashboard.py atual: `cp dashboard.py dashboard_backup.py`
   - Integrar funcionalidades do v3 ao dashboard principal
   - Ou usar dashboard_v3.py como versão principal

### Melhorias futuras possíveis:

- [ ] Adicionar análise de correlações entre fontes
- [ ] Implementar previsões para vendas de café e outros
- [ ] Criar relatórios automáticos em PDF
- [ ] Adicionar comparação YoY para cada fonte
- [ ] Implementar alertas de performance
- [ ] Adicionar filtros por produto específico

## 🐛 Troubleshooting

### Erro: "Nenhum dado encontrado"

**Solução:** Verificar se os caminhos dos ficheiros estão corretos:
- `/home/jorge/Documentos/pos/pos_1/*.xlsx`
- `/home/jorge/Documentos/pos/pos_2/*.csv`

### Erro: "Module not found"

**Solução:** Ativar o ambiente virtual:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Dashboard não inicia

**Solução:** Verificar se a porta 8501 está livre:
```bash
lsof -i :8501
# Se estiver ocupada, matar o processo ou usar outra porta:
streamlit run dashboard_v3.py --server.port 8502
```

## 📝 Notas Importantes

1. **Dados Santa Casa:** O módulo está preparado para carregar dados dos jogos Santa Casa quando estiverem disponíveis na pasta `dados_vendas/`.

2. **Performance:** Os dados são cacheados automaticamente por 1 hora (`@st.cache_data(ttl=3600)`), melhorando a performance.

3. **Encoding:** Os ficheiros CSV são lidos com encoding `latin1` devido aos caracteres especiais em português.

4. **Filtros de dados:** No `pos_1`, linhas com "Totais" são automaticamente excluídas para evitar duplicação de valores.

5. **Classificação:** Conforme solicitado, os dados do código 50010 (Totobola) do `pos_2` são classificados como "Outros Produtos" no dashboard.

## 🤝 Suporte

Para questões ou melhorias, verificar o código fonte em:
- [data_loader_v3.py](data_loader_v3.py)
- [dashboard_v3.py](dashboard_v3.py)

---

**Versão:** 3.0
**Data:** 13/10/2025
**Autor:** Dashboard desenvolvido com Claude Code
