# Dashboard v5 - Café Martins com Gestão de Custos 💰

## 🎯 Novidades da Versão 5

Dashboard profissional com análise completa de **vendas, custos operacionais e rentabilidade**.

### ✨ Novas Funcionalidades

#### 📦 Sistema de Gestão de Custos
- **Custos de Produtos (COGS)**: Custo unitário de cada produto
- **Custos Operacionais**: Renda, salários, impostos, contabilista, etc.
- **Cálculo Automático de Margens**: Margem bruta e líquida

#### 🆕 3 Novas Tabs de Análise

**1. Tab 8 - 💸 Análise de Custos**
- Distribuição de custos (COGS vs Operacionais)
- Detalhamento de custos operacionais por categoria
- Custos de produtos por categoria
- Gráficos interativos de custos

**2. Tab 9 - 📊 Rentabilidade & Margens**
- Lucro bruto e líquido
- Margens por categoria
- Top 10 produtos mais/menos rentáveis
- Análise de produtos vs objetivo de margem
- Scatter plot: Vendas vs Margem

**3. Tab 10 - 🎯 Break-Even Analysis**
- Ponto de equilíbrio (break-even point)
- Margem de segurança
- Dias para atingir break-even
- Gráfico de break-even interativo
- Análise de sensibilidade
- Recomendações estratégicas automáticas

---

## 📁 Estrutura de Arquivos

### Módulos Principais
```
dashboard_v5.py          → Dashboard principal com 10 tabs
cost_manager.py          → Gestor de custos e rentabilidade
data_loader_v5.py        → Carregador de dados com custos integrados
product_categorizer.py   → Categorizador de produtos (v4)
```

### Dados de Custos
```
dados_custos/
├── custos_produtos.csv      → Custos de cada produto
├── custos_operacionais.csv  → Custos fixos mensais
└── margens_categorias.csv   → Margens objetivo por categoria
```

---

## 💡 Exemplo de Dados

### Custos de Produtos
| Produto | Tipo_Compra | Preco_Compra | Rendimento | Custo_Unitario | Preco_Venda | Margem_Bruta |
|---------|-------------|--------------|------------|----------------|-------------|--------------|
| Café    | Kg (40,40€) | 40.40        | 131.58     | 0.307          | 0.70        | 56.14%       |
| Imperial| Barril 30L  | 45.00        | 200        | 0.225          | 1.10        | 79.55%       |

**Cálculo da Imperial:**
- Barril 30L = €45
- 1 Imperial = 0,15L → 200 imperiais por barril
- Custo unitário = €45 ÷ 200 = €0,225
- Margem = (€1,10 - €0,225) ÷ €1,10 = 79,55%

### Custos Operacionais (valores genéricos)
| Categoria    | Subcategoria       | Valor_Mensal | Tipo     |
|--------------|-------------------|--------------|----------|
| Instalações  | Renda             | 500.00       | Fixo     |
| RH           | Ordenado          | 1000.00      | Fixo     |
| RH           | Segurança Social  | 237.50       | Fixo     |
| Serviços     | Contabilista      | 150.00       | Fixo     |
| Serviços     | Eletricidade      | 200.00       | Variável |

**Total Custos Operacionais Mensais: €2.867,50**

---

## 🚀 Como Usar

### 1. Instalar Dependências
```bash
pip install streamlit pandas plotly numpy openpyxl
```

### 2. Executar Dashboard v5
```bash
streamlit run dashboard_v5.py --server.port 8503
```

### 3. Aceder ao Dashboard
```
http://localhost:8503
```

---

## 📊 Funcionalidades por Tab

### Tabs 1-7 (Herdadas do v4)
1. **Visão Geral**: KPIs principais e evolução
2. **Análise por Categoria**: Detalhamento por categoria
3. **Análise Temporal**: Vendas por dia/semana/mês
4. **Performance & KPIs**: Análise de Pareto, correlações
5. **Análise Financeira**: Projeções e waterfall
6. **Comparação & Benchmarks**: Comparações entre períodos
7. **Dados Detalhados**: Exportação CSV/Excel

### Tabs 8-10 (NOVAS no v5)

#### Tab 8 - Análise de Custos 💸
- **KPIs**: Receita, COGS, Custos Operacionais, Custo Total
- **Gráficos**:
  - Pizza: Distribuição COGS vs Operacionais
  - Barras: Custos operacionais por categoria
  - Barras: COGS por categoria de produto
- **Tabela**: Detalhamento completo de custos

