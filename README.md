# Dashboard Streamlit - Santa Casa da Misericórdia

Dashboard interativo para análise de vendas dos jogos da Santa Casa.

## Instalação

O dashboard está configurado para iniciar automaticamente no arranque do Raspberry Pi.

### Configuração
- **URL**: http://app.cafemartins.pt
- **Porta local**: 8501
- **Dados**: `/home/jorge/Documentos/Santa casa/dados/dados_extracao.txt`
- **Diretório**: `/home/jorge/Documentos/Streamlit`

## Gestão do Serviço

### Verificar status
```bash
sudo systemctl status streamlit-dashboard
```

### Parar o serviço
```bash
sudo systemctl stop streamlit-dashboard
```

### Iniciar o serviço
```bash
sudo systemctl start streamlit-dashboard
```

### Reiniciar o serviço
```bash
sudo systemctl restart streamlit-dashboard
```

### Ver logs
```bash
sudo journalctl -u streamlit-dashboard -f
```

### Desativar arranque automático
```bash
sudo systemctl disable streamlit-dashboard
```

### Ativar arranque automático
```bash
sudo systemctl enable streamlit-dashboard
```

## Estrutura de Ficheiros

```
/home/jorge/Documentos/Streamlit/
├── dashboard.py              # Aplicação principal
├── start_dashboard.sh        # Script de inicialização
├── venv/                     # Ambiente virtual Python
└── README.md                 # Este ficheiro
```

## Ficheiro de Dados

O dashboard lê os dados de:
```
/home/jorge/Documentos/Santa casa/dados/dados_extracao.txt
```

Formato esperado:
```
Totoloto: 195.00 (Data de Emissão: 17-05-2024)
Totobola: 0.00 (Data de Emissão: 17-05-2024)
...
```

### Atualização Automática de Dados

O dashboard **reinicia automaticamente todos os domingos às 09:00** para carregar os novos dados.

Esta tarefa está configurada no crontab:
```bash
# Ver cron jobs ativos
crontab -l | grep streamlit

# Log das atualizações
tail -f /home/jorge/Documentos/Streamlit/cron_restart.log
```

Para alterar o horário de atualização:
```bash
crontab -e
# Editar a linha: 0 9 * * 0 /usr/bin/systemctl restart streamlit-dashboard
```

## Configuração Nginx

O Nginx está configurado como reverse proxy em:
```
/etc/nginx/sites-available/streamlit
```

Para editar a configuração:
```bash
sudo nano /etc/nginx/sites-available/streamlit
sudo nginx -t  # Testar configuração
sudo systemctl reload nginx  # Recarregar
```

## Atualizar Dependências

```bash
cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
pip install --upgrade streamlit pandas plotly scikit-learn
deactivate
sudo systemctl restart streamlit-dashboard
```

## Troubleshooting

### Dashboard não carrega
1. Verificar se o serviço está ativo:
   ```bash
   sudo systemctl status streamlit-dashboard
   ```

2. Ver logs de erros:
   ```bash
   sudo journalctl -u streamlit-dashboard -n 50
   ```

3. Verificar se a porta 8501 está em uso:
   ```bash
   sudo netstat -tlnp | grep 8501
   ```

### Nginx não redireciona
1. Verificar configuração:
   ```bash
   sudo nginx -t
   ```

2. Ver logs do Nginx:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

### Ficheiro de dados não encontrado
Verificar se o ficheiro existe:
```bash
ls -la "/home/jorge/Documentos/Santa casa/dados/dados_extracao.txt"
```

## Funcionalidades do Dashboard

### **🎯 Dashboard Executivo** (NOVO!)
- KPIs com objetivos semanais comparativos
- Semáforos de performance (🟢🟡🔴)
- Gráficos Real vs Objetivo
- Análise de médias móveis (2-8 semanas)
- Filtros de data personalizados
- Exportação Excel/CSV profissional

### **📊 Comparações Avançadas** (NOVO!)
- **MoM (Month over Month)**: Crescimento mês a mês
- **YoY (Year over Year)**: Crescimento ano a ano
- **Previsão de Objetivos**: Probabilidade de atingir metas
- Recomendações automáticas baseadas em tendências

### **📈 Análises Existentes**
- 📊 **Visão Geral**: Métricas principais e top jogos
- 🎮 **Análise por Jogo**: Tendências, sazonalidade e previsões
- ⚖️ **Comparação**: Benchmarking entre jogos
- 💰 **Remuneração**: Análise de comissões por jogo

### **🎯 Objetivos Semanais Configurados**
| Jogo | Objetivo (€) | Notas |
|------|-------------|-------|
| Raspadinha | 2.627,70 | - |
| Euromilhões | 785,40 | 88% do total* |
| M1lhão | 107,10 | 12% do total* |
| EuroDreams | 301,65 | - |
| Placard | 433,55 | - |
| Lotaria Clássica | 72,15 | - |
| Lotaria Popular | 107,40 | - |
| Lotaria Instantânea | 2.627,70 | Equivalente a Raspadinha |
| Totoloto | 153,00 | - |
| Totobola | 3,00 | - |

_*Euromilhões e M1lhão vendem-se juntos (€2,50/aposta): €2,20 Euromilhões + €0,30 M1lhão_
_Total combinado: €892,50 (785,40 + 107,10)_

## Tecnologias Utilizadas

- Python 3.11
- Streamlit 1.50.0
- Pandas 2.3.3
- Plotly 6.3.1
- Scikit-learn 1.7.2
- **OpenPyXL 3.1.5** (NOVO! - Exportação Excel)
- Nginx (reverse proxy)
- Systemd (gestão de serviços)

## 🚀 Início Rápido

### Script Automático (Recomendado)
```bash
cd /home/jorge/Documentos/Streamlit
./executar_dashboard.sh
```

### Manual
```bash
cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
streamlit run dashboard.py
```

## 📥 Exportação de Relatórios

O dashboard agora suporta:
- **CSV**: Download direto de dados
- **Excel**: Relatório formatado profissionalmente
  - Cabeçalhos estilizados
  - Colunas auto-ajustadas
  - Informações do período

## 🚦 Sistema de Semáforos

- **🟢 Verde**: ≥100% do objetivo (Excelente!)
- **🟡 Amarelo**: 80-99% do objetivo (Bom)
- **🔴 Vermelho**: <80% do objetivo (Atenção necessária)

## 📊 Changelog

### Versão 2.0 (12/10/2025)
- ✅ Dashboard Executivo com KPIs e objetivos
- ✅ Comparações MoM e YoY
- ✅ Previsão de probabilidade de atingir objetivos
- ✅ Exportação Excel profissional
- ✅ Sistema de alertas e semáforos
- ✅ Médias móveis configuráveis
- ✅ Filtros de data personalizados
- ✅ Recomendações automáticas

### Versão 1.0
- Dashboard básico com visualizações
- Análise por jogo
- Gráficos interativos
