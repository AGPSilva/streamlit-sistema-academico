# ============================================================================
# app.py - Página Principal (Landing Page)
# ============================================================================
# Este é o arquivo principal que o Streamlit executa
# Aqui fica a landing page e o controle de autenticação

import streamlit as st
from config import TITULO_PRINCIPAL, SUBTITULO, PAGINAS_CONSULTAS
from utils import (
    inicializar_sessao,
    está_logado,
    obter_usuario,
    fazer_logout,
    mostrar_formulario_login
)

# ============================================================================
# CONFIGURAÇÕES DA PÁGINA
# ============================================================================
# Configura o layout e o ícone da página no navegador

st.set_page_config(
    page_title="Sistema Acadêmico",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# INICIALIZAR A SESSÃO
# ============================================================================
# Prepara as variáveis que controlam autenticação
inicializar_sessao()

# ============================================================================
# BARRA LATERAL (SIDEBAR)
# ============================================================================
# A barra lateral mostra informações do usuário e opção de logout

with st.sidebar:
    st.markdown("---")
    
    # Se está logado, mostra informações do usuário
    if está_logado():
        usuario = obter_usuario()
        st.success(f"✅ Logado como: **{usuario}**")
        
        # Botão de logout
        if st.button("🚪 Sair", use_container_width=True):
            fazer_logout()
            st.rerun()  # Recarrega a página
    
    st.markdown("---")

# ============================================================================
# TÍTULO E DESCRIÇÃO
# ============================================================================
# Exibe o título principal da aplicação

st.markdown(f"# {TITULO_PRINCIPAL}")
st.markdown(f"*{SUBTITULO}*")
st.markdown("---")

# ============================================================================
# FLUXO PRINCIPAL
# ============================================================================
# Se não está logado, mostra o formulário de login
# Se está logado, mostra a landing page com os links

if not está_logado():
    # Usuário não está autenticado - mostra apenas o formulário
    st.info("ℹ️ Para acessar o sistema, faça login primeiro.")
    mostrar_formulario_login()

else:
    # Usuário está autenticado - mostra a landing page completa
    st.success(f"👋 Bem-vindo, {obter_usuario()}!")
    
    st.markdown("""
    ### 📊 Selecione uma consulta:
    """)
    
    # ========================================================================
    # LINKS PARA AS PÁGINAS DE CONSULTAS
    # ========================================================================
    # Cria um grid com os links para cada consulta
    
    # Divide a tela em 2 colunas para melhor visualização
    col1, col2 = st.columns(2)
    
    # Dicionário com as consultas (vem do config.py)
    consultas = PAGINAS_CONSULTAS
    
    # Lista para armazenar os links
    links = []
    
    # Cria um link para cada consulta
    for i, (nome_consulta, arquivo) in enumerate(consultas.items()):
        # Alterna entre col1 e col2
        coluna = col1 if i % 2 == 0 else col2
        
        with coluna:
            # Cria um container com estilo
            with st.container(border=True):
                # Ícones diferentes para cada consulta
                icones = {
                    "Alunos Ativos": "👥",
                    "Alunos com Reprovação": "❌",
                    "Alunos em RODA": "⚠️",
                    "Coeficientes de Rendimento": "📈",
                    "Cumprimento da Grade": "✅"
                }
                
                icone = icones.get(nome_consulta, "📄")
                
                # Botão que leva para a página
                if st.button(
                    f"{icone} {nome_consulta}",
                    use_container_width=True,
                    key=f"btn_{nome_consulta}"
                ):
                    st.switch_page(f"pages/{arquivo}")
    
    # ========================================================================
    # RODAPÉ
    # ========================================================================
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
        Sistema de Informação Acadêmica | Desenvolvido com Streamlit
    </div>
    """, unsafe_allow_html=True)