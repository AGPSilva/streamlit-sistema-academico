# ============================================================================
# 05_Cumprimento_Grade.py - Página de Consulta de Cumprimento da Grade
# ============================================================================
# Consulta de cumprimento da grade curricular por aluno
# Integrado ao sistema Streamlit de autenticação

import streamlit as st
import pandas as pd
import os
from utils import inicializar_sessao, está_logado, obter_usuario, fazer_logout
from processamento_cumprimento_grade import (
    validar_matricula,
    gerar_relatorio_cumprimento_grade
)

# ============================================================================
# CONFIGURAÇÕES DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Cumprimento da Grade",
    page_icon="📚",
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

st.markdown("# 📚 Cumprimento da Grade Curricular")
st.markdown("*Consulte o progresso do aluno em relação à grade curricular*")
st.markdown("---")

# ============================================================================
# DEFINIR CAMINHOS DOS ARQUIVOS
# ============================================================================

pasta_raiz = os.path.dirname(os.path.dirname(__file__))
pasta_bases = os.path.join(pasta_raiz, "bases")

caminhos = {
    'alunos_ativos': os.path.join(pasta_bases, "info_geral2026-1.xlsx"),
    'rendimento': os.path.join(pasta_bases, "rendimento_alunos_ativos.xlsx"),
    'grade_old': os.path.join(pasta_bases, "grade_old.xlsx"),
    'grade_new': os.path.join(pasta_bases, "grade_new.xlsx")
}

# ============================================================================
# SEÇÃO DE ENTRADA: CAMPO DE MATRÍCULA
# ============================================================================

st.markdown("### 🔍 Informe a Matrícula do Aluno")
st.markdown("*Digite o número da matrícula com 11 dígitos*")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    matricula_input = st.text_input(
        "Matrícula",
        placeholder="Ex: 20201100123",
        max_chars=11,
        label_visibility="collapsed"
    )

with col2:
    btn_consultar = st.button("🔎 Consultar", use_container_width=True)

st.markdown("---")

# ============================================================================
# FUNÇÃO AUXILIAR: COLORIR DATAFRAME
# ============================================================================

def colorir_dataframe(df, cursadas):
    """
    Aplica cores às linhas do DataFrame baseado no status de cursamento
    
    Args:
        df: pandas DataFrame
        cursadas: lista de booleanos indicando se cada linha foi cursada
    
    Returns:
        Styled DataFrame
    """
    
    def aplicar_cor(row):
        idx = row.name
        if idx < len(cursadas) and cursadas[idx]:
            # Verde para cursada
            return ['background-color: #d4edda; color: #155724'] * len(row)
        else:
            # Cinza para não cursada
            return ['background-color: #f8f9fa; color: #000000'] * len(row)
    
    return df.style.apply(aplicar_cor, axis=1)

# ============================================================================
# PROCESSAMENTO E VALIDAÇÃO
# ============================================================================

