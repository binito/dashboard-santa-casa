# Credenciais de Acesso ao Dashboard

## Acesso Atual

**URL:** https://app.cafemartins.pt (quando DNS propagar)
**URL Local:** http://localhost:8501

### Credenciais Temporárias

```
Utilizador: jorge
Password: DashboardSC2025!
```

## Como Alterar a Password

### Opção 1: Usar o script gerador

```bash
cd /home/jorge/Documentos/Streamlit
python3 generate_password.py
```

Depois copia a configuração gerada para o ficheiro `config.yaml`

### Opção 2: Gerar manualmente

```bash
python3 -c "
import bcrypt
password = input('Nova password: ')
hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(f'Hash: {hash}')
"
```

Depois edita o ficheiro `config.yaml` e substitui o hash antigo pelo novo.

### Opção 3: Editar config.yaml diretamente

```bash
nano /home/jorge/Documentos/Streamlit/config.yaml
```

Depois reinicia o serviço:
```bash
sudo systemctl restart streamlit-dashboard
```

## Adicionar Novos Utilizadores

Edita o ficheiro `/home/jorge/Documentos/Streamlit/config.yaml`:

```yaml
credentials:
  usernames:
    jorge:
      email: jorge@cafemartins.pt
      name: Jorge Martins
      password: $2b$12$...

    novoutilizador:
      email: novoutilizador@cafemartins.pt
      name: Nome Completo
      password: $2b$12$...  # Gerar com script
```

Depois reinicia o serviço:
```bash
sudo systemctl restart streamlit-dashboard
```

## Segurança

- **IMPORTANTE:** Altera a password temporária assim que possível!
- Não partilhes o ficheiro `config.yaml` pois contém os hashes das passwords
- Os cookies de sessão expiram após 30 dias
- Para forçar logout de todos os utilizadores, altera a chave `cookie.key` no `config.yaml`

## Troubleshooting

### Esqueci a password

1. Gera um novo hash com o script:
   ```bash
   python3 generate_password.py
   ```

2. Substitui no `config.yaml`

3. Reinicia:
   ```bash
   sudo systemctl restart streamlit-dashboard
   ```

### Login não funciona

1. Verifica os logs:
   ```bash
   sudo journalctl -u streamlit-dashboard -n 50
   ```

2. Verifica se o `config.yaml` está correto:
   ```bash
   cat /home/jorge/Documentos/Streamlit/config.yaml
   ```

3. Testa localmente:
   ```bash
   cd /home/jorge/Documentos/Streamlit
   ./venv/bin/streamlit run dashboard.py
   ```
