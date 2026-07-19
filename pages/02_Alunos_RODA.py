# ============================================================================
# pages/02_Alunos_RODA.py - Página de Gerenciamento de Alunos em RODA (v2.1)
# ============================================================================
# CORREÇÃO: Sempre resetar session_state para o tamanho atual do DataFrame
# ATUALIZAÇÃO: Adicionadas 4 colunas novas (reprovação último período, reprovações repetidas, ECH, EPL)

import streamlit as st
import pandas as pd
import os
import re
from utils import inicializar_sessao, está_logado, obter_usuario, fazer_logout
from processamento_roda import ProcessadorRODA
from config import PERIODO_CORRENTE

# ============================================================================
# CONFIGURAÇÕES DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Alunos em RODA",
    page_icon="📊",
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

st.markdown("# 📊 Alunos em RODA")
st.markdown("*Gerenciamento de alunos em RODA e categorias relacionadas*")
st.markdown("---")

# ============================================================================
# INICIALIZAR PROCESSADOR
# ============================================================================

try:
    processador = ProcessadorRODA()
except Exception as e:
    st.error(f"❌ Erro ao inicializar: {e}")
    st.info("💡 Verifique se as credenciais do Google Sheets estão corretas.")
    st.stop()

# ============================================================================
# FUNÇÕES AUXILIARES DE VALIDAÇÃO
# ============================================================================

def validar_matricula(matricula: str) -> tuple:
    """
    Valida o formato da matrícula (11 dígitos)
    
    Returns:
        tuple: (é_válida, mensagem_erro)
    """
    if not matricula:
        return False, "❌ Por favor, digite uma matrícula"
    
    if len(matricula) != 11:
        return False, "❌ Matrícula deve ter 11 dígitos"
    
    if not matricula.isdigit():
        return False, "❌ Matrícula deve conter apenas números"
    
    return True, ""

def validar_ingresso(ingresso: str) -> tuple:
    """
    Valida o formato do ingresso (AAAA/[1|2])
    
    Returns:
        tuple: (é_válido, mensagem_erro)
    """
    if not ingresso:
        return False, "❌ Por favor, digite o período de ingresso"
    
    # Verificar formato com regex
    padrao = r'^\d{4}/[12]$'
    if not re.match(padrao, ingresso):
        return False, "❌ Formato deve ser AAAA/[1|2], ex: 2022/1"
    
    # Extrair ano
    try:
        ano = int(ingresso.split('/')[0])
        ano_corrente = int(PERIODO_CORRENTE.split('/')[0])
        
        if ano < 2009:
            return False, "❌ Ano não pode ser anterior a 2009"
        
        if ano > ano_corrente:
            return False, f"❌ Ano não pode ser superior a {ano_corrente}"
        
        return True, ""
    
    except Exception as e:
        return False, f"❌ Erro ao validar ingresso: {e}"

def exibir_tabela_com_checkbox(df, chave_sessao):
    """
    Exibe tabela com checkbox para seleção múltipla
    
    Args:
        df: DataFrame com dados (DEVE TER ÍNDICE RESETADO)
        chave_sessao: chave para armazenar seleções em st.session_state
    
    Returns:
        list: índices dos registros selecionados
    """
    if df.empty:
        st.info("ℹ️ Nenhum registro encontrado")
        return []
    
    # CORREÇÃO: SEMPRE resetar session_state para o tamanho ATUAL
    st.session_state[chave_sessao] = [False] * len(df)
    
    # Criar cabeçalho
    col1, col2, col3, col4 = st.columns([0.5, 2, 2, 2])
    
    with col1:
        st.write("**Sel.**")
    with col2:
        st.write("**Matrícula**")
    with col3:
        st.write("**Nome**")
    with col4:
        st.write("**Ingresso**")
    
    st.markdown("---")
    
    # Exibir linhas com checkbox
    for idx, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([0.5, 2, 2, 2])
        
        with col1:
            st.session_state[chave_sessao][idx] = st.checkbox(
                label="",
                value=st.session_state[chave_sessao][idx],
                key=f"checkbox_{chave_sessao}_{idx}"
            )
        
        with col2:
            st.write(row['matrícula'])
        
        with col3:
            st.write(row['nome'][:30])
        
        with col4:
            st.write(row['ingresso'])
    
    # Retornar índices selecionados
    indices_selecionados = [i for i, selecionado in enumerate(st.session_state[chave_sessao]) if selecionado]
    
    return indices_selecionados

