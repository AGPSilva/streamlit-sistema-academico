# 📚 Sistema de Informação Acadêmica

**Sistema privado de gerenciamento de informações acadêmicas** desenvolvido com Streamlit e Google Sheets.

---

## 📋 Descrição

Sistema web para gerenciamento de dados acadêmicos de alunos, incluindo:
- Consulta de alunos ativos
- Gerenciamento de alunos em RODA (Regime de Aceleração Acadêmica)
- Análise de reprovações (1, 2 ou múltiplas)
- Cálculo de coeficientes de rendimento
- Verificação de cumprimento de grade curricular

**Acesso:** Restrito a 3 usuários autorizados

---

## 🔧 Tecnologias

- **Python 3.10+**
- **Streamlit** - Framework web
- **Pandas** - Manipulação de dados
- **Google Sheets API** - Armazenamento de dados
- **openpyxl** - Leitura de arquivos Excel

---

## 📁 Estrutura do Projeto

```
streamlit-sistema-academico/
├── app.py                              # Arquivo principal
├── config.py                           # Configurações do sistema
├── utils.py                            # Funções utilitárias
├── google_sheets_manager.py            # Gerenciador do Google Sheets
├── processamento_roda.py               # Processamento de dados RODA
├── processamento_reprovacoes.py        # Processamento de reprovações
├── processamento_cumprimento_grade.py  # Processamento de grade
│
├── bases/                              # Arquivos de dados (Excel)
│   ├── info_geral2026-1.xlsx
│   ├── rendimento_alunos_ativos.xlsx
│   ├── alunos_ativos.xlsx
│   ├── RODA_alunos.xlsx
│   ├── grade_old.xlsx
│   ├── grade_new.xlsx
│   ├── coef_rend2026-1.xlsx
│   ├── periodo_rend2026-1.xlsx
│   ├── reprovados_uma_vez_cursando.xlsx
│   ├── reprovados_duas_vezes_cursando.xlsx
│   └── reprovacoes_multiplas_sem_cursar.xlsx
│
├── pages/                              # Páginas Streamlit
│   ├── 01_Alunos_Ativos.py
│   ├── 02_Alunos_RODA.py
│   ├── 03_Alunos_Reprovacoes.py
│   ├── 04_Coeficientes_Rendimento.py
│   └── 05_Cumprimento_Grade.py
│
├── credenciais/                        # ⚠️ Não versionado no Git
│   └── google_sheets_creds.json        # Credenciais Google (privado)
│
├── .streamlit/                         # ⚠️ Não versionado no Git
│   └── secrets.toml                    # Secrets do Streamlit (privado)
│
├── .gitignore                          # Arquivos ignorados pelo Git
├── requirements.txt                    # Dependências Python
└── README.md                           # Este arquivo
```

---

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Git
- Conta no GitHub (para clonar o repositório)

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/AGPSilva/streamlit-sistema-academico.git
cd streamlit-sistema-academico
```

### Passo 2: Criar Ambiente Virtual (Opcional, mas recomendado)

```bash
python -m venv venv
# No Windows
venv\Scripts\activate
# No macOS/Linux
source venv/bin/activate
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Configurar Credenciais Google

