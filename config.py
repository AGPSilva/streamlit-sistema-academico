# ============================================================================
# config.py - Arquivo de Configuração Global
# ============================================================================
# Este arquivo centraliza todas as configurações da aplicação
# Credenciais, títulos, descrições, etc.

# ============================================================================
# CREDENCIAIS DOS USUÁRIOS (3 usuários)
# ============================================================================
# Formato: {"usuario": "senha"}
# IMPORTANTE: Em produção, considere usar variáveis de ambiente para maior segurança
# Por enquanto, isso funciona bem para 3 usuários de confiança

USUARIOS = {
    "Angelus": "senha123",
    "Alessandra": "senha456",
    "Visitante": "senha789"
}

# ============================================================================
# CONFIGURAÇÕES DA APLICAÇÃO
# ============================================================================

TITULO_PRINCIPAL = "Sistema de Informação Acadêmica"
SUBTITULO = "Consultas e Relatórios Acadêmicos"
AUTOR = "Seu Nome"



# ============================================================================
# PERÍODO CORRENTE E ANTERIOR
# ============================================================================
# Alterar estas variáveis conforme necessário

PERIODO_CORRENTE = "2026/1"
PERIODO_ANTERIOR = "2025/2"

# ============================================================================
# CONFIGURAÇÕES DE SESSÃO
# ============================================================================
# Tempo de inatividade antes de deslogar (em minutos)
# Por enquanto, deixamos indefinido (o usuário se mantém logado durante a sessão)
TEMPO_SESSAO = None  # Sessão infinita enquanto o navegador está aberto

# ============================================================================
# NOMES DAS PÁGINAS DE CONSULTAS
# ============================================================================
# Estes são os links que aparecem na landing page
PAGINAS_CONSULTAS = {
    "Alunos Ativos": "01_Alunos_Ativos.py",
    "Coeficientes de Rendimento": "04_Coeficientes_Rendimento.py",
    "Alunos com Reprovação": "03_Alunos_Reprovacoes.py",
    "Alunos em RODA": "02_Alunos_RODA.py",
    "Cumprimento da Grade": "05_Cumprimento_Grade.py"
}