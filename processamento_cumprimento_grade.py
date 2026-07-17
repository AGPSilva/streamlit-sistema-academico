# ============================================================================
# processamento_cumprimento_grade.py (VERSÃO ATUALIZADA)
# ============================================================================
# Funções para processar e gerar relatório de cumprimento da grade curricular

import pandas as pd
import numpy as np
import os
import json

def normalizar_matricula(matricula):
    """
    Converte matrícula para string e adiciona '00' no início se tiver 9 dígitos
    
    Args:
        matricula: valor da matrícula (int ou str)
    
    Returns:
        str: matrícula normalizada com 11 dígitos
    """
    matricula_str = str(int(matricula))
    
    if len(matricula_str) == 9:
        return "00" + matricula_str
    
    return matricula_str


def validar_matricula(matricula_input):
    """
    Valida a matrícula inserida pelo usuário
    
    Verificações:
    - Comprimento deve ser 11 caracteres
    - Deve conter apenas dígitos
    
    Args:
        matricula_input: string da matrícula digitada
    
    Returns:
        tuple: (é_válida, mensagem_erro)
    """
    
    # Verificar comprimento
    if len(matricula_input) != 11:
        return False, f"❌ Matrícula inválida. Comprimento deve ser 11 caracteres (recebido: {len(matricula_input)})"
    
    # Verificar se são apenas dígitos
    if not matricula_input.isdigit():
        return False, "❌ Matrícula inválida. Deve conter apenas números"
    
    return True, ""


def matricula_existe_na_base(matricula, caminho_arquivo):
    """
    Verifica se a matrícula existe na base de dados de alunos ativos
    
    Args:
        matricula: string da matrícula (11 caracteres)
        caminho_arquivo: caminho do arquivo Excel com alunos ativos
    
    Returns:
        tuple: (existe, dados_aluno) onde dados_aluno é None se não existe
    """
    
    try:
        # Ler o arquivo
        df = pd.read_excel(caminho_arquivo)
        
        # Normalizar matrículas do arquivo
        df['Matrícula'] = df['Matrícula'].astype(str)
        df['Matrícula'] = df['Matrícula'].apply(normalizar_matricula)
        
        # Buscar a matrícula
        linha = df[df['Matrícula'] == matricula]
        
        if linha.empty:
            return False, None
        
        # Extrair dados do aluno
        dados_aluno = {
            'nome': linha['Nome'].values[0],
            'ingresso': linha['Ingresso'].values[0],
            'cota': linha['Cota'].values[0] if 'Cota' in df.columns else 'N/A'
        }
        
        return True, dados_aluno
    
    except Exception as e:
        return False, None


def determinar_grade(ingresso):
    """
    Determina qual grade o aluno segue baseado no ano de ingresso
    
    Args:
        ingresso: string com formato "YYYY/S" (ex: "2020/1")
    
    Returns:
        str: "grade_old" ou "grade_new"
    """
    
    try:
        ano_ingresso = int(ingresso.split('/')[0])
        
        if ano_ingresso < 2023:
            return "grade_old"
        else:
            return "grade_new"
    
    except:
        return "grade_new"  # Default


def carregar_grades(caminho_grade_old, caminho_grade_new):
    """
    Carrega as grades teóricas (antiga e nova) e cria dicionários estruturados
    
    Args:
        caminho_grade_old: caminho do arquivo grade_old.xlsx
        caminho_grade_new: caminho do arquivo grade_new.xlsx
    
    Returns:
        tuple: (grade_old_dic, grade_new_dic)
    """
    
    # Carregar dataframes
    g_old_df = pd.read_excel(caminho_grade_old)
    g_new_df = pd.read_excel(caminho_grade_new)
    
    # Converter periodo em inteiros
    g_old_df['periodo'] = g_old_df['periodo'].astype('Int64')
    g_new_df['periodo'] = g_new_df['periodo'].astype('Int64')
    
    # Criar dicionários vazios
    chaves = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'optativas', 'eletivas']
    grade_old_dic = {chave: [] for chave in chaves}
    grade_new_dic = {chave: [] for chave in chaves}
    
    # Preencher grade antiga
    for periodo in range(1, 11):
        linhas_periodo = g_old_df[g_old_df['periodo'] == periodo]
        
        for idx, row in linhas_periodo.iterrows():
            # Estrutura: [sigla, disciplina, equivalências, período_cursada, foi_cursada]
            lista = [
                row['sigla'],
                row['disciplina'],
                row['disc_equiv'],
                np.nan,
                False
            ]
            grade_old_dic[periodo].append(lista)
    
    # Preencher grade nova
    for periodo in range(1, 11):
        linhas_periodo = g_new_df[g_new_df['periodo'] == periodo]
        
        for idx, row in linhas_periodo.iterrows():
            lista = [
                row['sigla'],
                row['disciplina'],
                row['disc_equiv'],
                np.nan,
                False
            ]
            grade_new_dic[periodo].append(lista)
    
    return grade_old_dic, grade_new_dic


