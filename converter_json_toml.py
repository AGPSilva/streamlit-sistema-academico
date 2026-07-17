import json

# Abra seu arquivo JSON
with open('credenciais/google_sheets_creds.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

# Converta para TOML correto
toml_output = ""

for chave, valor in dados.items():
    if isinstance(valor, str):
        # Escapar corretamente para TOML
        valor_escapado = valor.replace('\\', '\\\\').replace('"', '\\"')
        toml_output += f'{chave} = "{valor_escapado}"\n'
    else:
        toml_output += f'{chave} = {valor}\n'

# Salve em um arquivo de texto
with open('secrets_convertido.txt', 'w', encoding='utf-8') as f:
    f.write(toml_output)

print("✅ Arquivo convertido com sucesso!")
print("\nCopie o conteúdo abaixo e cole no Streamlit Cloud:")
print("=" * 80)
print(toml_output)