# path_config.py
# ============================================================================
# Configuração de caminhos para funcionar tanto localmente quanto na nuvem
# ============================================================================

import os
from pathlib import Path

# Detectar se está rodando no Streamlit Cloud ou localmente
IS_STREAMLIT_CLOUD = "STREAMLIT_RUNTIME_VERSION" in os.environ or ".streamlit" in str(Path.cwd())

# Diretório base do projeto
BASE_DIR = Path(__file__).parent

# Definir caminhos relativos
BASES_DIR = BASE_DIR / "bases"

# ============================================================================
# ARQUIVOS DE BASES DE DADOS
# ============================================================================

# Se estiver na nuvem, usa caminhos relativos
# Se estiver local, usa caminhos relativos também (mais simples!)
ARQUIVO_INFO_GERAL = BASES_DIR / "info_geral2026-1.xlsx"
ARQUIVO_RENDIMENTO = BASES_DIR / "rendimento_alunos_ativos.xlsx"
ARQUIVO_GRADE_OLD = BASES_DIR / "grade_old.xlsx"
ARQUIVO_GRADE_NEW = BASES_DIR / "grade_new.xlsx"

# ============================================================================
# FUNÇÃO AUXILIAR PARA OBTER CAMINHO SEGURO
# ============================================================================

def get_path(arquivo_nome):
    """
    Retorna o caminho correto para um arquivo de base de dados
    
    Args:
        arquivo_nome: nome do arquivo (ex: "info_geral2026-1.xlsx")
    
    Returns:
        Path: caminho do arquivo
    """
    caminho = BASES_DIR / arquivo_nome
    
    if not caminho.exists():
        raise FileNotFoundError(
            f"❌ Arquivo não encontrado: {caminho}\n"
            f"Certifique-se de que o arquivo '{arquivo_nome}' está na pasta 'bases/'"
        )
    
    return str(caminho)

# ============================================================================
# DICIONÁRIO COM TODOS OS CAMINHOS (Para fácil acesso)
# ============================================================================

CAMINHOS = {
    'info_geral': str(ARQUIVO_INFO_GERAL),
    'rendimento': str(ARQUIVO_RENDIMENTO),
    'grade_old': str(ARQUIVO_GRADE_OLD),
    'grade_new': str(ARQUIVO_GRADE_NEW),
}

# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

"""
# No lugar de:
# caminho = C:\\Users\\Angelus\\Dropbox\\...\\info_geral2026-1.xlsx
# df = pd.read_excel(caminho)

# Use:
# from path_config import CAMINHOS
# df = pd.read_excel(CAMINHOS['info_geral'])
"""