def carregar_rendimento_aluno(matricula, caminho_arquivo):
    """
    Carrega o histórico acadêmico do aluno
    
    Args:
        matricula: string da matrícula (11 caracteres)
        caminho_arquivo: caminho do arquivo de rendimento
    
    Returns:
        pd.DataFrame: histórico do aluno
    """
    
    # Ler o arquivo
    df = pd.read_excel(caminho_arquivo)
    
    # Normalizar matrículas
    df['matrícula'] = df['matrícula'].astype(str)
    df['matrícula'] = df['matrícula'].apply(normalizar_matricula)
    
    # Filtrar pela matrícula
    aluno_df = df[df['matrícula'] == matricula]
    
    return aluno_df


def processar_cumprimento_grade(matricula, grade_dic, rendimento_df):
    """
    Processa o cumprimento da grade comparando o que foi cursado com a grade teórica
    
    Args:
        matricula: string da matrícula
        grade_dic: dicionário com a grade teórica
        rendimento_df: DataFrame com o histórico do aluno
    
    Returns:
        dict: dicionário com a grade atualizada
    """
    
    # Filtrar apenas disciplinas aprovadas
    # Situações aceitas: APR (aprovado), ISE (dispensado), DISP (dispensado), AARE (aprovado AARE)
    rend_aluno_apr_df = rendimento_df[
        rendimento_df['situação'].isin(['APR', 'ISE', 'DISP', 'AARE'])
    ]
    
    # Comparar disciplinas obrigatórias (períodos 1-10)
    for periodo in range(1, 11):
        for idx_lista, lista in enumerate(grade_dic[periodo]):
            # Ler equivalências (índice 2)
            equivs = lista[2]
            
            encontrou = False
            
            # Procurar nos disciplinas cursadas
            for idx_df, row in rend_aluno_apr_df.iterrows():
                sigla_df = row['sigla']
                
                # Verificar se a sigla está nas equivalências
                if sigla_df in str(equivs).split(' - '):
                    # Encontrou! Atualizar a lista
                    grade_dic[periodo][idx_lista][0] = row['sigla']
                    grade_dic[periodo][idx_lista][1] = row['disciplina']
                    grade_dic[periodo][idx_lista][3] = str(row['período']).strip()
                    grade_dic[periodo][idx_lista][4] = True
                    
                    encontrou = True
                    break
    
    # Processar disciplinas optativas
    if (rend_aluno_apr_df['status'] == 'opt').any():
        for idx, row in rend_aluno_apr_df.iterrows():
            if row['status'] == 'opt':
                optat = [row['sigla'], row['disciplina'], row['período']]
                grade_dic['optativas'].append(optat)
    
    # Processar disciplinas eletivas
    if (rend_aluno_apr_df['status'] == 'elt').any():
        for idx, row in rend_aluno_apr_df.iterrows():
            if row['status'] == 'elt':
                eletiva = [row['sigla'], row['disciplina'], row['período']]
                grade_dic['eletivas'].append(eletiva)
    
    return grade_dic


