# 🎲 Dashboard Santa Casa - Análise Completa

> Dashboard interativo profissional para análise detalhada de jogos da Santa Casa da Misericórdia com remunerações, prémios e prestações de contas transparentes.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-red.svg)
![Status](https://img.shields.io/badge/Status-Produção-success.svg)

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades Principais](#-funcionalidades-principais)
- [Páginas de Análise](#-páginas-de-análise)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Estrutura de Dados](#-estrutura-de-dados)
- [Tecnologias](#-tecnologias)
- [Configuração](#-configuração)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Visão Geral

O **Dashboard Santa Casa** é uma aplicação completa desenvolvida em Streamlit para análise detalhada e transparente dos jogos da Santa Casa da Misericórdia. Oferece visões executivas, análises semanais, comparações avançadas e gestão de objetivos.

### Características Principais

- 📊 **11 Páginas de Análise** especializadas
- 🎯 **Sistema de Objetivos** com previsões automáticas
- 📈 **Comparações MoM, YoY e WoW** (Month/Year/Week over Week)
- 💰 **Análise de Rentabilidade** detalhada por jogo
- 🎁 **Gestão de Prémios** e raspadinhas
- 📋 **Prestação de Contas** semanal automatizada
- 📊 **Heatmaps de Performance** e tendências
- 🔒 **Sistema de Autenticação** integrado

---

## ✨ Funcionalidades Principais

### 🔐 Autenticação
- Login seguro com credenciais
- Gestão de sessões
- Proteção de dados sensíveis

### 📊 Métricas de Performance em Tempo Real
- **WoW** (Week over Week): Comparação com semana anterior
- **SWLY** (Same Week Last Year): Mesma semana ISO do ano anterior
- **MTD** (Month To Date): Performance mensal por ciclos semanais
- Indicadores visuais com variação percentual

### 🎯 Sistema de Objetivos Inteligente
- Definição de metas semanais por jogo
- Cálculo automático de % de cumprimento
- Projeções para 4 semanas e anuais
- Semáforos de status (🟢 🟡 🔴)
- Alertas e recomendações automáticas

### 💎 Indicadores Principais (KPIs)
- 💰 Vendas Ilíquidas totais
- 💵 Remunerações acumuladas
- 🎁 Prémios pagos
- 💎 Total Prestações (Valor Líquido)
- 📊 Número de transações

---

## 📄 Páginas de Análise

### 1. 📊 Visão Geral
Visão executiva de alto nível com:
- Indicadores principais (KPIs coloridos)
- Métricas de performance (WoW, SWLY, MTD)
- Evolução temporal de vendas
- Vendas por categoria
- Filtros de período personalizados

### 2. 🎯 Dashboard Executivo
Dashboard gerencial com foco em objetivos:
- Top 10 jogos com comparação Real vs Objetivo
- Evolução mensal de vendas
- Sistema de previsão de cumprimento de metas
- Gráficos de barras comparativos
- Definição e edição de objetivos semanais
- Status por jogo (Excelente/Próximo/Abaixo do objetivo)

### 3. 🔬 Análise Semanal
Análise detalhada week-over-week:
- **Tab WoW**: Comparação vendas última semana vs anterior
- **Tab Heatmap**: Mapa de calor de performance por jogo/semana
- **Tab Tendências**: Evolução por categoria com estatísticas
- **Tab Insights**: Comentários e análises automáticas
- Identificação de jogos mais consistentes e em crescimento

### 4. 📊 Comparações Avançadas
Comparações temporais sofisticadas:
- **MoM** (Month over Month): Crescimento mensal
- **YoY** (Year over Year): Comparação ano a ano
- **Semana a Semana**: Análise granular semanal
- **Previsão**: Probabilidade de atingir objetivos com recomendações

### 5. 🎰 Por Categoria
Análise por categorias de jogos:
- Resumo com vendas, remunerações, prémios e margem
- Distribuição em pizza (% de vendas)
- Evolução temporal por categoria
- Cálculo de margem percentual

### 6. 🎮 Por Jogo
Análise individual de jogos:
- Top N jogos (configurável: 5-20)
- Detalhes completos: vendas, remunerações, prémios, valor líquido
- Métricas de performance por jogo
- Comparação entre jogos

### 7. 🎫 Raspadinhas
Análise especializada de raspadinhas:
- Vendas por jogo rececionado
- Análise de maços comprados
- Detalhes completos com quantidade de maços
- Tracking de inventário

### 8. 📅 Temporal
Análise de evolução temporal:
- Agrupamento por Mês ou Semana
- Tabela de dados com todas as métricas
- Gráfico de evolução no tempo
- Estatísticas agregadas

### 9. 💰 Prémios
Análise detalhada de prémios pagos:
- **Por Jogo**: Top 10 jogos com mais prémios pagos
- **Por Categoria**: Distribuição de prémios por categoria
- **Evolução Temporal**: Tendência de prémios ao longo do tempo
- **Raspadinhas**: Análise de rentabilidade especial
  - 📅 Desde Sempre
  - 📆 Últimos 6 Meses
  - 📊 Últimos 2 Meses
  - 📆 Última Semana
- Cálculo de **Rentabilidade por Maço**
- Identificação de jogos mais e menos rentáveis

### 10. 📋 Prestação de Contas
Gestão de prestações semanais à Santa Casa:
- Listagem de semanas com total prestado
- Detalhes semanais completos
- Tracking de pagamentos
- Histórico de prestações

### 11. 📋 Dados Detalhados
Visualização raw dos dados:
- Tabela completa com todos os registos
- Estatísticas descritivas
- Filtros aplicados
- Exportação de dados

---

## 🚀 Instalação

### Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. **Clone o repositório ou navegue até a pasta:**
```bash
cd /home/jorge/Documentos/Streamlit
```

2. **Crie e ative um ambiente virtual:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências:**
```bash
pip install streamlit pandas plotly numpy streamlit-authenticator pyyaml openpyxl
```

4. **Verifique a estrutura de dados:**
Certifique-se de que o arquivo de dados existe em:
```
/home/jorge/Documentos/Santa casa/dados/dados_extracao.txt
```

---

## 💻 Como Usar

### Inicialização Local

```bash
cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
streamlit run dashboard_santa_casa.py --server.port 8503
```

### Acesso Web

Após iniciar, acesse no navegador:
- **Local**: http://localhost:8503
- **Rede**: http://192.168.X.X:8503
- **Domínio** (se configurado): https://app.cafemartins.pt

### Login

1. Abra o dashboard
2. Insira as credenciais configuradas em `config.yaml`
3. Clique em "Login"

### Navegação

1. Use o **menu lateral** (sidebar) para navegar entre páginas
2. Aplique **filtros de data** usando as pills de ano ou seletor personalizado
3. Explore as **tabs dentro de cada página** para análises detalhadas
4. Use o botão **🔄 Reset Total** para limpar cache se necessário

### Definir Objetivos

1. Navegue para **🎯 Dashboard Executivo**
2. Role até **⚙️ Configurações de Objetivos**
3. Insira o valor desejado para cada jogo
4. Clique em **💾 Guardar Objetivo**

---

## 📊 Estrutura de Dados

### Arquivo de Entrada
**Localização**: `/home/jorge/Documentos/Santa casa/dados/dados_extracao.txt`

**Formato esperado** (TSV - Tab Separated Values):
```
Data	Categoria	Jogo	Vendas ilíquidas (€)	Remunerações (€)	Prémios (€)	Valor (€)	Jogo Rececionado	Qt Maços
2025-01-05	Jogos Sociais do Estado	Euromilhões	1200.50	96.04	0.00	1104.46		0
2025-01-05	Raspadinhas	Raspadinha	2500.00	200.00	450.00	1850.00	5€ Jackpot	3
...
```

### Colunas Obrigatórias
- `Data`: Data da transação (formato: YYYY-MM-DD)
- `Categoria`: Categoria do jogo
- `Jogo`: Nome do jogo
- `Vendas ilíquidas (€)`: Valor bruto de vendas
- `Remunerações (€)`: Comissões recebidas
- `Prémios (€)`: Prémios pagos aos jogadores
- `Valor (€)`: Valor líquido (Vendas - Remunerações - Prémios)

### Colunas Opcionais
- `Jogo Rececionado`: Nome específico da raspadinha
- `Qt Maços`: Quantidade de maços (para raspadinhas)

---

## 🛠️ Tecnologias

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.11+ | Linguagem base |
| Streamlit | 1.50+ | Framework web |
| Pandas | 2.3+ | Manipulação de dados |
| Plotly | 6.3+ | Gráficos interativos |
| NumPy | Latest | Cálculos numéricos |
| Streamlit-Authenticator | Latest | Autenticação |
| OpenPyXL | 3.1+ | Exportação Excel |
| PyYAML | Latest | Configuração |

---

## ⚙️ Configuração

### Autenticação

Edite o arquivo `config.yaml`:

```yaml
credentials:
  usernames:
    jsmith:
      email: jsmith@example.com
      name: John Smith
      password: $2b$12$...  # Hash bcrypt
cookie:
  expiry_days: 30
  key: random_signature_key
  name: random_cookie_name
preauthorized:
  emails:
  - admin@example.com
```

### Objetivos Semanais

Os objetivos são salvos em:
```
/home/jorge/Documentos/Streamlit/objetivos_semanais.json
```

Formato:
```json
{
  "Euromilhões": 785.40,
  "Raspadinha": 2627.70,
  "Placard": 433.55,
  ...
}
```

### Configuração de Produção (Systemd)

Para executar como serviço do sistema, crie:
```bash
sudo nano /etc/systemd/system/streamlit-santa-casa.service
```

Conteúdo:
```ini
[Unit]
Description=Dashboard Santa Casa Streamlit
After=network.target

[Service]
Type=simple
User=jorge
WorkingDirectory=/home/jorge/Documentos/Streamlit
ExecStart=/home/jorge/Documentos/Streamlit/venv/bin/streamlit run dashboard_santa_casa.py --server.port 8503 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
```

Ativar:
```bash
sudo systemctl enable streamlit-santa-casa
sudo systemctl start streamlit-santa-casa
```

---

## 🐛 Troubleshooting

### Erro: "Arquivo de dados não encontrado"

**Solução:**
```bash
# Verificar se o arquivo existe
ls -la "/home/jorge/Documentos/Santa casa/dados/dados_extracao.txt"

# Verificar permissões
chmod 644 "/home/jorge/Documentos/Santa casa/dados/dados_extracao.txt"
```

### Dashboard não carrega

**Solução:**
```bash
# Verificar se a porta está livre
lsof -i :8503

# Matar processos anteriores
pkill -f "streamlit run dashboard_santa_casa.py"

# Reiniciar
streamlit run dashboard_santa_casa.py --server.port 8503
```

### Erro de módulos não encontrados

**Solução:**
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Reinstalar dependências
pip install -r requirements.txt
```

### Gráficos não aparecem

**Solução:**
1. Limpar cache: Clique em **🔄 Reset Total** no sidebar
2. Verificar console do navegador (F12) para erros JavaScript
3. Tentar outro navegador (Chrome, Firefox)

### Dados não atualizam

**Solução:**
1. Verificar se o arquivo `dados_extracao.txt` foi atualizado
2. Clicar em **🔄 Reset Total** para limpar cache
3. Reiniciar o dashboard

---

## 📈 Métricas e KPIs

### Fórmulas Principais

**Valor Líquido (Total Prestações):**
```
Valor Líquido = Vendas Ilíquidas - Remunerações - Prémios
```

**Margem Percentual:**
```
Margem % = (Valor Líquido / Vendas Ilíquidas) × 100
```

**% Cumprimento de Objetivo:**
```
% Cumprimento = (Média Semanal / Objetivo Semanal) × 100
```

**Projeção Anual:**
```
Projeção Anual = Média Semanal × 52 semanas
```

**Rentabilidade por Maço:**
```
Rentabilidade = Valor Líquido / Quantidade de Maços
```

---

## 📞 Suporte

Para questões ou problemas:
1. Verificar este README
2. Consultar a seção [Troubleshooting](#-troubleshooting)
3. Verificar logs do Streamlit
4. Contactar o administrador do sistema

---

## 📝 Notas de Versão

### Versão Atual (Janeiro 2026)

**Melhorias:**
- ✅ Formato de moeda atualizado para padrão português (X€)
- ✅ Renomeação "Valor Líquido" → "💎 Total Prestações"
- ✅ Keys únicas em todos os gráficos Plotly
- ✅ Melhoria no cálculo SWLY (baseado em semanas ISO)
- ✅ Performance mensal por ciclos semanais
- ✅ 11 páginas de análise completas
- ✅ Sistema de objetivos persistente
- ✅ Comparações MoM, YoY, WoW
- ✅ Análise de rentabilidade de raspadinhas
- ✅ Heatmaps de performance
- ✅ Prestação de contas automatizada

---

## 📄 Licença

Este projeto é de uso interno. Todos os direitos reservados.

---

**Desenvolvido com ❤️ usando Streamlit e Python**