if btn_consultar:
    # Validar entrada
    if not matricula_input:
        st.error("❌ Por favor, digite uma matrícula")
    else:
        # Validar formato
        é_válida, mensagem_erro = validar_matricula(matricula_input)
        
        if not é_válida:
            st.error(mensagem_erro)
        else:
            # Tentar gerar relatório
            try:
                with st.spinner("⏳ Processando dados..."):
                    dfs, dados_aluno = gerar_relatorio_cumprimento_grade(
                        matricula_input,
                        caminhos
                    )
                
                # Exibir resultado com sucesso
                st.success(f"✅ Dados carregados com sucesso!")
                st.markdown("---")
                
                # Exibir informações do aluno
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Matrícula", matricula_input)
                
                with col2:
                    st.metric("Nome", dados_aluno['nome'][:30])
                
                with col3:
                    st.metric("Ingresso", dados_aluno['ingresso'])
                
                st.markdown("---")
                
                # ============================================================
                # EXIBIR LEGENDA DE CORES
                # ============================================================
                
                st.markdown("### 📊 Legenda de Cores")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    🟢 **Linha Verde**: Disciplina cursada
                    """)
                
                with col2:
                    st.markdown("""
                    ⚫ **Linha Cinza**: Disciplina não cursada
                    """)
                
                st.markdown("---")
                
                # ============================================================
                # EXIBIR DISCIPLINAS OBRIGATÓRIAS POR PERÍODO
                # ============================================================
                
                st.markdown("### 📚 Disciplinas Obrigatórias")
                
                for periodo in range(1, 11):
                    chave = f'periodo_{periodo}'
                    
                    if chave in dfs:
                        df_periodo = dfs[chave]['df']
                        cursadas = dfs[chave]['cursadas']
                        
                        # Exibir período com subtítulo
                        with st.expander(f"📖 Período {periodo} ({len(df_periodo)} disciplinas)", expanded=False):
                            st.dataframe(
                                colorir_dataframe(df_periodo, cursadas),
                                use_container_width=True,
                                hide_index=True,
                                height=300
                            )
                
                st.markdown("---")
                
                # ============================================================
                # EXIBIR DISCIPLINAS OPTATIVAS
                # ============================================================
                
                st.markdown("### 🎓 Disciplinas Optativas")
                
                if 'optativas' in dfs:
                    df_opt = dfs['optativas']['df']
                    cursadas_opt = dfs['optativas']['cursadas']
                    
                    if len(df_opt) > 0:
                        st.dataframe(
                            colorir_dataframe(df_opt, cursadas_opt),
                            use_container_width=True,
                            hide_index=True,
                            height=300
                        )
                    else:
                        st.info("ℹ️ Nenhuma disciplina optativa cursada")
                
                st.markdown("---")
                
                # ============================================================
                # EXIBIR DISCIPLINAS ELETIVAS
                # ============================================================
                
                st.markdown("### ⚡ Disciplinas Eletivas")
                
                if 'eletivas' in dfs:
                    df_ele = dfs['eletivas']['df']
                    cursadas_ele = dfs['eletivas']['cursadas']
                    
                    if len(df_ele) > 0:
                        st.dataframe(
                            colorir_dataframe(df_ele, cursadas_ele),
                            use_container_width=True,
                            hide_index=True,
                            height=300
                        )
                    else:
                        st.info("ℹ️ Nenhuma disciplina eletiva cursada")
                
                st.markdown("---")
                
                # ============================================================
                # GERAR E EXIBIR RELATÓRIO EM TEXTO
                # ============================================================
                
                def gerar_relatorio_texto(dfs, matricula, nome, ingresso):
                    """Gera versão em texto do relatório para download"""
                    linhas = []
                    
                    linhas.append("=" * 80)
                    linhas.append("CUMPRIMENTO DA GRADE CURRICULAR")
                    linhas.append("=" * 80)
                    linhas.append(f"\nMatrícula: {matricula}")
                    linhas.append(f"Nome: {nome}")
                    linhas.append(f"Ingresso: {ingresso}")
                    linhas.append("")
                    
                    # Obrigatórias
                    linhas.append("=" * 80)
                    linhas.append("DISCIPLINAS OBRIGATÓRIAS")
                    linhas.append("=" * 80)
                    
                    for periodo in range(1, 11):
                        chave = f'periodo_{periodo}'
                        if chave in dfs:
                            df = dfs[chave]['df']
                            cursadas = dfs[chave]['cursadas']
                            
                            linhas.append(f"\nPeríodo {periodo}:")
                            linhas.append("-" * 80)
                            
                            for idx, row in df.iterrows():
                                status = "✅ CURSADA" if cursadas[idx] else "❌ NÃO CURSADA"
                                linhas.append(f"{row['Sigla']:15} | {row['Disciplina']:45} | {status:15} | {row['Período']}")
                    
                    # Optativas
                    linhas.append("\n" + "=" * 80)
                    linhas.append("DISCIPLINAS OPTATIVAS")
                    linhas.append("=" * 80)
                    
                    if 'optativas' in dfs and len(dfs['optativas']['df']) > 0:
                        for idx, row in dfs['optativas']['df'].iterrows():
                            linhas.append(f"{row['Sigla']:15} | {row['Disciplina']:45} | {row['Período']}")
                    else:
                        linhas.append("Nenhuma disciplina optativa cursada")
                    
                    # Eletivas
                    linhas.append("\n" + "=" * 80)
                    linhas.append("DISCIPLINAS ELETIVAS")
                    linhas.append("=" * 80)
                    
                    if 'eletivas' in dfs and len(dfs['eletivas']['df']) > 0:
                        for idx, row in dfs['eletivas']['df'].iterrows():
                            linhas.append(f"{row['Sigla']:15} | {row['Disciplina']:45} | {row['Período']}")
                    else:
                        linhas.append("Nenhuma disciplina eletiva cursada")
                    
                    linhas.append("\n" + "=" * 80)
                    
                    return "\n".join(linhas)
                
                relatorio_texto = gerar_relatorio_texto(dfs, matricula_input, dados_aluno['nome'], dados_aluno['ingresso'])
                
                # ============================================================
                # SEÇÃO DE DOWNLOAD
                # ============================================================
                
                st.markdown("### 📥 Exportar Relatório")
                
                st.download_button(
                    label="📥 Baixar Relatório Completo (.txt)",
                    data=relatorio_texto,
                    file_name=f"cumprimento_grade_{matricula_input}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
            except Exception as e:
                erro_msg = str(e)
                
                if "Matrícula não encontrada" in erro_msg:
                    st.error(f"❌ {erro_msg}")
                    st.info("💡 Certifique-se de que digitou corretamente a matrícula do aluno e que ele está ativo no período corrente.")
                else:
                    st.error(f"❌ Erro ao processar: {erro_msg}")
                    st.info("💡 Verifique se todos os arquivos necessários estão na pasta `bases/`")

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    Sistema de Informação Acadêmica | Consulta de Cumprimento da Grade Curricular
</div>
""", unsafe_allow_html=True)