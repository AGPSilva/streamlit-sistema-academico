# ============================================================================
# processamento_reprovacoes.py (VERSÃO FINAL)
# ============================================================================
# Funções para processar e formatar relatórios de alunos reprovados

import pandas as pd
import os

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


def ler_reprovados_uma_vez(caminho_arquivo):
    """
    Lê o arquivo de reprovados cursando a disciplina
    
    Args:
        caminho_arquivo: caminho do arquivo .xlsx
    
    Returns:
        pd.DataFrame: dados lidos e processados
    """
    # Ler o arquivo
    df = pd.read_excel(caminho_arquivo)
    
    # Normalizar matrículas
    df['matrícula'] = df['matrícula'].apply(normalizar_matricula)
    
    return df


def processar_reprovados_uma_vez(df):
    """
    Processa o DataFrame para gerar relatório de reprovações
    
    Agrupa alunos por matrícula e formata informações sobre reprovações
    
    Códigos de situação de reprovação suportados:
    - RPM: Reprovado por Média
    - RPF: Reprovado por Falta
    - RMF: Reprovado por Múltiplas Faltas
    
    Args:
        df: DataFrame com colunas: matrícula, nome, ingresso, sigla, disciplina, período, situação
    
    Returns:
        dict: dicionário com matrículas como chaves e lista de informações como valores
    """
    
    # Dicionário para armazenar dados agrupados por matrícula
    resultado = {}
    
    # Agrupar por matrícula
    for matricula, grupo in df.groupby('matrícula'):
        
        # Inicializar entrada para esta matrícula
        if matricula not in resultado:
            resultado[matricula] = {
                'nome': grupo['nome'].iloc[0],
                'ingresso': grupo['ingresso'].iloc[0],
                'reprovacoes': []
            }
        
        # Processar as duplas de linhas (reprovação + cursando)
        # Filtrar por todos os códigos de reprovação: RPM, RPF, RMF
        reprovacoes = grupo[grupo['situação'].isin(['RPM', 'RPF', 'RMF'])]
        
        for idx, linha_reprovacao in reprovacoes.iterrows():
            sigla_reprovacao = linha_reprovacao['sigla']
            disciplina_reprovacao = linha_reprovacao['disciplina']
            periodo_reprovacao = linha_reprovacao['período']
            
            # Encontrar a linha correspondente de cursando (CUR) da mesma disciplina
            cursando = grupo[
                (grupo['situação'] == 'CUR') & 
                (grupo['sigla'] == sigla_reprovacao)
            ]
            
            if not cursando.empty:
                linha_cursando = cursando.iloc[0]
                sigla_cursando = linha_cursando['sigla']
                disciplina_cursando = linha_cursando['disciplina']
                periodo_cursando = linha_cursando['período']
                
                # Armazenar informações da reprovação
                info_reprovacao = {
                    'sigla_reprovacao': sigla_reprovacao,
                    'disciplina_reprovacao': disciplina_reprovacao,
                    'periodo_reprovacao': periodo_reprovacao,
                    'sigla_cursando': sigla_cursando,
                    'disciplina_cursando': disciplina_cursando,
                    'periodo_cursando': periodo_cursando
                }
                
                resultado[matricula]['reprovacoes'].append(info_reprovacao)
    
    return resultado


def formatar_relatorio_reprovados_uma_vez(dados_processados):
    """
    Formata os dados processados em um texto legível
    
    Args:
        dados_processados: dicionário retornado por processar_reprovados_uma_vez()
    
    Returns:
        list: lista de strings formatadas para exibição
    """
    
    linhas_relatorio = []
    
    # Iterar por cada matrícula
    for matricula in sorted(dados_processados.keys()):
        aluno = dados_processados[matricula]
        nome = aluno['nome']
        ingresso = aluno['ingresso']
        
        # Cabeçalho do aluno
        linhas_relatorio.append(f"**{matricula}** – {nome} – ingresso em {ingresso}")
        
        # Listar reprovações
        for i, reprovacao in enumerate(aluno['reprovacoes'], 1):
            texto = (
                f"  Reprovado em {reprovacao['sigla_reprovacao']} – "
                f"{reprovacao['disciplina_reprovacao']} – "
                f"em {reprovacao['periodo_reprovacao']} e cursando "
                f"{reprovacao['sigla_cursando']} – "
                f"{reprovacao['disciplina_cursando']} – "
                f"em {reprovacao['periodo_cursando']}."
            )
            linhas_relatorio.append(texto)
        
        # Linha em branco após cada aluno
        linhas_relatorio.append("")
    
    return linhas_relatorio


def gerar_relatorio_reprovados_uma_vez(caminho_arquivo):
    """
    Função principal que orquestra todo o processo
    
    Args:
        caminho_arquivo: caminho do arquivo .xlsx
    
    Returns:
        tuple: (lista_formatada, dados_processados, dataframe_original)
    """
    
    # Ler dados
    df = ler_reprovados_uma_vez(caminho_arquivo)
    
    # Processar dados
    dados_processados = processar_reprovados_uma_vez(df)
    
    # Formatar relatório
    relatorio_formatado = formatar_relatorio_reprovados_uma_vez(dados_processados)
    
    return relatorio_formatado, dados_processados, df