# ============================================================================
# MENU PRINCIPAL - SELEÇÃO DE CATEGORIA
# ============================================================================

st.markdown("### 📋 Selecione uma Categoria")

categorias = [
    "Alunos já em RODA",
    "Alunos com matrícula reativada",
    "Alunos com condições especiais",
    "Alunos que se enquadram em RODA"
]

categoria_selecionada = st.selectbox(
    "Categoria",
    categorias,
    label_visibility="collapsed"
)

st.markdown("---")

# ============================================================================
# FUNCIONALIDADE 1: ALUNOS JÁ EM RODA
# ============================================================================

if categoria_selecionada == "Alunos já em RODA":
    st.markdown("### 👥 Alunos já em RODA")
    
    # Abas para operações
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Mostrar",
        "➕ Incluir",
        "🗑️ Excluir",
        "✏️ Editar"
    ])
    
    # ====================================================================
    # ABA 1: MOSTRAR
    # ====================================================================
    
    with tab1:
        st.markdown("#### Alunos Atualmente em RODA")
        
        try:
            df_em_roda = processador.ler_google_sheet('eh_roda')
            
            if df_em_roda.empty:
                st.info("ℹ️ Não há alunos em RODA atualmente")
            else:
                # Exibir apenas as colunas necessárias
                df_exibir = df_em_roda[['matrícula', 'nome', 'ingresso']].copy()
                st.dataframe(df_exibir, use_container_width=True, hide_index=True)
                st.success(f"✅ Total de alunos em RODA: {len(df_em_roda)}")
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {e}")
    
    # ====================================================================
    # ABA 2: INCLUIR
    # ====================================================================
    
    with tab2:
        st.markdown("#### Incluir Aluno em RODA")
        
        # Campos de entrada
        matricula_input = st.text_input(
            "Matrícula",
            placeholder="Ex: 20201100123",
            max_chars=11,
            key="incluir_roda_matricula"
        )
        
        nome_input = st.text_input(
            "Nome",
            placeholder="Ex: João da Silva",
            key="incluir_roda_nome"
        )
        
        ingresso_input = st.text_input(
            "Ingresso",
            placeholder="Ex: 2022/1",
            key="incluir_roda_ingresso"
        )
        
        # Botão de confirmação
        if st.button("✅ Confirmar Inclusão", use_container_width=True, key="confirmar_incluir_roda"):
            # Validar matrícula
            é_válida, msg_erro = validar_matricula(matricula_input)
            if not é_válida:
                st.error(msg_erro)
            else:
                # Validar ingresso
                é_válido, msg_erro = validar_ingresso(ingresso_input)
                if not é_válido:
                    st.error(msg_erro)
                else:
                    # Validar nome
                    if not nome_input or not nome_input.strip():
                        st.error("❌ Por favor, digite o nome do aluno")
                    else:
                        try:
                            # Verificar se já está em RODA
                            if processador.matricula_existe_em_roda(matricula_input):
                                st.error("Este aluno já se encontra em RODA")
                            else:
                                # Inserir na base
                                processador.adicionar_aluno_em_roda(
                                    matricula_input,
                                    nome_input.strip(),
                                    ingresso_input,
                                    True
                                )
                                st.success("✅ Aluno incluído em RODA com sucesso")
                                st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erro ao incluir: {e}")
    
    # ====================================================================
    # ABA 3: EXCLUIR (CORRIGIDA)
    # ====================================================================
    
    with tab3:
        st.markdown("#### Excluir Alunos de RODA")
        
        try:
            df_em_roda = processador.ler_google_sheet('eh_roda')
            
            if df_em_roda.empty:
                st.info("ℹ️ Não há alunos em RODA para excluir")
            else:
                # Resetar índice
                df_em_roda = df_em_roda.reset_index(drop=True)
                
                # Exibir com checkbox
                indices_selecionados = exibir_tabela_com_checkbox(
                    df_em_roda[['matrícula', 'nome', 'ingresso']],
                    "checkbox_roda_excluir"
                )
                
                if indices_selecionados:
                    st.markdown("---")
                    
                    # Guardar matrículas antes de excluir
                    matriculas_para_excluir = [df_em_roda.iloc[idx]['matrícula'] for idx in indices_selecionados]
                    nomes_para_excluir = [df_em_roda.iloc[idx]['nome'] for idx in indices_selecionados]
                    
                    # Mostrar alunos selecionados para exclusão
                    st.markdown(f"**⚠️ {len(matriculas_para_excluir)} aluno(s) selecionado(s) para exclusão:**")
                    
                    for matricula, nome in zip(matriculas_para_excluir, nomes_para_excluir):
                        st.write(f"• {matricula} - {nome}")
                    
                    # Confirmar exclusão
                    if st.button("🗑️ Confirmar Exclusão", use_container_width=True, key="confirmar_excluir_roda"):
                        try:
                            excluidos = 0
                            erros = []
                            
                            # Usar matrículas guardadas (não índices)
                            for matricula in matriculas_para_excluir:
                                try:
                                    processador.remover_aluno_de_roda(matricula)
                                    excluidos += 1
                                except Exception as e:
                                    erros.append(f"{matricula}: {str(e)}")
                            
                            if excluidos > 0:
                                st.success(f"✅ {excluidos} aluno(s) excluído(s) com sucesso")
                            
                            if erros:
                                st.warning(f"⚠️ Erros: {', '.join(erros)}")
                            
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erro ao excluir: {e}")
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {e}")
    
    # ====================================================================
    # ABA 4: EDITAR
    # ====================================================================
    
    with tab4:
        st.markdown("#### Editar Alunos em RODA")
        
        try:
            df_em_roda = processador.ler_google_sheet('eh_roda')
            
            if df_em_roda.empty:
                st.info("ℹ️ Não há alunos em RODA para editar")
            else:
                # Resetar índice
                df_em_roda = df_em_roda.reset_index(drop=True)
                
                # Seleção de aluno
                opcoes_alunos = [f"{row['matrícula']} - {row['nome']}" 
                                for _, row in df_em_roda.iterrows()]
                
                indice_selecionado = st.selectbox(
                    "Selecione um aluno",
                    range(len(df_em_roda)),
                    format_func=lambda x: opcoes_alunos[x],
                    key="editar_roda_select"
                )
                
                # Obter aluno selecionado
                aluno = df_em_roda.iloc[indice_selecionado]
                matricula_original = aluno['matrícula']
                
                st.markdown("---")
                st.markdown("#### Dados do Aluno")
                
                # Usar container para forçar re-renderização
                with st.container():
                    # Criar unique keys baseados no índice para evitar cache
                    matricula_key = f"editar_roda_matricula_{indice_selecionado}"
                    nome_key = f"editar_roda_nome_{indice_selecionado}"
                    ingresso_key = f"editar_roda_ingresso_{indice_selecionado}"
                    
                    # Campos editáveis com valores sincronizados
                    matricula_edit = st.text_input(
                        "Matrícula",
                        value=aluno['matrícula'],
                        key=matricula_key
                    )
                    
                    nome_edit = st.text_input(
                        "Nome",
                        value=aluno['nome'],
                        key=nome_key
                    )
                    
                    ingresso_edit = st.text_input(
                        "Ingresso",
                        value=aluno['ingresso'],
                        key=ingresso_key
                    )
                
                # Confirmar edição
                if st.button("💾 Salvar Alterações", use_container_width=True, key="confirmar_editar_roda"):
                    # Validar matrícula
                    é_válida, msg_erro = validar_matricula(matricula_edit)
                    if not é_válida:
                        st.error(msg_erro)
                    else:
                        # Validar ingresso
                        é_válido, msg_erro = validar_ingresso(ingresso_edit)
                        if not é_válido:
                            st.error(msg_erro)
                        else:
                            # Validar nome
                            if not nome_edit or not nome_edit.strip():
                                st.error("❌ Por favor, digite um nome válido")
                            else:
                                try:
                                    # Atualizar na base com matrícula antiga e nova
                                    processador.atualizar_aluno_em_roda(
                                        matricula_original,
                                        matricula_edit,
                                        nome_edit.strip(),
                                        ingresso_edit,
                                        True
                                    )
                                    st.success("✅ Aluno atualizado com sucesso")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro ao atualizar: {e}")
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {e}")