#### Tab 9 - Rentabilidade & Margens 📊
- **KPIs**: Lucro Bruto, Lucro Líquido, Margem Bruta %, Margem Líquida %
- **Análise por Categoria**:
  - Margens vs objetivos
  - Status (✅ Acima / ⚠️ Abaixo / ➡️ No Alvo)
- **Produtos**:
  - Top 10 mais rentáveis
  - Top 10 menos rentáveis
  - Classificação automática (⭐ Estrela / ⚠️ Descontinuar)

#### Tab 10 - Break-Even Analysis 🎯
- **Análise de Ponto de Equilíbrio**:
  - Custos fixos mensais
  - Vendas necessárias para break-even
  - Margem de contribuição
  - Margem de segurança
- **Gráficos**:
  - Break-even point visual
  - Análise de sensibilidade
- **Recomendações Estratégicas Automáticas**:
  - 🚨 Alerta se abaixo do break-even
  - ⚠️ Aviso se margem de segurança < 20%
  - ✅ Confirmação se operação saudável

---

## 🔧 Personalização

### Adicionar Novos Produtos
Editar `dados_custos/custos_produtos.csv`:
```csv
Produto,Categoria,Tipo_Compra,Unidade_Compra,Preco_Compra,Rendimento,Custo_Unitario,Preco_Venda,Margem_Bruta
Novo Produto,CATEGORIA,Tipo,Unidade,10.00,50,0.20,1.50,86.67%
```

### Atualizar Custos Operacionais
Editar `dados_custos/custos_operacionais.csv`:
```csv
Categoria,Subcategoria,Valor_Mensal,Tipo,Notas
Nova Categoria,Nova Despesa,100.00,Fixo,Descrição
```

### Ajustar Margens Objetivo
Editar `dados_custos/margens_categorias.csv`:
```csv
Categoria,Margem_Objetivo,IVA_Aplicavel,Custo_Medio_Estimado
CAFETARIA,70%,13%,0.40
```

---

## 📈 Métricas Calculadas

### Margens
- **Margem Bruta** = (Receita - COGS) / Receita × 100%
- **Margem Líquida** = (Receita - COGS - Custos Operacionais) / Receita × 100%

### Break-Even
- **Vendas Break-Even** = Custos Fixos / (Margem de Contribuição % / 100)
- **Margem de Segurança** = (Vendas Atuais - Vendas Break-Even) / Vendas Atuais × 100%

### Rentabilidade
- **Lucro Bruto** = Receita - COGS
- **Lucro Líquido** = Lucro Bruto - Custos Operacionais
- **ROI** = (Lucro Líquido / Custos Operacionais) × 100%

---

## 🎨 Diferenciais do v5

✅ **Gestão Completa de Custos**
✅ **Análise de Rentabilidade por Produto**
✅ **Break-Even Analysis Automático**
✅ **Recomendações Estratégicas**
✅ **Gráficos Interativos de Custos**
✅ **Cálculo Automático de Margens**
✅ **Análise de Produtos Problemáticos**
✅ **Projeções Financeiras Avançadas**

---

## 🔐 Autenticação

O dashboard requer autenticação. Credenciais em `config.yaml`.

---

## 📝 Notas Técnicas

- **Cache**: 30 minutos (1800s)
- **Porta**: 8503 (v4 usa 8501, original usa 8502)
- **Dados**: Integração automática de 3 fontes
- **Performance**: Otimizado para 10.000+ transações

---

## 🆚 Comparação de Versões

| Funcionalidade           | v4  | v5  |
|--------------------------|-----|-----|
| Tabs de Análise          | 7   | 10  |
| Gestão de Custos         | ❌  | ✅  |
| Análise de Rentabilidade | ❌  | ✅  |
| Break-Even Analysis      | ❌  | ✅  |
| Categorização Produtos   | ✅  | ✅  |
| Integração 3 Fontes      | ✅  | ✅  |
| Autenticação             | ✅  | ✅  |

---

## 🚧 Próximos Passos

1. Preencher dados reais de custos
2. Ajustar margens objetivo por categoria
3. Configurar alertas automáticos
4. Adicionar histórico de custos
5. Implementar simulador "E se..."

---

## 📞 Suporte

Para dúvidas ou sugestões sobre o Dashboard v5:
- Verificar logs do Streamlit
- Consultar documentação dos módulos
- Testar com dados de exemplo primeiro

---

**Desenvolvido com ❤️ usando Streamlit, Plotly e Claude Code**

*Dashboard v5 - Gestão Completa de Vendas e Custos para Café Martins*
