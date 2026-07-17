import json
import base64

# Abra seu arquivo JSON
with open('credenciais/google_sheets_creds.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

# Converter para TOML format correto
print("=" * 80)
print("COPIE EXATAMENTE ISTO E COLE NO STREAMLIT CLOUD:")
print("=" * 80)
print()

for chave, valor in dados.items():
    if chave == 'private_key':
        # A private_key é especial: tem quebras de linha
        # Escapar corretamente para TOML
        valor_escapado = valor.replace('\n', '\\n')
        print(f'{chave} = "{valor_escapado}"')
    elif isinstance(valor, str):
        # Outras strings
        print(f'{chave} = "{valor}"')
    else:
        # Números ou booleanos
        print(f'{chave} = {valor}')

print()
print("=" * 80)