# ============================================================================
# FUNCIONALIDADE 2: ALUNOS COM MATRÍCULA REATIVADA
# ============================================================================

elif categoria_selecionada == "Alunos com matrícula reativada":
    st.markdown("### 🔄 Alunos com Matrícula Reativada")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Mostrar",
        "➕ Incluir",
        "🗑️ Excluir",
        "✏️ Editar"
    ])
    
    with tab1:
        st.markdown("#### Alunos com Matrícula Reativada")
        
        try:
            df_mat_reativada = processador.ler_google_sheet('mat_reativada')
            
            if df_mat_reativada.empty:
                st.info("ℹ️ Não há alunos com matrícula reativada")
            else:
                df_exibir = df_mat_reativada[['matrícula', 'nome', 'ingresso']].copy()
                st.dataframe(df_exibir, use_container_width=True, hide_index=True)
                st.success(f"✅ Total: {len(df_mat_reativada)}")
        
        except Exception as e:
            st.error(f"❌ Erro: {e}")
    
    with tab2:
        st.markdown("#### Incluir Aluno com Matrícula Reativada")
        
        matricula_input = st.text_input(
            "Matrícula",
            placeholder="Ex: 20201100123",
            max_chars=11,
            key="incluir_mat_reativada_matricula"
        )
        
        nome_input = st.text_input(
            "Nome",
            placeholder="Ex: João da Silva",
            key="incluir_mat_reativada_nome"
        )
        
        ingresso_input = st.text_input(
            "Ingresso",
            placeholder="Ex: 2022/1",
            key="incluir_mat_reativada_ingresso"
        )
        
        if st.button("✅ Confirmar Inclusão", use_container_width=True, key="confirmar_incluir_mat_reativada"):
            é_válida, msg_erro = validar_matricula(matricula_input)
            if not é_válida:
                st.error(msg_erro)
            else:
                é_válido, msg_erro = validar_ingresso(ingresso_input)
                if not é_válido:
                    st.error(msg_erro)
                else:
                    if not nome_input or not nome_input.strip():
                        st.error("❌ Por favor, digite o nome do aluno")
                    else:
                        try:
                            df_mat_reativada = processador.ler_google_sheet('mat_reativada')
                            
                            if not df_mat_reativada.empty:
                                for _, row in df_mat_reativada.iterrows():
                                    if row['matrícula'].strip() == matricula_input:
                                        st.error("Esta matrícula já está na lista de alunos com matrícula reativada.")
                                        st.stop()
                            
                            processador.adicionar_aluno_matricula_reativada(
                                matricula_input,
                                nome_input.strip(),
                                ingresso_input,
                                True
                            )
                            st.success("✅ Aluno incluído com sucesso")
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erro ao incluir: {e}")
    
    with tab3:
        st.markdown("#### Excluir Alunos com Matrícula Reativada")
        
        try:
            df_mat_reativada = processador.ler_google_sheet('mat_reativada')
            
            if df_mat_reativada.empty:
                st.info("ℹ️ Não há alunos para excluir")
            else:
                # Resetar índice
                df_mat_reativada = df_mat_reativada.reset_index(drop=True)
                
                indices_selecionados = exibir_tabela_com_checkbox(
                    df_mat_reativada[['matrícula', 'nome', 'ingresso']],
                    "checkbox_mat_reativada_excluir"
                )
                
                if indices_selecionados:
                    st.markdown("---")
                    
                    # Guardar matrículas antes de excluir
                    matriculas_para_excluir = [df_mat_reativada.iloc[idx]['matrícula'] for idx in indices_selecionados]
                    nomes_para_excluir = [df_mat_reativada.iloc[idx]['nome'] for idx in indices_selecionados]
                    
                    st.markdown(f"**⚠️ {len(matriculas_para_excluir)} aluno(s) para exclusão:**")
                    
                    for matricula, nome in zip(matriculas_para_excluir, nomes_para_excluir):
                        st.write(f"• {matricula} - {nome}")
                    
                    if st.button("🗑️ Confirmar Exclusão", use_container_width=True, key="confirmar_excluir_mat_reativada"):
                        try:
                            excluidos = 0
                            erros = []
                            
                            # Usar matrículas guardadas (não índices)
                            for matricula in matriculas_para_excluir:
                                try:
                                    processador.remover_aluno_de_matricula_reativada(matricula)
                                    excluidos += 1
                                except Exception as e:
                                    erros.append(f"{matricula}: {str(e)}")
                            
                            if excluidos > 0:
                                st.success(f"✅ {excluidos} aluno(s) excluído(s)")
                            
                            if erros:
                                st.warning(f"⚠️ Erros: {', '.join(erros)}")
                            
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erro: {e}")
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {e}")
    
    with tab4:
        st.markdown("#### Editar Alunos com Matrícula Reativada")
        
        try:
            df_mat_reativada = processador.ler_google_sheet('mat_reativada')
            
            if df_mat_reativada.empty:
                st.info("ℹ️ Não há alunos para editar")
            else:
                df_mat_reativada = df_mat_reativada.reset_index(drop=True)
                
                opcoes_alunos = [f"{row['matrícula']} - {row['nome']}" 
                                for _, row in df_mat_reativada.iterrows()]
                
                indice_selecionado = st.selectbox(
                    "Selecione um aluno",
                    range(len(df_mat_reativada)),
                    format_func=lambda x: opcoes_alunos[x],
                    key="editar_mat_reativada_select"
                )
                
                aluno = df_mat_reativada.iloc[indice_selecionado]
                matricula_original = aluno['matrícula']
                
                st.markdown("---")
                
                with st.container():
                    matricula_key = f"editar_mat_reativada_matricula_{indice_selecionado}"
                    nome_key = f"editar_mat_reativada_nome_{indice_selecionado}"
                    ingresso_key = f"editar_mat_reativada_ingresso_{indice_selecionado}"
                    
                    matricula_edit = st.text_input(
                        "Matrícula",
                        value=aluno['matrícula'],
                        key=matricula_key
                    )
                    
                    nome_edit = st.text_input(
                        "Nome",
                        value=aluno['nome'],
                        key=nome_key
                    )
                    
                    ingresso_edit = st.text_input(
                        "Ingresso",
                        value=aluno['ingresso'],
                        key=ingresso_key
                    )
                
                if st.button("💾 Salvar Alterações", use_container_width=True, key="confirmar_editar_mat_reativada"):
                    é_válida, msg_erro = validar_matricula(matricula_edit)
                    if not é_válida:
                        st.error(msg_erro)
                    else:
                        é_válido, msg_erro = validar_ingresso(ingresso_edit)
                        if not é_válido:
                            st.error(msg_erro)
                        else:
                            if not nome_edit or not nome_edit.strip():
                                st.error("❌ Por favor, digite um nome válido")
                            else:
                                try:
                                    processador.atualizar_aluno_matricula_reativada(
                                        matricula_original,
                                        matricula_edit,
                                        nome_edit.strip(),
                                        ingresso_edit,
                                        True
                                    )
                                    st.success("✅ Aluno atualizado")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro: {e}")
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {e}")

