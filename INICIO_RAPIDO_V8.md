# ⚡ Início Rápido - Dashboard V8

**Tempo de leitura:** 2 minutos
**Tempo de setup:** 30 segundos

---

## 🚀 **Testar Agora (3 comandos)**

### **1. Testar Performance**

```bash
cd /home/jorge/Documentos/Streamlit
venv/bin/python3 benchmark_filtros_v7_vs_v8.py
```

**Esperado:** V8 é ~11x mais rápido que V7

---

### **2. Iniciar Dashboard V8**

```bash
cd /home/jorge/Documentos/Streamlit
./start_dashboard_v8.sh
```

**Acesso:** http://localhost:8505

---

### **3. Comparar com V7** (Opcional)

Abrir 2 abas do navegador:
- **V7:** http://localhost:8502 (se estiver rodando)
- **V8:** http://localhost:8505

**Note:** V8 carrega **muito mais rápido** ao aplicar filtros!

---

## 📊 **Resultados Esperados**

### **Benchmark com Filtros:**

```
V7 (Ficheiros):
  • Tempo: 11.27s
  • Carrega: 12,680 registos
  • Usa: 401 registos
  • Desperdício: 96.8%

V8 (MariaDB):
  • Tempo: 992ms
  • Carrega: 948 registos (filtrados)
  • Desperdício: 0%

🚀 V8 é 11.4x mais rápido!
```

---

## ✅ **Verificações**

### **1. MariaDB está funcionando?**

```bash
mysql -u root -p'ppVlU3qbJcZaUeaZWpDlOo14Msmrdkpo' dashboard -e "SELECT COUNT(*) FROM dados_dashboard;"
```

**Esperado:** Deve retornar ~3,992 registos

---

### **2. Scripts cron estão a funcionar?**

```bash
# Ver últimas execuções
tail -20 /home/jorge/web_scrapper/mariadb_cron.log
tail -20 /home/jorge/web_scrapper/load_pos2.log
```

**Esperado:** Logs recentes (máx. 1 dia atrás)

---

### **3. Dashboard V8 está a rodar?**

```bash
ps aux | grep dashboard_v8
```

**Esperado:** Processo streamlit rodando

---

## 🔧 **Troubleshooting**

### **Problema: MariaDB não conecta**

```bash
# Verificar serviço MariaDB
sudo systemctl status mariadb

# Reiniciar se necessário
sudo systemctl restart mariadb
```

---

### **Problema: Dashboard não inicia**

```bash
# Ver logs
cd /home/jorge/Documentos/Streamlit
source venv/bin/activate
streamlit run dashboard_v8.py --server.port=8505
```

**Procurar erros** na saída do terminal

---

### **Problema: Porta 8505 já em uso**

```bash
# Ver processo usando porta 8505
lsof -i :8505

# Matar processo se necessário
kill -9 <PID>
```

---

## 📚 **Próximos Passos**

1. ✅ **Testou performance?** → Viu a diferença?
2. ✅ **Dashboard rodando?** → Experimente os filtros!
3. 📖 **Quer saber mais?** → Leia [README_V8_MARIADB.md](README_V8_MARIADB.md)
4. 📊 **Comparar versões?** → Leia [SUMARIO_DASHBOARD_V8.md](SUMARIO_DASHBOARD_V8.md)

---

## 🎯 **Diferenças Visíveis no Dashboard**

| Ação | V7 | V8 |
|------|----|----|
| **Carregar inicial** | ~11s | ~15s* |
| **Aplicar filtro de data** | ~11s | ~1s ⚡ |
| **Mudar período** | ~11s | ~1s ⚡ |
| **Filtro + categoria** | ~11s | ~0.5s ⚡ |

*\* V8 carrega mais dados inicialmente (18k vs 12k)*

**A vantagem real do V8 aparece ao usar FILTROS!**

---

## ⚠️ **Importante**

- **NÃO** modificar scripts de carregamento (cron)
- V7 e V8 podem rodar **simultaneamente**
- Dados são os **mesmos** (mesma fonte MariaDB para V8)
- **Cache:** 30 minutos em ambas versões

---

## 💡 **Dica Profissional**

Use V8 para:
- ✅ Análises de períodos específicos
- ✅ Dashboards com filtros dinâmicos
- ✅ Consultas frequentes
- ✅ Relatórios mensais/semanais

Use V7 para:
- ⚠️  Backup/fallback
- ⚠️  Carregar TUDO sempre (raro)

---

## 🎉 **Pronto!**

Em **30 segundos** você:
1. ✅ Testou a performance
2. ✅ Iniciou o dashboard
3. ✅ Viu a diferença de velocidade

**Aproveite o Dashboard V8! 🚀**

---

**Dúvidas?** Leia a documentação completa em [README_V8_MARIADB.md](README_V8_MARIADB.md)
