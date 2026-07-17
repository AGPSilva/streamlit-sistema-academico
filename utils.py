# ============================================================================
# utils.py - Funções Utilitárias (Autenticação)
# ============================================================================
# Este arquivo centraliza funções que podem ser usadas em vários lugares
# Neste caso: funções de autenticação

import streamlit as st
from config import USUARIOS

# ============================================================================
# FUNÇÃO 1: Inicializar o estado da sessão
# ============================================================================
def inicializar_sessao():
    """
    Inicializa as variáveis de sessão do Streamlit.
    
    O Streamlit usa st.session_state para guardar dados que persistem
    enquanto o usuário está na aplicação.
    
    Variables criadas:
    - logado: True/False - indica se o usuário está autenticado
    - usuario: string - nome do usuário logado
    """
    if 'logado' not in st.session_state:
        st.session_state.logado = False
    
    if 'usuario' not in st.session_state:
        st.session_state.usuario = None


# ============================================================================
# FUNÇÃO 2: Verificar credenciais
# ============================================================================
def verificar_credenciais(usuario, senha):
    """
    Verifica se o usuário e senha estão corretos.
    
    Parâmetros:
    -----------
    usuario : str
        Nome do usuário digitado
    senha : str
        Senha digitada
    
    Retorna:
    --------
    bool
        True se credenciais estão corretas, False caso contrário
    
    Exemplo:
    --------
    >>> if verificar_credenciais("professor1", "senha123"):
    ...     print("Login bem-sucedido!")
    """
    # Verifica se o usuário existe e se a senha corresponde
    if usuario in USUARIOS and USUARIOS[usuario] == senha:
        return True
    return False


# ============================================================================
# FUNÇÃO 3: Fazer login
# ============================================================================
def fazer_login(usuario, senha):
    """
    Realiza o login do usuário.
    
    Se as credenciais estiverem corretas:
    - Marca o usuário como logado
    - Armazena o nome do usuário na sessão
    - Retorna True
    
    Se as credenciais estiverem incorretas:
    - Retorna False
    
    Parâmetros:
    -----------
    usuario : str
        Nome do usuário
    senha : str
        Senha do usuário
    
    Retorna:
    --------
    bool
        True se login foi bem-sucedido, False caso contrário
    """
    if verificar_credenciais(usuario, senha):
        st.session_state.logado = True
        st.session_state.usuario = usuario
        return True
    return False


# ============================================================================
# FUNÇÃO 4: Fazer logout
# ============================================================================
def fazer_logout():
    """
    Realiza o logout do usuário.
    
    Define:
    - logado = False
    - usuario = None
    """
    st.session_state.logado = False
    st.session_state.usuario = None


# ============================================================================
# FUNÇÃO 5: Verificar se está logado
# ============================================================================
def está_logado():
    """
    Retorna se o usuário está autenticado.
    
    Retorna:
    --------
    bool
        True se logado, False caso contrário
    
    Exemplo:
    --------
    >>> if está_logado():
    ...     st.write("Bem-vindo!")
    ... else:
    ...     st.warning("Você precisa fazer login primeiro")
    """
    return st.session_state.logado


# ============================================================================
# FUNÇÃO 6: Obter nome do usuário logado
# ============================================================================
def obter_usuario():
    """
    Retorna o nome do usuário logado.
    
    Retorna:
    --------
    str or None
        Nome do usuário se logado, None caso contrário
    
    Exemplo:
    --------
    >>> usuario = obter_usuario()
    >>> if usuario:
    ...     st.write(f"Logado como: {usuario}")
    """
    return st.session_state.usuario


# ============================================================================
# FUNÇÃO 7: Mostrar formulário de login
# ============================================================================
def mostrar_formulario_login():
    """
    Exibe o formulário de login na tela.
    
    Retorna:
    --------
    None
    
    Efeitos colaterais:
    - Exibe um formulário com campos para usuário e senha
    - Se o botão "Entrar" for clicado, tenta fazer login
    - Se bem-sucedido, mostra mensagem de sucesso e recarrega a página
    - Se mal-sucedido, mostra mensagem de erro
    """
    st.markdown("---")
    st.markdown("### 🔐 Login")
    
    # Criar containers para melhor organização
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Campo de usuário
        usuario = st.text_input(
            label="Usuário",
            placeholder="Digite seu usuário",
            key="input_usuario"
        )
        
        # Campo de senha
        senha = st.text_input(
            label="Senha",
            type="password",
            placeholder="Digite sua senha",
            key="input_senha"
        )
        
        # Botão de entrar
        if st.button("🔓 Entrar", use_container_width=True):
            # Verifica se os campos não estão vazios
            if not usuario or not senha:
                st.error("❌ Por favor, preencha usuário e senha")
            # Tenta fazer login
            elif fazer_login(usuario, senha):
                st.success("✅ Login bem-sucedido! Redirecionando...")
                st.rerun()  # Recarrega a página para mostrar conteúdo logado
            else:
                st.error("❌ Usuário ou senha incorretos")
    
    st.markdown("---")