# Função para processar reprovações em 2 disciplinas

def processar_reprovados_duas_vezes(df):
    """
    Processa o DataFrame para gerar relatório de alunos reprovados 2 vezes
    
    Agrupa alunos por matrícula e depois por disciplina.
    Para cada disciplina, espera 3 linhas: 2 reprovações + 1 cursando
    
    Códigos de situação de reprovação suportados:
    - RPM: Reprovado por Média
    - RPF: Reprovado por Falta
    - RMF: Reprovado por Múltiplas Faltas
    
    Args:
        df: DataFrame com colunas: matrícula, nome, ingresso, sigla, disciplina, período, situação
    
    Returns:
        dict: dicionário com matrículas como chaves e lista de informações como valores
    """
    
    # Dicionário para armazenar dados agrupados por matrícula
    resultado = {}
    
    # Agrupar por matrícula
    for matricula, grupo_aluno in df.groupby('matrícula'):
        
        # Inicializar entrada para esta matrícula
        if matricula not in resultado:
            resultado[matricula] = {
                'nome': grupo_aluno['nome'].iloc[0],
                'ingresso': grupo_aluno['ingresso'].iloc[0],
                'disciplinas': []
            }
        
        # Agrupar por disciplina (sigla) dentro de cada aluno
        for sigla, grupo_disciplina in grupo_aluno.groupby('sigla'):
            
            # Separar reprovações e cursando
            reprovacoes = grupo_disciplina[
                grupo_disciplina['situação'].isin(['RPM', 'RPF', 'RMF'])
            ].sort_values('período')
            
            cursando = grupo_disciplina[grupo_disciplina['situação'] == 'CUR']
            
            # Verificar se há exatamente 2 reprovações e 1 cursando
            if len(reprovacoes) >= 2 and len(cursando) > 0:
                
                # Pegar as duas primeiras reprovações
                rep1 = reprovacoes.iloc[0]
                rep2 = reprovacoes.iloc[1]
                cur = cursando.iloc[0]
                
                info_disciplina = {
                    'sigla': sigla,
                    'disciplina': rep1['disciplina'],
                    'periodo_reprovacao_1': rep1['período'],
                    'periodo_reprovacao_2': rep2['período'],
                    'periodo_cursando': cur['período']
                }
                
                resultado[matricula]['disciplinas'].append(info_disciplina)
    
    return resultado


def formatar_relatorio_reprovados_duas_vezes(dados_processados):
    """
    Formata os dados processados em um texto legível
    
    Args:
        dados_processados: dicionário retornado por processar_reprovados_duas_vezes()
    
    Returns:
        list: lista de strings formatadas para exibição
    """
    
    linhas_relatorio = []
    
    # Iterar por cada matrícula
    for matricula in sorted(dados_processados.keys()):
        aluno = dados_processados[matricula]
        nome = aluno['nome']
        ingresso = aluno['ingresso']
        
        # Cabeçalho do aluno
        linhas_relatorio.append(f"**{matricula}** – {nome} – ingresso em {ingresso}")
        
        # Listar disciplinas com 2 reprovações
        for disciplina in aluno['disciplinas']:
            texto = (
                f"  Reprovado em {disciplina['sigla']} – "
                f"{disciplina['disciplina']} – "
                f"em {disciplina['periodo_reprovacao_1']}; reprovado novamente em "
                f"{disciplina['sigla']} – {disciplina['disciplina']} – "
                f"em {disciplina['periodo_reprovacao_2']} e cursando "
                f"{disciplina['sigla']} – {disciplina['disciplina']} – "
                f"em {disciplina['periodo_cursando']}."
            )
            linhas_relatorio.append(texto)
        
        # Linha em branco após cada aluno
        linhas_relatorio.append("")
    
    return linhas_relatorio


def gerar_relatorio_reprovados_duas_vezes(caminho_arquivo):
    """
    Função principal que orquestra todo o processo para reprovações em 2 disciplinas
    
    Args:
        caminho_arquivo: caminho do arquivo .xlsx
    
    Returns:
        tuple: (lista_formatada, dados_processados, dataframe_original)
    """
    
    # Ler dados
    df = ler_reprovados_uma_vez(caminho_arquivo)  # Usa a mesma função de leitura
    
    # Processar dados
    dados_processados = processar_reprovados_duas_vezes(df)
    
    # Formatar relatório
    relatorio_formatado = formatar_relatorio_reprovados_duas_vezes(dados_processados)
    
    return relatorio_formatado, dados_processados, df


# Função para processar múltiplas reprovações na mesma disciplina sem cursá-la