1. **Obter credenciais:**
   - Acesse [Google Cloud Console](https://console.cloud.google.com/)
   - Crie uma conta de serviço
   - Baixe o arquivo JSON de credenciais

2. **Adicionar credenciais localmente:**
   - Crie a pasta `credenciais/` na raiz do projeto
   - Copie o arquivo JSON para: `credenciais/google_sheets_creds.json`

3. **Configurar secrets do Streamlit (opcional):**
   - Crie a pasta `.streamlit/` na raiz
   - Crie o arquivo `.streamlit/secrets.toml`
   - Copie o conteúdo do JSON para dentro deste arquivo

### Passo 5: Executar o Sistema

```bash
streamlit run app.py
```

O sistema abrirá em `http://localhost:8501` no navegador.

---

## 📊 Funcionalidades

### 1️⃣ **Alunos Ativos**
- Visualização de lista de alunos ativos
- Filtros por ingresso, nome, matrícula
- Exportação de dados

### 2️⃣ **Alunos em RODA**
- **Mostrar:** Visualizar alunos já em RODA
- **Incluir:** Adicionar novo aluno em RODA
- **Editar:** Modificar informações de aluno
- **Excluir:** Remover aluno de RODA
- Integração com Google Sheets

### 3️⃣ **Alunos Reprovados**
Três tipos de consultas:

#### a) Reprovado Uma Vez e Cursando
- Alunos que foram reprovados uma vez
- Estão cursando a disciplina novamente
- Período de reprovação vs período atual

#### b) Reprovado Duas Vezes e Cursando
- Alunos com duas reprovações na mesma disciplina
- Estão cursando novamente
- Histórico de ambas as reprovações

#### c) Múltiplas Reprovações (Sem Cursar)
- Alunos com 2+ reprovações na mesma disciplina
- **NÃO estão cursando** atualmente
- Não foram aprovados após reprovações

### 4️⃣ **Coeficientes de Rendimento**
- Cálculo de rendimento acadêmico
- Filtros por período, aluno
- Análise de desempenho

### 5️⃣ **Cumprimento de Grade**
- Visualização da grade curricular teórica
- Disciplinas cursadas por aluno
- Separação por período, obrigatórias, optativas e eletivas
- Suporte para 2 grades (antiga e nova)

---

## 📝 Estrutura de Dados

### Matrículas
- Formato: **11 dígitos** (string)
- Exemplo: `20201100123`
- Padronização automática (se necessário, adiciona `00` no início)

### Períodos Acadêmicos
- Formato: `AAAA/S` (ano/semestre)
- Exemplo: `2026/1` (2026, semestre 1)

### Situações de Aluno
- `APR` - Aprovado
- `RPM` - Reprovado por Média
- `RPF` - Reprovado por Falta
- `RMF` - Reprovado por Múltiplas Faltas
- `ISE` - Integralização Simultânea
- `DISP` - Dispensado
- `AARE` - Aproveitamento de Estudos
- `CUR` - Cursando
- `RODA` - Em regime de aceleração acadêmica

---

## 🔐 Segurança

⚠️ **Arquivos Sensíveis (NÃO versionados no Git):**
- `credenciais/google_sheets_creds.json` - Credenciais Google
- `.streamlit/secrets.toml` - Secrets do Streamlit
- `__pycache__/` - Cache Python

Estes arquivos estão listados em `.gitignore` e **nunca serão enviados** para o GitHub.

---

## 👥 Usuários Autorizados

Este sistema é **privado** e destinado apenas a:
1. Angelus da Silva (Desenvolvimento e manutenção)
2. [Usuário 2]
3. [Usuário 3]

---

## 🔄 Atualizações e Manutenção

### Para Atualizar o Código

```bash
# 1. Sincronizar com GitHub
git pull origin main

# 2. Atualizar dependências (se necessário)
pip install -r requirements.txt

# 3. Testar o sistema
streamlit run app.py
```

### Para Enviar Alterações

```bash
# 1. Fazer alterações nos arquivos

# 2. Adicionar alterações
git add .

# 3. Criar commit
git commit -m "Descrição das alterações"

# 4. Enviar para GitHub
git push origin main
```

### Para Atualizar as Bases de Dados

1. Acesse a pasta `bases/`
2. Atualize os arquivos Excel conforme necessário
3. Salve os arquivos
4. Execute `git add bases/` e `git commit -m "Atualizar bases de dados"`
5. Envie com `git push origin main`

---

## 📞 Contato

Para dúvidas ou sugestões sobre o sistema:
- **Desenvolvedor:** Angelus da Silva
- **Email:** [seu-email@example.com]
- **GitHub:** https://github.com/AGPSilva

---

## 📄 Licença

Este projeto é **privado** e restrito a uso interno apenas.

---

## 🗂️ Histórico de Versões

| Versão | Data | Descrição |
|--------|------|-----------|
| 1.0.0 | 2026-07-17 | Versão inicial com todas as funcionalidades |

---

## ✅ Checklist de Funcionalidades

- [x] Consulta de alunos ativos
- [x] Gerenciamento de RODA (mostrar, incluir, editar, excluir)
- [x] Análise de reprovações (3 tipos)
- [x] Cálculo de coeficientes de rendimento
- [x] Verificação de cumprimento de grade
- [x] Integração com Google Sheets
- [x] Autenticação de usuários
- [x] Versionamento no GitHub
- [x] Documentação (este README)

---

**Última atualização:** 17 de julho de 2026