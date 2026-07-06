# 🔒 Melhorias de Segurança Implementadas - Dashboard v8

**Data**: 16 de Dezembro de 2025
**Implementação**: Opção 1 (Segurança Básica)
**Status**: ✅ **CONCLUÍDO COM SUCESSO**

---

## 📋 Resumo das Alterações

Foram implementadas melhorias críticas de segurança para proteger credenciais e dados sensíveis do sistema Dashboard v8 + Despesify.

---

## ✅ 1. Credenciais Migradas para Variáveis de Ambiente

### Antes (INSEGURO):
```python
# data_loader_v8.py e despesify_loader.py
DB_CONFIG = {
    'user': 'root',
    'password': 'ppVlU3qbJcZaUeaZWpDlOo14Msmrdkpo',  # ❌ SENHA EM TEXTO PLANO!
    'database': 'dashboard'
}
```

### Depois (SEGURO):
```python
# Credenciais carregadas de .env
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME_DASHBOARD', 'dashboard')
}
```

### Ficheiro Criado: `.env`
```bash
DB_USER=dashboard_app
DB_PASSWORD=rg0guT1jvTGYImYqmS8CNrtiNHFxY@bP  # Senha forte de 32 caracteres
DB_NAME_DASHBOARD=dashboard
DB_NAME_DESPESIFY=despesify
COOKIE_KEY=d87c04f3bce0e8180e0edfc56b1e45dc08aef75d4e1a4b104b01d6700f8fd78c
```

**Benefícios**:
- ✅ Senhas não expostas no código
- ✅ Ficheiro `.env` já protegido no `.gitignore`
- ✅ Permissões restritivas (600) - apenas proprietário pode ler

---

## ✅ 2. Utilizador Dedicado do MariaDB Criado

### Antes (INSEGURO):
- Conexões usando conta **`root`** (privilégios totais)
- Violação do princípio do menor privilégio

### Depois (SEGURO):
- Novo utilizador: **`dashboard_app@localhost`**
- Senha forte de 32 caracteres: `rg0guT1jvTGYImYqmS8CNrtiNHFxY@bP`

### Privilégios Limitados:
| Base de Dados | Privilégios Concedidos | Justificação |
|---------------|------------------------|--------------|
| **dashboard** | SELECT, INSERT, UPDATE, DELETE | Leitura + escrita de dados de vendas |
| **despesify** | SELECT (apenas leitura) | Dashboard não deve modificar despesas |

### O que o utilizador NÃO pode fazer:
- ❌ Criar ou apagar bases de dados
- ❌ Criar ou apagar tabelas
- ❌ Alterar estruturas (ALTER TABLE)
- ❌ Gerir outros utilizadores
- ❌ Acesso remoto (apenas localhost)

**Script criado**: `criar_usuario_db.sql`

---

## ✅ 3. Chave de Cookie Forte Gerada

### Antes (INSEGURO):
```yaml
cookie:
  key: streamlit_dashboard_santa_casa_auth_key_2025  # ❌ Previsível
```

### Depois (SEGURO):
```yaml
cookie:
  key: d87c04f3bce0e8180e0edfc56b1e45dc08aef75d4e1a4b104b01d6700f8fd78c  # ✅ 64 caracteres aleatórios
```

**Benefícios**:
- ✅ Chave gerada com `secrets.token_hex(32)`
- ✅ Impossível de adivinhar
- ✅ Previne falsificação de sessões

---

## ✅ 4. Permissões de Ficheiros Corrigidas

### Antes (INSEGURO):
```bash
-rw-r--r-- config.yaml          # ❌ Legível por todos
-rw-r--r-- data_loader_v8.py    # ❌ Legível por todos
```

### Depois (SEGURO):
```bash
-rw------- .env                  # ✅ Apenas proprietário (600)
-rw------- config.yaml           # ✅ Apenas proprietário (600)
-rw------- data_loader_v8.py     # ✅ Apenas proprietário (600)
-rw------- despesify_loader.py   # ✅ Apenas proprietário (600)
```

**Benefícios**:
- ✅ Nenhum outro utilizador do sistema pode ler ficheiros sensíveis
- ✅ Protege contra acesso local não autorizado

---

## ✅ 5. Proteção contra Commits Acidentais

### Verificado: `.gitignore`
```gitignore
# Dados sensíveis
config.yaml
*.env
```

**Benefícios**:
- ✅ `.env` nunca será commitado para Git
- ✅ Protege contra exposição pública no GitHub