def processar_reprovacoes_multiplas_sem_cursar(df):
    """
    Processa o DataFrame para gerar relatório de alunos com múltiplas reprovações
    na mesma disciplina ou equivalentes, sem aprovação posterior e sem estar cursando
    
    Agrupa alunos por matrícula e depois por disciplina.
    Para cada disciplina, processa todas as reprovações (2 ou mais)
    
    Códigos de situação de reprovação suportados:
    - RPM: Reprovado por Média
    - RPF: Reprovado por Falta
    - RMF: Reprovado por Múltiplas Faltas
    
    Args:
        df: DataFrame com colunas: matrícula, nome, ingresso, sigla, disciplina, período, situação
    
    Returns:
        dict: dicionário com matrículas como chaves e lista de informações como valores
    """
    
    # Dicionário para armazenar dados agrupados por matrícula
    resultado = {}
    
    # Agrupar por matrícula
    for matricula, grupo_aluno in df.groupby('matrícula'):
        
        # Inicializar entrada para esta matrícula
        if matricula not in resultado:
            resultado[matricula] = {
                'nome': grupo_aluno['nome'].iloc[0],
                'ingresso': grupo_aluno['ingresso'].iloc[0],
                'disciplinas': []
            }
        
        # Agrupar por disciplina (sigla) dentro de cada aluno
        for sigla, grupo_disciplina in grupo_aluno.groupby('sigla'):
            
            # Filtrar apenas reprovações (RPM, RPF, RMF)
            reprovacoes = grupo_disciplina[
                grupo_disciplina['situação'].isin(['RPM', 'RPF', 'RMF'])
            ].sort_values('período')
            
            # Verificar se há pelo menos 2 reprovações
            if len(reprovacoes) >= 2:
                
                # Extrair períodos e criar lista de reprovações
                periodos = reprovacoes['período'].tolist()
                
                info_disciplina = {
                    'sigla': sigla,
                    'disciplina': reprovacoes.iloc[0]['disciplina'],
                    'periodos': periodos
                }
                
                resultado[matricula]['disciplinas'].append(info_disciplina)
    
    return resultado


def formatar_relatorio_reprovacoes_multiplas_sem_cursar(dados_processados):
    """
    Formata os dados processados em um texto legível
    
    Formato esperado:
    - Se 2 reprovações: "Reprovado em {sigla} – {disciplina} – em {período}; reprovado novamente em {sigla} – {disciplina} – em {período}."
    - Se 3+ reprovações: "Reprovado em {sigla} – {disciplina} – em {período}; reprovado novamente em {sigla} – {disciplina} – em {período}; reprovado novamente em {sigla} – {disciplina} – em {período}."
    
    Args:
        dados_processados: dicionário retornado por processar_reprovacoes_multiplas_sem_cursar()
    
    Returns:
        list: lista de strings formatadas para exibição
    """
    
    linhas_relatorio = []
    
    # Iterar por cada matrícula
    for matricula in sorted(dados_processados.keys()):
        aluno = dados_processados[matricula]
        nome = aluno['nome']
        ingresso = aluno['ingresso']
        
        # Cabeçalho do aluno
        linhas_relatorio.append(f"**{matricula}** – {nome} – ingresso em {ingresso}")
        
        # Listar disciplinas com múltiplas reprovações
        for disciplina in aluno['disciplinas']:
            sigla = disciplina['sigla']
            nome_disciplina = disciplina['disciplina']
            periodos = disciplina['periodos']
            
            # Construir texto de reprovações
            if len(periodos) == 2:
                # Caso com 2 reprovações
                texto = (
                    f"  Reprovado em {sigla} – {nome_disciplina} – "
                    f"em {periodos[0]}; reprovado novamente em {sigla} – "
                    f"{nome_disciplina} – em {periodos[1]}."
                )
            else:
                # Caso com 3 ou mais reprovações
                # Primeira reprovação
                texto = f"  Reprovado em {sigla} – {nome_disciplina} – em {periodos[0]}"
                
                # Reprovações intermediárias (2 a n-1)
                for i in range(1, len(periodos) - 1):
                    texto += f"; reprovado novamente em {sigla} – {nome_disciplina} – em {periodos[i]}"
                
                # Última reprovação
                texto += f"; reprovado novamente em {sigla} – {nome_disciplina} – em {periodos[-1]}."
            
            linhas_relatorio.append(texto)
        
        # Linha em branco após cada aluno
        linhas_relatorio.append("")
    
    return linhas_relatorio


def gerar_relatorio_reprovacoes_multiplas_sem_cursar(caminho_arquivo):
    """
    Função principal que orquestra todo o processo para múltiplas reprovações
    
    Args:
        caminho_arquivo: caminho do arquivo .xlsx
    
    Returns:
        tuple: (lista_formatada, dados_processados, dataframe_original)
    """
    
    # Ler dados
    df = ler_reprovados_uma_vez(caminho_arquivo)  # Usa a mesma função de leitura
    
    # Processar dados
    dados_processados = processar_reprovacoes_multiplas_sem_cursar(df)
    
    # Formatar relatório
    relatorio_formatado = formatar_relatorio_reprovacoes_multiplas_sem_cursar(dados_processados)
    
    return relatorio_formatado, dados_processados, df