def gerar_dataframes_cumprimento_grade(matricula, nome, ingresso, grade_dic):
    """
    Gera DataFrames estruturados para exibição em tabelas Streamlit
    
    Args:
        matricula: string da matrícula
        nome: string com o nome do aluno
        ingresso: string com período de ingresso
        grade_dic: dicionário com a grade processada
    
    Returns:
        dict: dicionário com DataFrames para cada seção
    """
    
    dfs = {}
    
    # Criar DataFrames para cada período das disciplinas obrigatórias
    for periodo in range(1, 11):
        dados = []
        marcadores_cursada = []  # Para estilização
        
        for lista in grade_dic[periodo]:
            sigla = lista[0]
            disciplina = lista[1]
            periodo_cursada = lista[3]
            cursada = lista[4]
            
            # Tratar valor NaN
            if pd.isna(periodo_cursada):
                periodo_cursada = "-"
            
            dados.append({
                'Sigla': sigla,
                'Disciplina': disciplina,
                'Período': periodo_cursada
            })
            
            marcadores_cursada.append(cursada)
        
        if dados:
            df_periodo = pd.DataFrame(dados)
            dfs[f'periodo_{periodo}'] = {
                'df': df_periodo,
                'cursadas': marcadores_cursada
            }
    
    # DataFrame para disciplinas optativas
    if grade_dic['optativas']:
        dados_opt = []
        for lista in grade_dic['optativas']:
            dados_opt.append({
                'Sigla': lista[0],
                'Disciplina': lista[1],
                'Período': lista[2]
            })
        
        dfs['optativas'] = {
            'df': pd.DataFrame(dados_opt),
            'cursadas': [True] * len(dados_opt)  # Todas as optativas foram cursadas
        }
    else:
        dfs['optativas'] = {
            'df': pd.DataFrame(columns=['Sigla', 'Disciplina', 'Período']),
            'cursadas': []
        }
    
    # DataFrame para disciplinas eletivas
    if grade_dic['eletivas']:
        dados_ele = []
        for lista in grade_dic['eletivas']:
            dados_ele.append({
                'Sigla': lista[0],
                'Disciplina': lista[1],
                'Período': lista[2]
            })
        
        dfs['eletivas'] = {
            'df': pd.DataFrame(dados_ele),
            'cursadas': [True] * len(dados_ele)  # Todas as eletivas foram cursadas
        }
    else:
        dfs['eletivas'] = {
            'df': pd.DataFrame(columns=['Sigla', 'Disciplina', 'Período']),
            'cursadas': []
        }
    
    # Adicionar informações do aluno
    dfs['info_aluno'] = {
        'matricula': matricula,
        'nome': nome,
        'ingresso': ingresso
    }
    
    return dfs


def gerar_relatorio_cumprimento_grade(matricula, caminhos):
    """
    Função principal que orquestra todo o processo
    
    Args:
        matricula: string da matrícula (11 caracteres)
        caminhos: dicionário com os caminhos dos arquivos necessários
                  {
                      'alunos_ativos': caminho,
                      'rendimento': caminho,
                      'grade_old': caminho,
                      'grade_new': caminho
                  }
    
    Returns:
        tuple: (dfs_estruturados, dados_aluno)
    
    Raises:
        Exception: se algum arquivo não for encontrado
    """
    
    # Verificar se a matrícula existe na base
    existe, dados_aluno = matricula_existe_na_base(matricula, caminhos['alunos_ativos'])
    
    if not existe:
        raise Exception("Matrícula não encontrada na base de dados de alunos ativos")
    
    # Determinar qual grade usar
    grade_tipo = determinar_grade(dados_aluno['ingresso'])
    
    # Carregar as grades
    grade_old_dic, grade_new_dic = carregar_grades(
        caminhos['grade_old'],
        caminhos['grade_new']
    )
    
    # Selecionar a grade apropriada
    grade_selecionada = grade_old_dic if grade_tipo == "grade_old" else grade_new_dic
    
    # Carregar rendimento do aluno
    rendimento_aluno = carregar_rendimento_aluno(matricula, caminhos['rendimento'])
    
    # Processar o cumprimento
    grade_processada = processar_cumprimento_grade(matricula, grade_selecionada, rendimento_aluno)
    
    # Gerar DataFrames estruturados
    dfs = gerar_dataframes_cumprimento_grade(
        matricula,
        dados_aluno['nome'],
        dados_aluno['ingresso'],
        grade_processada
    )
    
    return dfs, dados_aluno