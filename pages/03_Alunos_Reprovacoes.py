# ============================================================================
# 03_Alunos_Reprovacoes.py - Página de Consulta de Alunos com Reprovações
# ============================================================================
# Consulta de alunos reprovados em uma, duas ou múltiplas disciplinas
# Integrado ao sistema Streamlit de autenticação

import streamlit as st
import pandas as pd
import os
from utils import inicializar_sessao, está_logado, obter_usuario, fazer_logout
from processamento_reprovacoes import (
    gerar_relatorio_reprovados_uma_vez,
    gerar_relatorio_reprovados_duas_vezes,
    gerar_relatorio_reprovacoes_multiplas_sem_cursar
)

# ============================================================================
# CONFIGURAÇÕES DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Alunos com Reprovações",
    page_icon="📝",
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

st.markdown("# 📝 Alunos com Reprovações")
st.markdown("*Consulte alunos reprovados em disciplinas*")
st.markdown("---")

# ============================================================================
# MENU COM 3 OPÇÕES
# ============================================================================

st.markdown("### 🔍 Escolha uma opção:")

opcao = st.radio(
    "Tipo de Consulta:",
    [
        "Reprovação em 1 disciplina (inscrito nela ou equivalente)",
        "Reprovação em 2 disciplinas (inscrito nelas ou equivalentes)",
        "Duas ou mais reprovações na mesma disciplina sem aprovação posterior e sem inscrição no período corrente"
    ],
    label_visibility="collapsed"
)

st.markdown("---")

# ============================================================================
# DEFINIR CAMINHOS DOS ARQUIVOS
# ============================================================================
# Usa caminhos relativos para funcionar em qualquer máquina/servidor

caminho_arquivo_uma_vez = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "bases",
    "reprovados_uma_vez_cursando.xlsx"
)

caminho_arquivo_duas_vezes = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "bases",
    "reprovados_duas_vezes_cursando.xlsx"
)

caminho_arquivo_multiplas = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "bases",
    "reprovacoes_multiplas_sem_cursar.xlsx"
)

# ============================================================================
# PROCESSAMENTO DAS OPÇÕES
# ============================================================================

if opcao == "Reprovação em 1 disciplina (inscrito nela ou equivalente)":
    st.markdown("### 📋 Alunos com Reprovação em 1 Disciplina")
    st.markdown("*Alunos que tiveram reprovação em apenas uma disciplina e estão inscritos nela ou em disciplina equivalente*")
    st.markdown("---")
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(caminho_arquivo_uma_vez):
            st.error(f"❌ Arquivo não encontrado: {caminho_arquivo_uma_vez}")
            st.info("Certifique-se de que o arquivo `reprovados_uma_vez_cursando.xlsx` está na pasta `bases/`")
        else:
            # Gerar relatório
            with st.spinner("⏳ Processando dados..."):
                relatorio_formatado, dados_processados, df_original = gerar_relatorio_reprovados_uma_vez(
                    caminho_arquivo_uma_vez
                )
            
            # Exibir resultado
            if relatorio_formatado:
                st.success(f"✅ {len(dados_processados)} aluno(s) encontrado(s)")
                st.markdown("---")
                
                # Exibir relatório formatado
                for linha in relatorio_formatado:
                    if linha == "":
                        st.write("")  # Linha em branco
                    else:
                        st.markdown(linha)
                
                st.markdown("---")
                
                # Opção para baixar dados em Excel
                st.markdown("### 📥 Exportar Dados")
                
                # Preparar DataFrame para download
                df_export = pd.DataFrame([
                    {
                        'Matrícula': matricula,
                        'Nome': aluno['nome'],
                        'Ingresso': aluno['ingresso'],
                        'Disciplina (Reprovado)': rep['disciplina_reprovacao'],
                        'Sigla (Reprovado)': rep['sigla_reprovacao'],
                        'Período (Reprovado)': rep['periodo_reprovacao'],
                        'Disciplina (Cursando)': rep['disciplina_cursando'],
                        'Sigla (Cursando)': rep['sigla_cursando'],
                        'Período (Cursando)': rep['periodo_cursando']
                    }
                    for matricula, aluno in dados_processados.items()
                    for rep in aluno['reprovacoes']
                ])
                
                # Botão para download
                csv = df_export.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Baixar como CSV",
                    data=csv,
                    file_name="alunos_reprovacao_uma_vez.csv",
                    mime="text/csv"
                )
            else:
                st.info("ℹ️ Nenhum aluno encontrado com este critério.")
    
    except Exception as e:
        st.error(f"❌ Erro ao processar dados: {str(e)}")
        st.info("Verifique se o arquivo está no formato correto (.xlsx) e contém as colunas esperadas.")

