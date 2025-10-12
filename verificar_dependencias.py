#!/usr/bin/env python3
"""
Script para verificar todas as dependências do dashboard
"""

import sys

def verificar_biblioteca(nome_biblioteca, nome_import=None):
    """Verifica se uma biblioteca está instalada."""
    if nome_import is None:
        nome_import = nome_biblioteca

    try:
        modulo = __import__(nome_import)
        versao = getattr(modulo, '__version__', 'Versão desconhecida')
        print(f"✅ {nome_biblioteca}: {versao}")
        return True
    except ImportError:
        print(f"❌ {nome_biblioteca}: NÃO INSTALADO")
        return False

def main():
    print("=" * 60)
    print("Verificação de Dependências - Dashboard Santa Casa")
    print("=" * 60)
    print()

    bibliotecas = [
        ('streamlit', 'streamlit'),
        ('pandas', 'pandas'),
        ('plotly', 'plotly'),
        ('numpy', 'numpy'),
        ('scikit-learn', 'sklearn'),
        ('openpyxl', 'openpyxl'),
        ('pyyaml', 'yaml'),
        ('streamlit-authenticator', 'streamlit_authenticator'),
    ]

    todas_ok = True

    for nome, nome_import in bibliotecas:
        if not verificar_biblioteca(nome, nome_import):
            todas_ok = False

    print()
    print("=" * 60)

    if todas_ok:
        print("✅ TODAS AS DEPENDÊNCIAS ESTÃO INSTALADAS!")
        print("🚀 Dashboard pronto para executar!")
        print()
        print("Execute: streamlit run dashboard.py")
    else:
        print("⚠️  ALGUMAS DEPENDÊNCIAS ESTÃO FALTANDO")
        print()
        print("Instale com:")
        print("pip install streamlit pandas plotly numpy scikit-learn openpyxl pyyaml streamlit-authenticator")

    print("=" * 60)

    return 0 if todas_ok else 1

if __name__ == "__main__":
    sys.exit(main())
