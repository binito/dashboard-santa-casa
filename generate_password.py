#!/usr/bin/env python3
"""
Script para gerar hash de password para autenticação no Streamlit.
Uso: python3 generate_password.py
"""

import bcrypt

def generate_password_hash():
    print("=== Gerador de Password Hash para Streamlit ===\n")

    username = input("Nome de utilizador: ").strip()
    name = input("Nome completo: ").strip()
    password = input("Password: ").strip()

    # Gerar hash da password
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    print("\n" + "="*50)
    print("Configuração para config.yaml:")
    print("="*50)
    print(f"""
credentials:
  usernames:
    {username}:
      email: {username}@cafemartins.pt
      name: {name}
      password: {password_hash}
""")
    print("="*50)

if __name__ == "__main__":
    generate_password_hash()