---

## 📦 Ficheiros Modificados

1. ✅ **`data_loader_v8.py`** - Usa variáveis de ambiente
2. ✅ **`despesify_loader.py`** - Usa variáveis de ambiente
3. ✅ **`config.yaml`** - Chave de cookie forte
4. ✅ **`.env`** - NOVO - Credenciais seguras
5. ✅ **`criar_usuario_db.sql`** - NOVO - Script de criação de utilizador

---

## 🔍 Testes Realizados

### Teste 1: Conexão com Novo Utilizador
```bash
✅ dashboard_app conectou com sucesso
✅ Acesso à DB 'dashboard' (3 tabelas)
✅ Acesso à DB 'despesify' (5 tabelas)
```

### Teste 2: Permissões de Ficheiros
```bash
✅ .env: rw------- (600)
✅ config.yaml: rw------- (600)
✅ data_loader_v8.py: rw------- (600)
✅ despesify_loader.py: rw------- (600)
```

### Teste 3: Integração Despesify
```bash
✅ DespesifyLoader conecta com sucesso
✅ CostManagerV2 funciona corretamente
✅ Dashboard v8 carrega dados sem erros
```

---

## ⚠️ IMPORTANTE - Próximos Passos

### 1. Testar Dashboard
Execute o dashboard e verifique se tudo funciona:
```bash
streamlit run dashboard_v8.py --server.port 8502
```

### 2. Guardar Credenciais em Local Seguro
- ✅ Senhas geradas:
  - **DB Password**: `rg0guT1jvTGYImYqmS8CNrtiNHFxY@bP`
  - **Cookie Key**: `d87c04f3bce0e8180e0edfc56b1e45dc08aef75d4e1a4b104b01d6700f8fd78c`
- 💾 Guardar num gestor de senhas (ex: KeePass, Bitwarden)
- 💾 Fazer backup encriptado do `.env`

### 3. Manter Conta Root Segura
A conta `root` ainda existe e deve ser protegida:
```bash
# Opcional: Alterar senha do root
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED BY '<nova_senha_forte>';
FLUSH PRIVILEGES;
```

### 4. Desativar Conta Root (Opcional - AVANÇADO)
**CUIDADO**: Apenas se tiver certeza que não precisa de root:
```sql
-- Remover privilégios do root (CUIDADO!)
REVOKE ALL PRIVILEGES ON *.* FROM 'root'@'localhost';
```

---

## 🛡️ Nível de Segurança Alcançado

| Aspeto | Antes | Depois |
|--------|-------|--------|
| Credenciais no código | ❌ Sim (texto plano) | ✅ Não (.env) |
| Utilizador root | ❌ Usado | ✅ Substituído |
| Chave de cookie | ❌ Fraca | ✅ Forte (64 chars) |
| Permissões de ficheiros | ❌ Públicas (644) | ✅ Privadas (600) |
| Protegido no Git | ⚠️ Parcial | ✅ Completo |
| Princípio menor privilégio | ❌ Não | ✅ Sim |

**Resultado**: Sistema **MUITO MAIS SEGURO** 🎯

---

## 📚 Documentação Adicional

### Como Adicionar Novo Servidor/Ambiente
Se precisar migrar para outro servidor:
1. Copiar ficheiro `.env` para o novo servidor
2. Ajustar `DB_HOST` se necessário
3. Executar `criar_usuario_db.sql` no MariaDB do novo servidor
4. Ajustar permissões: `chmod 600 .env config.yaml`

### Como Rodar Credenciais (Recomendado a cada 6 meses)
1. Gerar nova senha: `python3 -c "import secrets; print(secrets.token_hex(16))"`
2. Atualizar `.env` com nova senha
3. Atualizar utilizador no MariaDB:
   ```sql
   ALTER USER 'dashboard_app'@'localhost' IDENTIFIED BY '<nova_senha>';
   FLUSH PRIVILEGES;
   ```

---

## 🆘 Suporte

Se encontrar problemas:
1. Verificar logs do dashboard
2. Testar conexão manualmente:
   ```bash
   mysql -u dashboard_app -p'rg0guT1jvTGYImYqmS8CNrtiNHFxY@bP' -e "SELECT 1;"
   ```
3. Verificar se `.env` está no diretório correto
4. Verificar permissões dos ficheiros

---

**✅ Implementação concluída com sucesso!**
**🔒 Sistema agora muito mais seguro contra ataques e acessos não autorizados!**