elif opcao == "Reprovação em 2 disciplinas (inscrito nelas ou equivalentes)":
    st.markdown("### 📋 Alunos com Reprovação em 2 Disciplinas")
    st.markdown("*Alunos que tiveram reprovação em exatamente duas disciplinas e estão inscritos nelas ou em disciplinas equivalentes*")
    st.markdown("---")
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(caminho_arquivo_duas_vezes):
            st.error(f"❌ Arquivo não encontrado: {caminho_arquivo_duas_vezes}")
            st.info("Certifique-se de que o arquivo `reprovados_duas_vezes_cursando.xlsx` está na pasta `bases/`")
        else:
            # Gerar relatório
            with st.spinner("⏳ Processando dados..."):
                relatorio_formatado, dados_processados, df_original = gerar_relatorio_reprovados_duas_vezes(
                    caminho_arquivo_duas_vezes
                )
            
            # Exibir resultado
            if relatorio_formatado:
                st.success(f"✅ {len(dados_processados)} aluno(s) encontrado(s)")
                st.markdown("---")
                
                # Exibir relatório formatado
                for linha in relatorio_formatado:
                    if linha == "":
                        st.write("")  # Linha em branco
                    else:
                        st.markdown(linha)
                
                st.markdown("---")
                
                # Opção para baixar dados em Excel
                st.markdown("### 📥 Exportar Dados")
                
                # Preparar DataFrame para download
                df_export = pd.DataFrame([
                    {
                        'Matrícula': matricula,
                        'Nome': aluno['nome'],
                        'Ingresso': aluno['ingresso'],
                        'Disciplina': disc['disciplina'],
                        'Sigla': disc['sigla'],
                        'Período 1ª Reprovação': disc['periodo_reprovacao_1'],
                        'Período 2ª Reprovação': disc['periodo_reprovacao_2'],
                        'Período Cursando': disc['periodo_cursando']
                    }
                    for matricula, aluno in dados_processados.items()
                    for disc in aluno['disciplinas']
                ])
                
                # Botão para download
                csv = df_export.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Baixar como CSV",
                    data=csv,
                    file_name="alunos_reprovacao_duas_vezes.csv",
                    mime="text/csv"
                )
            else:
                st.info("ℹ️ Nenhum aluno encontrado com este critério.")
    
    except Exception as e:
        st.error(f"❌ Erro ao processar dados: {str(e)}")
        st.info("Verifique se o arquivo está no formato correto (.xlsx) e contém as colunas esperadas.")

elif opcao == "Duas ou mais reprovações na mesma disciplina sem aprovação posterior e sem inscrição no período corrente":
    st.markdown("### 📋 Alunos com Múltiplas Reprovações na Mesma Disciplina")
    st.markdown("*Alunos que tiveram duas ou mais reprovações na mesma disciplina ou em equivalentes, sem aprovação posterior e sem estar inscrito no período corrente*")
    st.markdown("---")
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(caminho_arquivo_multiplas):
            st.error(f"❌ Arquivo não encontrado: {caminho_arquivo_multiplas}")
            st.info("Certifique-se de que o arquivo `reprovacoes_multiplas_sem_cursar.xlsx` está na pasta `bases/`")
        else:
            # Gerar relatório
            with st.spinner("⏳ Processando dados..."):
                relatorio_formatado, dados_processados, df_original = gerar_relatorio_reprovacoes_multiplas_sem_cursar(
                    caminho_arquivo_multiplas
                )
            
            # Exibir resultado
            if relatorio_formatado:
                st.success(f"✅ {len(dados_processados)} aluno(s) encontrado(s)")
                st.markdown("---")
                
                # Exibir relatório formatado
                for linha in relatorio_formatado:
                    if linha == "":
                        st.write("")  # Linha em branco
                    else:
                        st.markdown(linha)
                
                st.markdown("---")
                
                # Opção para baixar dados em Excel
                st.markdown("### 📥 Exportar Dados")
                
                # Preparar DataFrame para download
                df_export_data = []
                for matricula, aluno in dados_processados.items():
                    for disc in aluno['disciplinas']:
                        for i, periodo in enumerate(disc['periodos'], 1):
                            df_export_data.append({
                                'Matrícula': matricula,
                                'Nome': aluno['nome'],
                                'Ingresso': aluno['ingresso'],
                                'Disciplina': disc['disciplina'],
                                'Sigla': disc['sigla'],
                                f'Período Reprovação {i}': periodo
                            })
                
                df_export = pd.DataFrame(df_export_data)
                
                # Botão para download
                csv = df_export.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Baixar como CSV",
                    data=csv,
                    file_name="alunos_reprovacao_multiplas_sem_cursar.csv",
                    mime="text/csv"
                )
            else:
                st.info("ℹ️ Nenhum aluno encontrado com este critério.")
    
    except Exception as e:
        st.error(f"❌ Erro ao processar dados: {str(e)}")
        st.info("Verifique se o arquivo está no formato correto (.xlsx) e contém as colunas esperadas.")

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    Sistema de Informação Acadêmica | Consulta de Alunos com Reprovações
</div>
""", unsafe_allow_html=True)