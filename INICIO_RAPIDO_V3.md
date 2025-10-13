# 🚀 Início Rápido - Dashboard v3

## ⚡ Início em 30 Segundos

```bash
cd /home/jorge/Documentos/Streamlit
streamlit run dashboard_v3.py
```

Acesse: **http://localhost:8501**

Pronto! 🎉

---

## 📊 O Que Vais Ver

### No Topo
- **💰 Total de Vendas**: €96.309,46
- **📊 Média Diária**: Vendas médias por dia
- **📅 Dias com Vendas**: Quantos dias têm dados
- **🏆 Melhor Dia**: Dia com mais vendas

### Gráficos Principais
1. **Gráfico de Pizza**: Distribuição entre Café e Outros
2. **Evolução Temporal**: Linha do tempo das vendas
   - Podes escolher: Diária | Semanal | Mensal

### 4 Tabs de Análise
1. **📊 Análise Comparativa**: Café vs Outros
2. **📅 Análise Temporal**: Padrões por dia/semana/mês
3. **🎯 Top Vendas**: Melhores dias e meses
4. **📑 Dados Detalhados**: Tabela completa + Exportar CSV

---

## 🎛️ Filtros Disponíveis

### Barra Lateral Esquerda

**Fonte de Dados:**
- ☑️ Vendas Café
- ☑️ Outros Produtos
- ☐ Jogos Santa Casa (quando disponível)

**Período:**
- Seleciona data de início
- Seleciona data de fim

---

## 💡 Dicas Rápidas

### Ver Apenas Café
1. Na barra lateral, desmarca "Outros Produtos"
2. Os gráficos atualizam automaticamente

### Ver Apenas Outros (Totobola)
1. Na barra lateral, desmarca "Vendas Café"
2. Análise focada em Totobola

### Exportar Dados
1. Vai à tab "📑 Dados Detalhados"
2. Clica em "📥 Exportar para CSV"
3. Ficheiro baixado automaticamente

### Mudar Período
1. Na barra lateral, secção "Período"
2. Clica no calendário
3. Seleciona início e fim

---

## 🆚 Comparar com Dashboard Original

### Executar Ambos Simultaneamente

**Terminal 1:**
```bash
streamlit run dashboard.py --server.port 8501
```

**Terminal 2:**
```bash
streamlit run dashboard_v3.py --server.port 8502
```

Agora tens:
- Dashboard Original: http://localhost:8501
- Dashboard v3: http://localhost:8502

---

## 🧪 Validar Instalação

```bash
python3 test_dashboard_v3.py
```

Deve mostrar:
```
✓ TESTE PASSOU - Dashboard v3 está funcional!
Fontes com dados: 2/3
Total de registos: 9,184
Total de vendas: €96,309.46
```

---

## ❓ Resolução de Problemas

### Dashboard não abre?

**Problema:** Porta ocupada
```bash
# Matar processo na porta 8501
lsof -ti:8501 | xargs kill -9

# Ou usar outra porta
streamlit run dashboard_v3.py --server.port 8503
```

**Problema:** Módulo não encontrado
```bash
# Ativar ambiente virtual
cd /home/jorge/Documentos/Streamlit
source venv/bin/activate

# Reinstalar se necessário
pip install streamlit pandas plotly numpy scikit-learn openpyxl
```

### Não vê dados?

**Verificar ficheiros:**
```bash
ls -lh /home/jorge/Documentos/pos/pos_1/
ls -lh /home/jorge/Documentos/pos/pos_2/
```

Deve mostrar:
- pos_1: 2023.xlsx, 2024.xlsx, 2025.xlsx
- pos_2: Mapas_Artigos-*.csv

### Dados errados?

**Validar carregamento:**
```bash
python3 -c "from data_loader_v3 import DataLoaderV3; print(DataLoaderV3().get_resumo_dados())"
```

---

## 📱 Acesso Remoto (Opcional)

### Da Rede Local

1. Descobre teu IP:
```bash
hostname -I | awk '{print $1}'
```

2. No dashboard, verás:
```
Network URL: http://192.168.1.XXX:8501
```

3. Acede de outro dispositivo na mesma rede

### Da Internet (Avançado)

Usa ngrok ou similar:
```bash
ngrok http 8501
```

---

## 📚 Documentação Completa

- **README_v3.md**: Documentação técnica completa
- **COMPARACAO_DASHBOARDS.md**: Original vs v3
- **dashboard_v3.py**: Código fonte do dashboard
- **data_loader_v3.py**: Código do carregador de dados

---

## 🎯 Próximos Passos

### Hoje
1. ✅ Abrir dashboard v3
2. ✅ Explorar todas as tabs
3. ✅ Testar filtros
4. ✅ Exportar um CSV de teste

### Esta Semana
1. 📊 Comparar com dados reais conhecidos
2. 📈 Mostrar a colegas/equipe
3. 💭 Decidir se integra com dashboard original
4. 📝 Reportar qualquer problema ou sugestão

### Próximo Mês
1. 🔄 Adicionar dados Santa Casa quando disponíveis
2. 🎨 Personalizar cores/layout se necessário
3. ⚙️ Adicionar autenticação se necessário
4. 📊 Adicionar novos tipos de análise

---

## ✨ Funcionalidades Escondidas

### Hover nos Gráficos
- Passa o rato por cima dos gráficos
- Vê valores exatos
- Clica em legendas para esconder/mostrar séries

### Zoom nos Gráficos
- Arrasta para selecionar área
- Clica "Reset axes" para voltar

### Gráficos em Ecrã Completo
- Botão de câmara para capturar imagem
- Botão de expandir para tela cheia

---

## 📞 Ajuda

### Encontrou um bug?
Verifica:
1. Console do navegador (F12)
2. Terminal onde corre o streamlit
3. Logs em `~/.streamlit/logs/`

### Quer adicionar funcionalidade?
Ficheiros para editar:
- `dashboard_v3.py` - Interface e visualizações
- `data_loader_v3.py` - Carregamento de dados

### Precisa de ajuda técnica?
Documentação Streamlit: https://docs.streamlit.io

---

**Criado:** 13/10/2025
**Versão:** 3.0
**Status:** ✅ Testado e Funcional

---

🎊 **Diverte-te a explorar os dados!** 📊
