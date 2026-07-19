# ============================================================================
# processamento_roda.py (CORRIGIDO)
# ============================================================================
# Processamento e lógica para funcionalidades de RODA
# Integra Google Sheets com dados locais
# CORREÇÃO: Funções de atualização sem validação de matrícula

import pandas as pd
import os
from google_sheets_manager import GoogleSheetsManager
from processamento_cumprimento_grade import normalizar_matricula

# ============================================================================
# CONFIGURAÇÕES DE IDs DAS GOOGLE SHEETS
# ============================================================================

GOOGLE_SHEETS_IDS = {
    'eh_roda': '1xloUiNCASWOUh_QqkO6-z-HLUVLwUstX36UrvIedQ6M',
    'cond_especial': '1xS3dhoUivfzaNM39j_UCbVBTMXxEnunEwCrY10y7Dh4',
    'mat_reativada': '1twTEQ7tKAEUR7gmaAMbTyotj4gzyHhnlC6v7Wlj1jks'
}

SHEET_NAMES = {
    'eh_roda': 'Sheet1',
    'cond_especial': 'Sheet1',
    'mat_reativada': 'Sheet1'
}

# ============================================================================
# CLASSE PRINCIPAL: PROCESSADOR RODA
# ============================================================================

class ProcessadorRODA:
    """
    Processa dados de RODA e gerencia operações
    """
    
    def __init__(self):
        """Inicializa o processador"""
        try:
            self.manager = GoogleSheetsManager()
        except Exception as e:
            raise Exception(f"Erro ao inicializar gerenciador: {e}")
        
        self.pasta_raiz = os.path.dirname(os.path.abspath(__file__))
        self.pasta_bases = os.path.join(self.pasta_raiz, 'bases')
        self.arquivo_roda_alunos = os.path.join(self.pasta_bases, 'RODA_alunos.xlsx')
    
    # ========================================================================
    # MÉTODOS DE LEITURA
    # ========================================================================
    
    def carregar_roda_alunos(self) -> pd.DataFrame:
        """
        Carrega dados de RODA_alunos.xlsx
        
        Returns:
            pd.DataFrame: dados dos alunos em RODA
        
        Raises:
            Exception: se arquivo não existir
        """
        try:
            if not os.path.exists(self.arquivo_roda_alunos):
                raise FileNotFoundError(f"Arquivo não encontrado: {self.arquivo_roda_alunos}")
            
            df = pd.read_excel(self.arquivo_roda_alunos)
            
            # Normalizar matrículas
            if 'matrícula' in df.columns:
                df['matrícula'] = df['matrícula'].astype(str)
                df['matrícula'] = df['matrícula'].apply(normalizar_matricula)
            
            return df
        
        except Exception as e:
            raise Exception(f"Erro ao carregar RODA_alunos.xlsx: {e}")
    
    def ler_google_sheet(self, categoria: str) -> pd.DataFrame:
        """
        Lê dados de uma Google Sheet
        
        Args:
            categoria: 'eh_roda', 'cond_especial' ou 'mat_reativada'
        
        Returns:
            pd.DataFrame: dados da planilha
        
        Raises:
            Exception: se categoria inválida
        """
        if categoria not in GOOGLE_SHEETS_IDS:
            raise ValueError(f"Categoria inválida: {categoria}")
        
        try:
            sheet_id = GOOGLE_SHEETS_IDS[categoria]
            sheet_name = SHEET_NAMES.get(categoria, 'Sheet1')
            
            df = self.manager.ler_dados(sheet_id, sheet_name)
            
            # Normalizar matrículas se existirem
            if not df.empty and 'matrícula' in df.columns:
                df['matrícula'] = df['matrícula'].astype(str)
                df['matrícula'] = df['matrícula'].apply(normalizar_matricula)
            
            return df
        
        except Exception as e:
            raise Exception(f"Erro ao ler Google Sheet {categoria}: {e}")
    
    # ========================================================================
    # MÉTODOS DE VALIDAÇÃO E BUSCA
    # ========================================================================
    
    def matricula_existe_em_roda(self, matricula: str) -> bool:
        """
        Verifica se uma matrícula já está em RODA
        
        Args:
            matricula: número da matrícula (11 dígitos)
        
        Returns:
            bool: True se já está em RODA
        """
        try:
            df = self.ler_google_sheet('eh_roda')
            
            if df.empty:
                return False
            
            matricula_normalizada = normalizar_matricula(matricula)
            
            for idx, row in df.iterrows():
                if str(row.get('matrícula', '')).strip() == matricula_normalizada:
                    return True
            
            return False
        
        except Exception as e:
            raise Exception(f"Erro ao verificar matrícula em RODA: {e}")
    
    def encontrar_aluno_em_roda(self, matricula: str) -> tuple:
        """
        Encontra uma matrícula em RODA
        
        Args:
            matricula: número da matrícula
        
        Returns:
            tuple: (encontrada, row_index) onde row_index é para Google Sheets
        """
        try:
            sheet_id = GOOGLE_SHEETS_IDS['eh_roda']
            encontrada, row_index = self.manager.encontrar_matricula(sheet_id, matricula)
            return encontrada, row_index
        
        except Exception as e:
            raise Exception(f"Erro ao encontrar aluno: {e}")
    
    # ========================================================================
    # MÉTODOS DE INSERÇÃO
    # ========================================================================
    
    def adicionar_aluno_em_roda(self, matricula: str, nome: str, ingresso: str, roda: bool = True) -> bool:
        """
        Adiciona um aluno à planilha eh_RODA
        
        Args:
            matricula: número da matrícula
            nome: nome completo
            ingresso: período de ingresso
            roda: valor booleano (True/False)
        
        Returns:
            bool: True se adicionado com sucesso
        
        Raises:
            Exception: se houver erro
        """
        try:
            matricula_normalizada = normalizar_matricula(matricula)
            
            # Verificar se já existe
            if self.matricula_existe_em_roda(matricula_normalizada):
                raise ValueError("Aluno já está em RODA")
            
            dados = {
                'matrícula': matricula_normalizada,
                'nome': nome,
                'ingresso': ingresso,
                'RODA': str(roda)
            }
            
            sheet_id = GOOGLE_SHEETS_IDS['eh_roda']
            self.manager.inserir_linha(sheet_id, dados)
            
            return True
        
        except Exception as e:
            raise Exception(f"Erro ao adicionar aluno em RODA: {e}")
    
    def adicionar_aluno_com_condicao_especial(self, matricula: str, nome: str, ingresso: str, condicao_especial: bool = True) -> bool:
        """
        Adiciona um aluno à planilha cond_especial
        
        Args:
            matricula: número da matrícula
            nome: nome completo
            ingresso: período de ingresso
            condicao_especial: valor booleano
        
        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            matricula_normalizada = normalizar_matricula(matricula)
            
            dados = {
                'matrícula': matricula_normalizada,
                'nome': nome,
                'ingresso': ingresso,
                'condição especial': str(condicao_especial)
            }
            
            sheet_id = GOOGLE_SHEETS_IDS['cond_especial']
            self.manager.inserir_linha(sheet_id, dados)
            
            return True
        
        except Exception as e:
            raise Exception(f"Erro ao adicionar aluno com condição especial: {e}")
    
    def adicionar_aluno_matricula_reativada(self, matricula: str, nome: str, ingresso: str, reativada: bool = True) -> bool:
        """
        Adiciona um aluno à planilha mat_reativada
        
        Args:
            matricula: número da matrícula
            nome: nome completo
            ingresso: período de ingresso
            reativada: valor booleano
        
        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            matricula_normalizada = normalizar_matricula(matricula)
            
            dados = {
                'matrícula': matricula_normalizada,
                'nome': nome,
                'ingresso': ingresso,
                'matrícula reativada': str(reativada)
            }
            
            sheet_id = GOOGLE_SHEETS_IDS['mat_reativada']
            self.manager.inserir_linha(sheet_id, dados)
            
            return True
        
        except Exception as e:
            raise Exception(f"Erro ao adicionar aluno com matrícula reativada: {e}")
    
    # ========================================================================
    # MÉTODOS DE EXCLUSÃO
    # ========================================================================
    
    def remover_aluno_de_roda(self, matricula: str) -> bool:
        """
        Remove um aluno da planilha eh_RODA
        
        Args:
            matricula: número da matrícula
        
        Returns:
            bool: True se removido com sucesso
        """
        try:
            encontrada, row_index = self.encontrar_aluno_em_roda(matricula)
            
            if not encontrada:
                raise ValueError("Aluno não encontrado em RODA")
            
            sheet_id = GOOGLE_SHEETS_IDS['eh_roda']
            self.manager.deletar_linha(sheet_id, row_index)
            
            return True
        
        except Exception as e:
            raise Exception(f"Erro ao remover aluno de RODA: {e}")
    
    def remover_aluno_de_condicao_especial(self, matricula: str) -> bool:
        """
        Remove um aluno da planilha cond_especial
        
        Args:
            matricula: número da matrícula
        
        Returns:
            bool: True se removido com sucesso
        """
        try:
            sheet_id = GOOGLE_SHEETS_IDS['cond_especial']
            encontrada, row_index = self.manager.encontrar_matricula(sheet_id, matricula)
            
            if not encontrada:
                raise ValueError("Aluno não encontrado em condições especiais")
            
            self.manager.deletar_linha(sheet_id, row_index)
            
            return True
        
        except Exception as e:
            raise Exception(f"Erro ao remover aluno de condição especial: {e}")
    
    def remover_aluno_de_matricula_reativada(self, matricula: str) -> bool:
        """
        Remove um aluno da planilha mat_reativada
        
        Args:
            matricula: número da matrícula
        
        Returns:
            bool: True se removido com sucesso
        """
        try:
            sheet_id = GOOGLE_SHEETS_IDS['mat_reativada']
            encontrada, row_index = self.manager.encontrar_matricula(sheet_id, matricula)
            
            if not encontrada:
                raise ValueError("Aluno não encontrado em matrículas reativadas")
            
            self.manager.deletar_linha(sheet_id, row_index)
            
            return True
        
        except Exception as e:
            raise Exception(f"Erro ao remover aluno de matrícula reativada: {e}")
    
    # ========================================================================
    # MÉTODOS DE ATUALIZAÇÃO (CORRIGIDOS - SEM VALIDAÇÃO)
    # ========================================================================
    
    def atualizar_aluno_em_roda(self, matricula_antiga: str, matricula_nova: str, nome: str, ingresso: str, roda: bool) -> bool:
        """
        Atualiza dados de um aluno em eh_RODA
        
        IMPORTANTE: Não faz nenhuma validação. Confiar no operador para fornecer dados válidos.
        
        Args:
            matricula_antiga: matrícula original para localizar a linha
            matricula_nova: nova matrícula (pode ser igual à antiga)
            nome: nome completo
            ingresso: período de ingresso
            roda: valor booleano
        
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            sheet_id = GOOGLE_SHEETS_IDS['eh_roda']
            encontrada, row_index = self.manager.encontrar_matricula(sheet_id, matricula_antiga)
            
            if not encontrada:
                raise ValueError("Aluno não encontrado em RODA")
            
            # Normalizar matrícula nova
            matricula_nova_normalizada = normalizar_matricula(matricula_nova)
            
            dados = {
                'matrícula': matricula_nova_normalizada,
                'nome': nome,
                'ingresso': ingresso,
                'RODA': str(roda)
            }
            
            self.manager.atualizar_linha(sheet_id, row_index, dados)
            
            return True
        
        except Exception as e:
            raise Exception(f"Erro ao atualizar aluno em RODA: {e}")
    
    def atualizar_aluno_condicao_especial(self, matricula_antiga: str, matricula_nova: str, nome: str, ingresso: str, condicao_especial: bool) -> bool:
        """
        Atualiza dados de um aluno em cond_especial
        
        IMPORTANTE: Não faz nenhuma validação. Confiar no operador para fornecer dados válidos.
        
        Args:
            matricula_antiga: matrícula original para localizar a linha
            matricula_nova: nova matrícula (pode ser igual à antiga)
            nome: nome completo
            ingresso: período de ingresso
            condicao_especial: valor booleano
        
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            sheet_id = GOOGLE_SHEETS_IDS['cond_especial']
            encontrada, row_index = self.manager.encontrar_matricula(sheet_id, matricula_antiga)
            
            if not encontrada:
                raise ValueError("Aluno não encontrado em condições especiais")
            
            matricula_nova_normalizada = normalizar_matricula(matricula_nova)
            
            dados = {
                'matrícula': matricula_nova_normalizada,
                'nome': nome,
                'ingresso': ingresso,
                'condição especial': str(condicao_especial)
            }
            
            self.manager.atualizar_linha(sheet_id, row_index, dados)
            
            return True
        
        except Exception as e:
            raise Exception(f"Erro ao atualizar aluno em condição especial: {e}")
    
    def atualizar_aluno_matricula_reativada(self, matricula_antiga: str, matricula_nova: str, nome: str, ingresso: str, reativada: bool) -> bool:
        """
        Atualiza dados de um aluno em mat_reativada
        
        IMPORTANTE: Não faz nenhuma validação. Confiar no operador para fornecer dados válidos.
        
        Args:
            matricula_antiga: matrícula original para localizar a linha
            matricula_nova: nova matrícula (pode ser igual à antiga)
            nome: nome completo
            ingresso: período de ingresso
            reativada: valor booleano
        
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            sheet_id = GOOGLE_SHEETS_IDS['mat_reativada']
            encontrada, row_index = self.manager.encontrar_matricula(sheet_id, matricula_antiga)
            
            if not encontrada:
                raise ValueError("Aluno não encontrado em matrículas reativadas")
            
            matricula_nova_normalizada = normalizar_matricula(matricula_nova)
            
            dados = {
                'matrícula': matricula_nova_normalizada,
                'nome': nome,
                'ingresso': ingresso,
                'matrícula reativada': str(reativada)
            }
            
            self.manager.atualizar_linha(sheet_id, row_index, dados)
            
            return True
        
        except Exception as e:
            raise Exception(f"Erro ao atualizar aluno em matrícula reativada: {e}")
    
    # ========================================================================
    # MÉTODOS DE RELATÓRIO
    # ========================================================================
    
    def gerar_relatorio_alunos_enquadram_roda(self) -> pd.DataFrame:
        """
        Gera relatório de alunos que se enquadram em RODA
        Exclui aqueles que já estão em RODA
        
        Returns:
            pd.DataFrame: alunos que se enquadram mas não estão em RODA
        """
        try:
            # Carregar dados
            df_roda_alunos = self.carregar_roda_alunos()
            df_em_roda = self.ler_google_sheet('eh_roda')
            
            # Filtrar alunos que se enquadram mas NÃO estão em RODA
            if not df_em_roda.empty:
                # Extrair matrículas de quem já está em RODA
                matriculas_em_roda = set(df_em_roda['matrícula'].unique())
                
                # Filtrar
                df_resultado = df_roda_alunos[
                    ~df_roda_alunos['matrícula'].isin(matriculas_em_roda)
                ].copy()
            else:
                # Se nenhum está em RODA, usar todos
                df_resultado = df_roda_alunos.copy()
            
            # Manter colunas importantes
            colunas_manter = ['matrícula', 'nome', 'ingresso', 
                            'reprovação último período', 'reprovações repetidas', 'ECH', 'EPL']
            
            # Manter apenas colunas que existem
            colunas_manter = [col for col in colunas_manter if col in df_resultado.columns]
            
            return df_resultado[colunas_manter]
        
        except Exception as e:
            raise Exception(f"Erro ao gerar relatório: {e}")