# ============================================================================
# FUNCIONALIDADE 3: ALUNOS COM CONDIÇÕES ESPECIAIS
# ============================================================================

elif categoria_selecionada == "Alunos com condições especiais":
    st.markdown("### 🏥 Alunos com Condições Especiais")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Mostrar",
        "➕ Incluir",
        "🗑️ Excluir",
        "✏️ Editar"
    ])
    
    with tab1:
        st.markdown("#### Alunos com Condições Especiais")
        
        try:
            df_cond_especial = processador.ler_google_sheet('cond_especial')
            
            if df_cond_especial.empty:
                st.info("ℹ️ Não há alunos com condições especiais registradas")
            else:
                df_exibir = df_cond_especial[['matrícula', 'nome', 'ingresso']].copy()
                st.dataframe(df_exibir, use_container_width=True, hide_index=True)
                st.success(f"✅ Total: {len(df_cond_especial)}")
        
        except Exception as e:
            st.error(f"❌ Erro: {e}")
    
    with tab2:
        st.markdown("#### Incluir Aluno com Condição Especial")
        
        matricula_input = st.text_input(
            "Matrícula",
            placeholder="Ex: 20201100123",
            max_chars=11,
            key="incluir_cond_especial_matricula"
        )
        
        nome_input = st.text_input(
            "Nome",
            placeholder="Ex: João da Silva",
            key="incluir_cond_especial_nome"
        )
        
        ingresso_input = st.text_input(
            "Ingresso",
            placeholder="Ex: 2022/1",
            key="incluir_cond_especial_ingresso"
        )
        
        if st.button("✅ Confirmar Inclusão", use_container_width=True, key="confirmar_incluir_cond_especial"):
            é_válida, msg_erro = validar_matricula(matricula_input)
            if not é_válida:
                st.error(msg_erro)
            else:
                é_válido, msg_erro = validar_ingresso(ingresso_input)
                if not é_válido:
                    st.error(msg_erro)
                else:
                    if not nome_input or not nome_input.strip():
                        st.error("❌ Por favor, digite o nome do aluno")
                    else:
                        try:
                            df_cond_especial = processador.ler_google_sheet('cond_especial')
                            
                            if not df_cond_especial.empty:
                                for _, row in df_cond_especial.iterrows():
                                    if row['matrícula'].strip() == matricula_input:
                                        st.error("Esta matrícula já está na lista de alunos com condições especiais.")
                                        st.stop()
                            
                            processador.adicionar_aluno_com_condicao_especial(
                                matricula_input,
                                nome_input.strip(),
                                ingresso_input,
                                True
                            )
                            st.success("✅ Aluno incluído com sucesso")
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erro ao incluir: {e}")
    
    with tab3:
        st.markdown("#### Excluir Alunos com Condição Especial")
        
        try:
            df_cond_especial = processador.ler_google_sheet('cond_especial')
            
            if df_cond_especial.empty:
                st.info("ℹ️ Não há alunos para excluir")
            else:
                # Resetar índice
                df_cond_especial = df_cond_especial.reset_index(drop=True)
                
                indices_selecionados = exibir_tabela_com_checkbox(
                    df_cond_especial[['matrícula', 'nome', 'ingresso']],
                    "checkbox_cond_especial_excluir"
                )
                
                if indices_selecionados:
                    st.markdown("---")
                    
                    # Guardar matrículas antes de excluir
                    matriculas_para_excluir = [df_cond_especial.iloc[idx]['matrícula'] for idx in indices_selecionados]
                    nomes_para_excluir = [df_cond_especial.iloc[idx]['nome'] for idx in indices_selecionados]
                    
                    st.markdown(f"**⚠️ {len(matriculas_para_excluir)} aluno(s) para exclusão:**")
                    
                    for matricula, nome in zip(matriculas_para_excluir, nomes_para_excluir):
                        st.write(f"• {matricula} - {nome}")
                    
                    if st.button("🗑️ Confirmar Exclusão", use_container_width=True, key="confirmar_excluir_cond_especial"):
                        try:
                            excluidos = 0
                            erros = []
                            
                            # Usar matrículas guardadas (não índices)
                            for matricula in matriculas_para_excluir:
                                try:
                                    processador.remover_aluno_de_condicao_especial(matricula)
                                    excluidos += 1
                                except Exception as e:
                                    erros.append(f"{matricula}: {str(e)}")
                            
                            if excluidos > 0:
                                st.success(f"✅ {excluidos} aluno(s) excluído(s)")
                            
                            if erros:
                                st.warning(f"⚠️ Erros: {', '.join(erros)}")
                            
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erro ao carregar dados: {e}")
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {e}")
    
    with tab4:
        st.markdown("#### Editar Alunos com Condição Especial")
        
        try:
            df_cond_especial = processador.ler_google_sheet('cond_especial')
            
            if df_cond_especial.empty:
                st.info("ℹ️ Não há alunos para editar")
            else:
                df_cond_especial = df_cond_especial.reset_index(drop=True)
                
                opcoes_alunos = [f"{row['matrícula']} - {row['nome']}" 
                                for _, row in df_cond_especial.iterrows()]
                
                indice_selecionado = st.selectbox(
                    "Selecione um aluno",
                    range(len(df_cond_especial)),
                    format_func=lambda x: opcoes_alunos[x],
                    key="editar_cond_especial_select"
                )
                
                aluno = df_cond_especial.iloc[indice_selecionado]
                matricula_original = aluno['matrícula']
                
                st.markdown("---")
                
                with st.container():
                    matricula_key = f"editar_cond_especial_matricula_{indice_selecionado}"
                    nome_key = f"editar_cond_especial_nome_{indice_selecionado}"
                    ingresso_key = f"editar_cond_especial_ingresso_{indice_selecionado}"
                    
                    matricula_edit = st.text_input(
                        "Matrícula",
                        value=aluno['matrícula'],
                        key=matricula_key
                    )
                    
                    nome_edit = st.text_input(
                        "Nome",
                        value=aluno['nome'],
                        key=nome_key
                    )
                    
                    ingresso_edit = st.text_input(
                        "Ingresso",
                        value=aluno['ingresso'],
                        key=ingresso_key
                    )
                
                if st.button("💾 Salvar Alterações", use_container_width=True, key="confirmar_editar_cond_especial"):
                    é_válida, msg_erro = validar_matricula(matricula_edit)
                    if not é_válida:
                        st.error(msg_erro)
                    else:
                        é_válido, msg_erro = validar_ingresso(ingresso_edit)
                        if not é_válido:
                            st.error(msg_erro)
                        else:
                            if not nome_edit or not nome_edit.strip():
                                st.error("❌ Por favor, digite um nome válido")
                            else:
                                try:
                                    processador.atualizar_aluno_condicao_especial(
                                        matricula_original,
                                        matricula_edit,
                                        nome_edit.strip(),
                                        ingresso_edit,
                                        True
                                    )
                                    st.success("✅ Aluno atualizado")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro: {e}")
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {e}")

