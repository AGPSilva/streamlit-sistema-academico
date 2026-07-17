# ============================================================================
# 01_Alunos_Ativos.py - Página de Consulta de Alunos Ativos
# ============================================================================
# Este arquivo exibe a consulta de alunos ativos agrupados por ingresso
# Integrado ao sistema Streamlit de autenticação

import streamlit as st
import pandas as pd
from utils import inicializar_sessao, está_logado, obter_usuario, fazer_logout

# ============================================================================
# CONFIGURAÇÕES DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Alunos Ativos",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# INICIALIZAR A SESSÃO
# ============================================================================

inicializar_sessao()

# ============================================================================
# VERIFICAR AUTENTICAÇÃO
# ============================================================================
# Se o usuário não está logado, redireciona para a página principal

if not está_logado():
    st.warning("⚠️ Você não está autenticado. Faça login na página principal.")
    if st.button("🔙 Voltar para o Login"):
        st.switch_page("app.py")
    st.stop()

# ============================================================================
# BARRA LATERAL
# ============================================================================

with st.sidebar:
    st.markdown("---")
    usuario = obter_usuario()
    st.success(f"✅ Logado como: **{usuario}**")
    
    if st.button("🔙 Voltar para Menu", use_container_width=True):
        st.switch_page("app.py")
    
    if st.button("🚪 Sair", use_container_width=True):
        fazer_logout()
        st.switch_page("app.py")
    
    st.markdown("---")

# ============================================================================
# TÍTULO E DESCRIÇÃO
# ============================================================================

st.markdown("# 👥 Alunos Ativos")
st.markdown("*Consulta de alunos agrupados por período de ingresso*")
st.markdown("---")

# ============================================================================
# CARREGAR OS DADOS
# ============================================================================

try:
    from path_config import CAMINHOS
    
    # Ler apenas a primeira aba (índice 0)
    df = pd.read_excel(CAMINHOS['info_geral'], sheet_name=0)
    
    # Selecionar colunas necessárias
    colunas_desejadas = ['Matrícula', 'Nome', 'Ingresso', 'Cota']
    df_filtrado = df[colunas_desejadas].copy()
    
    # ========================================================================
    # CONVERTER / EM - NA COLUNA INGRESSO
    # ========================================================================
    # Substitui a barra (/) por hífen (-) para evitar problemas com caracteres especiais
    df_filtrado['Ingresso'] = df_filtrado['Ingresso'].astype(str).str.replace('/', '-')
    
    # Ordenar por Ingresso e depois por Nome (alfabeticamente)
    df_ordenado = df_filtrado.sort_values(by=['Ingresso', 'Nome']).reset_index(drop=True)
    
    # ========================================================================
    # EXIBIR DADOS POR INGRESSO
    # ========================================================================
    
    ingressos = df_ordenado['Ingresso'].unique()
    
    for ingresso in ingressos:
        # Filtrar dados para este Ingresso
        df_grupo = df_ordenado[df_ordenado['Ingresso'] == ingresso].reset_index(drop=True)
        
        # ====================================================================
        # USAR EXPANDERS PARA CADA INGRESSO
        # ====================================================================
        
        with st.expander(f"📅 Ingresso: {ingresso} ({len(df_grupo)} alunos)", expanded=False):
            
            # Preparar dados para exibição em tabela
            df_tabela = df_grupo[['Matrícula', 'Nome', 'Cota']].copy()
            
            # Renomear colunas para exibição
            df_tabela.columns = ['Matrícula', 'Nome', 'Cota']
            
            # Resetar índice para começar de 1
            df_tabela.reset_index(drop=True, inplace=True)
            df_tabela.index = df_tabela.index + 1
            
            # Exibir tabela com formatação
            st.dataframe(
                df_tabela,
                use_container_width=True,
                hide_index=False,
                height=400
            )
            
            # Mostrar resumo do grupo
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de alunos", len(df_grupo))
            
            # Contar por Cota
            cotas_count = df_grupo['Cota'].value_counts()
            
            with col2:
                st.metric("Ampla concorrência", cotas_count.get('Ampla concorrência', 0))
            
            with col3:
                st.metric("Cotas", len(df_grupo) - cotas_count.get('Ampla concorrência', 0))
    
    # ========================================================================
    # RESUMO GERAL
    # ========================================================================
    
    st.markdown("---")
    st.markdown("### 📊 Resumo Geral")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de alunos", len(df_ordenado))
    
    with col2:
        st.metric("Períodos de ingresso", len(ingressos))
    
    cotas_total = df_ordenado['Cota'].value_counts()
    with col3:
        st.metric("Ampla concorrência", cotas_total.get('Ampla concorrência', 0))
    
    # ========================================================================
    # OPÇÃO DE DOWNLOAD DOS DADOS EM CSV
    # ========================================================================
    
    st.markdown("---")
    st.markdown("### 📥 Exportar Dados")
    
    # Converter para CSV
    csv = df_ordenado.to_csv(index=False, encoding='utf-8')
    
    st.download_button(
        label="📥 Baixar como CSV",
        data=csv,
        file_name="alunos_ativos.csv",
        mime="text/csv"
    )

except FileNotFoundError:
    st.error("❌ Erro: Arquivo da base de dados não encontrado.")
    st.info(f"Procure pelo arquivo em: C:\\Users\\Angelus\\Dropbox\\prouenf\\arquivos de análise\\T6 - Aplicativo Coordenação\\Sistema_V1\\streamlit_local\\bases\\info_geral2026-1.xlsx")

except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {str(e)}")
    st.info("Verifique se o arquivo Excel está no formato correto e contém as colunas: Matrícula, Nome, Ingresso, Cota")

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    Sistema de Informação Acadêmica | Consulta de Alunos Ativos
</div>
""", unsafe_allow_html=True)