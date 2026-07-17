# ============================================================================
# 02_Coeficientes_Rendimento.py - Página de Consulta de Rendimento do Aluno
# ============================================================================
# Consulta de coeficientes de rendimento e rendimento por período
# Integrado ao sistema Streamlit de autenticação

import streamlit as st
import pandas as pd
from utils import inicializar_sessao, está_logado, obter_usuario, fazer_logout

# ============================================================================
# CONFIGURAÇÕES DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Coeficientes de Rendimento",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS PARA CENTRALIZAR TABELAS
# ============================================================================

st.markdown("""
<style>
    .dataframe {
        margin: 0 auto !important;
    }
    .dataframe thead th {
        text-align: center !important;
        font-weight: bold !important;
    }
    .dataframe tbody td {
        text-align: center !important;
    }
    .dataframe tbody th {
        text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)

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

st.markdown("# 📊 Coeficientes de Rendimento")
st.markdown("*Consulte os coeficientes globais e rendimento por período do aluno*")
st.markdown("---")

# ============================================================================
# FUNÇÃO PARA CARREGAR BASES DE DADOS
# ============================================================================

@st.cache_data
def carregar_bases():
    """Carrega as bases de dados de rendimento"""
    from path_config import CAMINHOS
    
    # Carregar coeficientes de rendimento
    rend_coef_df = pd.read_excel('bases/coef_rend2026-1.xlsx')
    
    # Carregar períodos de rendimento
    rend_per_df = pd.read_excel('bases/periodo_rend2026-1.xlsx')
    
    return rend_coef_df, rend_per_df

# ============================================================================
# FUNÇÃO PARA VALIDAR MATRÍCULA
# ============================================================================

def validar_matricula(mat):
    """Valida se a matrícula tem 11 dígitos numéricos"""
    if len(mat) != 11 or not mat.isdigit():
        return False
    return True

# ============================================================================
# FUNÇÃO PARA BUSCAR ALUNO
# ============================================================================

def buscar_aluno(mat, rend_coef_df, rend_per_df):
    """Busca o aluno nas bases de dados e retorna os dados"""
    
    # Converter coluna Matrícula para string para comparação
    rend_coef_df['Matrícula'] = rend_coef_df['Matrícula'].astype(str).str.zfill(11)
    
    # Procurar pela matrícula
    linha_encontrada = rend_coef_df[rend_coef_df['Matrícula'] == mat]
    
    if linha_encontrada.empty:
        return None, None
    
    # Converter coluna Matrícula em rend_per_df para string
    rend_per_df['Matrícula'] = rend_per_df['Matrícula'].astype(str).str.zfill(11)
    
    # Filtrar períodos do aluno
    rend_alu_df = rend_per_df[rend_per_df['Matrícula'] == mat]
    
    return linha_encontrada, rend_alu_df

# ============================================================================
# INTERFACE PRINCIPAL
# ============================================================================

# Inicializar estado da sessão para controlar fluxo
if 'mostrar_form' not in st.session_state:
    st.session_state.mostrar_form = True
if 'matricula_consulta' not in st.session_state:
    st.session_state.matricula_consulta = None
if 'resultado_encontrado' not in st.session_state:
    st.session_state.resultado_encontrado = False

# ========================================================================
# FORMULÁRIO DE ENTRADA
# ========================================================================

if st.session_state.mostrar_form:
    st.markdown("### 📝 Digite a matrícula do aluno")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        matricula_input = st.text_input(
            "Matrícula do Aluno (11 dígitos)",
            placeholder="Ex: 00115110777",
            key="input_matricula"
        )
    
    with col2:
        st.write("")  # Espaçador para alinhamento
        botao_buscar = st.button("🔍 Buscar", use_container_width=True)
    
    # ====================================================================
    # PROCESSAR BUSCA
    # ====================================================================
    
    if botao_buscar:
        if not matricula_input:
            st.error("❌ Digite um número de matrícula para buscar.")
        elif not validar_matricula(matricula_input):
            st.error("❌ Digite um número de matrícula válido. A matrícula deve ter exatamente 11 dígitos numéricos.")
        else:
            # Carregar bases de dados
            try:
                rend_coef_df, rend_per_df = carregar_bases()
                
                # Buscar aluno
                linha_encontrada, rend_alu_df = buscar_aluno(matricula_input, rend_coef_df, rend_per_df)
                
                if linha_encontrada is None:
                    st.error("❌ Esta matrícula não existe na base de dados.")
                else:
                    st.session_state.matricula_consulta = matricula_input
                    st.session_state.resultado_encontrado = True
                    st.session_state.mostrar_form = False
                    st.session_state.linha_encontrada = linha_encontrada
                    st.session_state.rend_alu_df = rend_alu_df
                    st.rerun()
            
            except FileNotFoundError:
                st.error("❌ Erro: Arquivos de base de dados não encontrados.")
                st.info("Verifique se os arquivos estão no caminho: C:\\Users\\Angelus\\Dropbox\\prouenf\\arquivos de análise\\T6 - Aplicativo Coordenação\\Sistema_V1\\Bases")
            
            except Exception as e:
                st.error(f"❌ Erro ao processar os dados: {str(e)}")

# ========================================================================
# EXIBIR RELATÓRIO
# ========================================================================

if st.session_state.resultado_encontrado and st.session_state.matricula_consulta:
    
    linha_encontrada = st.session_state.linha_encontrada
    rend_alu_df = st.session_state.rend_alu_df
    mat = st.session_state.matricula_consulta
    
    # ====================================================================
    # SEÇÃO 1: INFORMAÇÕES DO ALUNO
    # ====================================================================
    
    st.markdown("---")
    st.markdown("### 📋 Informações do Aluno")
    
    # Extrair valores da linha encontrada
    matricula = linha_encontrada['Matrícula'].values[0]
    nome = linha_encontrada['Nome'].values[0]
    ingresso = linha_encontrada['Ingresso'].values[0]
    cota = linha_encontrada['Cota'].values[0]
    
    # Criar tabela de informações básicas
    dados_aluno = {
        'Matrícula': [matricula],
        'Nome': [nome],
        'Ingresso': [ingresso],
        'Cota': [cota]
    }
    df_aluno = pd.DataFrame(dados_aluno)
    
    # Exibir com estilo centralizado
    st.dataframe(
        df_aluno.style.set_properties(**{
            'text-align': 'center',
            'border': '1px solid #ddd'
        }).set_table_styles([{
            'selector': 'th',
            'props': [
                ('text-align', 'center'),
                ('font-weight', 'bold'),
                ('background-color', '#f0f0f0'),
                ('border', '1px solid #ddd')
            ]
        }]),
        use_container_width=True,
        hide_index=True
    )
    
    # ====================================================================
    # SEÇÃO 2: COEFICIENTES GLOBAIS DE RENDIMENTO
    # ====================================================================
    
    st.markdown("---")
    st.markdown("### 📊 Coeficientes Globais de Rendimento")
    
    # Colunas de coeficientes
    colunas_coef = ['Carga Horária Total', 'CRA', 'CEA', 'CRE', 'ECH', 'EPL', 'CP', 'CREN', 'CEAN']
    
    # Extrair valores dos coeficientes
    valores_coef = {}
    for col in colunas_coef:
        if col in linha_encontrada.columns:
            try:
                valor = float(linha_encontrada[col].values[0])
                # Formatar com 2 casas decimais
                valores_coef[col] = [f"{valor:.2f}"]
            except (ValueError, TypeError):
                valores_coef[col] = [linha_encontrada[col].values[0]]
        else:
            valores_coef[col] = [None]
    
    # Criar tabela de coeficientes
    df_coef = pd.DataFrame(valores_coef)
    
    # Exibir com estilo centralizado
    st.dataframe(
        df_coef.style.set_properties(**{
            'text-align': 'center',
            'border': '1px solid #ddd'
        }).set_table_styles([{
            'selector': 'th',
            'props': [
                ('text-align', 'center'),
                ('font-weight', 'bold'),
                ('background-color', '#f0f0f0'),
                ('border', '1px solid #ddd')
            ]
        }]),
        use_container_width=True,
        hide_index=True
    )
    
    # ====================================================================
    # SEÇÃO 3: RENDIMENTO POR PERÍODO
    # ====================================================================
    
    st.markdown("---")
    st.markdown("### 📅 Rendimento por Período")
    
    if rend_alu_df.empty:
        st.info("⚠️ Nenhum registro de período de rendimento encontrado para este aluno.")
    else:
        # Colunas de período
        colunas_periodo = ['Período', 'Carga Período', 'CR Período']
        
        # Verificar se as colunas existem
        colunas_disponiveis = [col for col in colunas_periodo if col in rend_alu_df.columns]
        
        if not colunas_disponiveis:
            # Tentar nomes alternativos
            mapeamento_colunas = {
                'Período': ['Período', 'periodo', 'PERÍODO'],
                'Carga Período': ['Carga Período', 'Carga período', 'carga_periodo', 'CARGA_PERÍODO'],
                'CR Período': ['CR Período', 'CR período', 'cr_periodo', 'CR_PERÍODO', 'CRP']
            }
            
            colunas_reais = []
            for col_desejado, alternativas in mapeamento_colunas.items():
                for alt in alternativas:
                    if alt in rend_alu_df.columns:
                        colunas_reais.append(alt)
                        break
            
            if len(colunas_reais) >= 3:
                colunas_periodo = colunas_reais
            else:
                colunas_periodo = colunas_reais if colunas_reais else rend_alu_df.columns.tolist()[:3]
        
        # Criar tabela de períodos
        df_periodo = rend_alu_df[colunas_periodo].reset_index(drop=True)
        
        # Formatar CR Período com 1 casa decimal
        if 'CR Período' in df_periodo.columns:
            df_periodo['CR Período'] = df_periodo['CR Período'].apply(
                lambda x: f"{float(x):.1f}" if pd.notna(x) else x
            )
        
        # Exibir com estilo centralizado
        st.dataframe(
            df_periodo.style.set_properties(**{
                'text-align': 'center',
                'border': '1px solid #ddd'
            }).set_table_styles([{
                'selector': 'th',
                'props': [
                    ('text-align', 'center'),
                    ('font-weight', 'bold'),
                    ('background-color', '#f0f0f0'),
                    ('border', '1px solid #ddd')
                ]
            }]),
            use_container_width=True,
            hide_index=True
        )
    
    # ====================================================================
    # BOTÃO PARA NOVA CONSULTA
    # ====================================================================
    
    st.markdown("---")
    
    if st.button("🔄 Fazer Nova Consulta", use_container_width=True):
        st.session_state.mostrar_form = True
        st.session_state.resultado_encontrado = False
        st.session_state.matricula_consulta = None
        st.rerun()

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    Sistema de Informação Acadêmica | Consulta de Coeficientes de Rendimento
</div>
""", unsafe_allow_html=True)