# ============================================================================
# FUNCIONALIDADE 4: ALUNOS QUE SE ENQUADRAM EM RODA
# ============================================================================

elif categoria_selecionada == "Alunos que se enquadram em RODA":
    st.markdown("### 📊 Alunos que se Enquadram em RODA")
    st.markdown("*Alunos que atendem aos critérios de RODA mas não estão ainda incluídos*")
    st.markdown("---")
    
    try:
        # Gerar relatório
        df_enquadram = processador.gerar_relatorio_alunos_enquadram_roda()
        
        if df_enquadram.empty:
            st.success("✅ Não há alunos que se enquadrem em RODA (ou todos já estão incluídos)")
        else:
            st.markdown(f"### 📋 Total de Alunos: {len(df_enquadram)}")
            
            # MUDANÇA: Exibir 7 colunas (as 3 originais + as 4 novas)
            colunas_exibir = ['matrícula', 'nome', 'ingresso', 
                             'reprovação último período', 'reprovações repetidas', 'ECH', 'EPL']
            
            # Verificar quais colunas existem no DataFrame
            colunas_existentes = [col for col in colunas_exibir if col in df_enquadram.columns]
            
            # Exibir tabela com as colunas disponíveis
            df_exibicao = df_enquadram[colunas_existentes].copy()
            st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
            
            # Opção de download
            st.markdown("---")
            st.markdown("### 📥 Exportar Relatório")
            
            csv = df_enquadram.to_csv(index=False, encoding='utf-8')
            
            st.download_button(
                label="📥 Baixar como CSV",
                data=csv,
                file_name="alunos_enquadram_roda.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    except Exception as e:
        st.error(f"❌ Erro ao gerar relatório: {e}")
        st.info("💡 Verifique se o arquivo RODA_alunos.xlsx existe na pasta bases/")

# ============================================================================
# RODAPÉ
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    Sistema de Informação Acadêmica | Gerenciamento de Alunos em RODA
</div>
""", unsafe_allow_html=True)