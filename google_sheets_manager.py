# ============================================================================
# google_sheets_manager.py
# ============================================================================
# Gerenciador de operações com Google Sheets
# Leitura, escrita, atualização e deleção de dados
import streamlit as st
import os
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from typing import List, Dict, Optional, Tuple

# ============================================================================
# CONFIGURAÇÃO DE AUTENTICAÇÃO
# ============================================================================

class GoogleSheetsManager:
    """
    Gerenciador de operações com Google Sheets
    Fornece métodos para CRUD (Create, Read, Update, Delete)
    """
    
        def __init__(self, credenciais_path: str = 'credenciais/google_sheets_creds.json'):
            """
            Inicializa o gerenciador com autenticação
        
            Args:
                credenciais_path: caminho do arquivo JSON de credenciais
        
            Raises:
                Exception: se o arquivo de credenciais não existir
            """
        try:
            
            
            
            # Verificar se está no Streamlit Cloud (possui secrets)
            if 'type' in st.secrets:
                # Usar secrets do Streamlit Cloud
                self.creds = Credentials.from_service_account_info(
                    dict(st.secrets),
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            else:
                # Usar arquivo local
                self.creds = Credentials.from_service_account_file(
                    credenciais_path,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            
            self.gc = gspread.authorize(self.creds)
        except Exception as e:
            raise Exception(f"Erro ao autenticar com Google Sheets: {e}")
    
    def abrir_planilha(self, sheet_id: str, sheet_name: str = "Sheet1") -> gspread.Worksheet:
        """
        Abre uma worksheet específica de uma Google Sheet
        
        Args:
            sheet_id: ID da Google Sheet
            sheet_name: nome da aba (default: Sheet1)
        
        Returns:
            gspread.Worksheet: worksheet aberta
        
        Raises:
            Exception: se não conseguir abrir a planilha
        """
        try:
            spreadsheet = self.gc.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            return worksheet
        except Exception as e:
            raise Exception(f"Erro ao abrir planilha {sheet_id}: {e}")
    
    def ler_dados(self, sheet_id: str, sheet_name: str = "Sheet1") -> pd.DataFrame:
        """
        Lê todos os dados de uma worksheet e retorna como DataFrame
        
        Args:
            sheet_id: ID da Google Sheet
            sheet_name: nome da aba
        
        Returns:
            pd.DataFrame: dados da planilha
        """
        try:
            worksheet = self.abrir_planilha(sheet_id, sheet_name)
            dados = worksheet.get_all_records()
            
            if not dados:
                # Retornar DataFrame vazio com colunas apropriadas
                return pd.DataFrame()
            
            df = pd.DataFrame(dados)
            
            # Converter coluna matrícula para string e normalizar
            if 'matrícula' in df.columns:
                df['matrícula'] = df['matrícula'].astype(str)
                df['matrícula'] = df['matrícula'].apply(self._normalizar_matricula)
            
            return df
        
        except Exception as e:
            raise Exception(f"Erro ao ler dados de {sheet_id}: {e}")
    
    def inserir_linha(self, sheet_id: str, dados: Dict, sheet_name: str = "Sheet1") -> bool:
        """
        Insere uma nova linha na worksheet
        
        Args:
            sheet_id: ID da Google Sheet
            dados: dicionário com os dados {coluna: valor}
            sheet_name: nome da aba
        
        Returns:
            bool: True se inserido com sucesso
        
        Raises:
            Exception: se houver erro na inserção
        """
        try:
            worksheet = self.abrir_planilha(sheet_id, sheet_name)
            
            # Obter cabeçalhos
            headers = worksheet.row_values(1)
            
            # Criar lista de valores na ordem dos headers
            valores = [str(dados.get(header, '')) for header in headers]
            
            # Inserir a linha
            worksheet.append_row(valores)
            
            return True
        
        except Exception as e:
            raise Exception(f"Erro ao inserir linha em {sheet_id}: {e}")
    
    def atualizar_linha(self, sheet_id: str, row_index: int, dados: Dict, sheet_name: str = "Sheet1") -> bool:
        """
        Atualiza uma linha existente na worksheet
        
        Args:
            sheet_id: ID da Google Sheet
            row_index: número da linha a atualizar (1-indexed)
            dados: dicionário com os dados {coluna: valor}
            sheet_name: nome da aba
        
        Returns:
            bool: True se atualizado com sucesso
        
        Raises:
            Exception: se houver erro na atualização
        """
        try:
            worksheet = self.abrir_planilha(sheet_id, sheet_name)
            
            # Obter cabeçalhos
            headers = worksheet.row_values(1)
            
            # Criar lista de valores na ordem dos headers
            valores = [str(dados.get(header, '')) for header in headers]
            
            # Atualizar a linha
            worksheet.update(f'A{row_index}:Z{row_index}', [valores])
            
            return True
        
        except Exception as e:
            raise Exception(f"Erro ao atualizar linha em {sheet_id}: {e}")
    
    def deletar_linha(self, sheet_id: str, row_index: int, sheet_name: str = "Sheet1") -> bool:
        """
        Deleta uma linha da worksheet
        
        Args:
            sheet_id: ID da Google Sheet
            row_index: número da linha a deletar (1-indexed)
            sheet_name: nome da aba
        
        Returns:
            bool: True se deletado com sucesso
        
        Raises:
            Exception: se houver erro na deleção
        """
        try:
            worksheet = self.abrir_planilha(sheet_id, sheet_name)
            worksheet.delete_rows(row_index)
            return True
        
        except Exception as e:
            raise Exception(f"Erro ao deletar linha em {sheet_id}: {e}")
    
    def encontrar_matricula(self, sheet_id: str, matricula: str, sheet_name: str = "Sheet1") -> Tuple[bool, Optional[int]]:
        """
        Procura uma matrícula na worksheet
        
        Args:
            sheet_id: ID da Google Sheet
            matricula: número da matrícula (11 dígitos)
            sheet_name: nome da aba
        
        Returns:
            tuple: (encontrada, número_da_linha)
                   encontrada: bool
                   número_da_linha: int (1-indexed, None se não encontrada)
        """
        try:
            df = self.ler_dados(sheet_id, sheet_name)
            
            if df.empty:
                return False, None
            
            # Procurar pela matrícula normalizada
            matricula_normalizada = self._normalizar_matricula(matricula)
            
            for idx, row in df.iterrows():
                if str(row.get('matrícula', '')).strip() == matricula_normalizada:
                    # idx é 0-indexed, mas linha do Google Sheets é 1-indexed
                    # +2 porque linha 1 é header
                    return True, idx + 2
            
            return False, None
        
        except Exception as e:
            raise Exception(f"Erro ao procurar matrícula: {e}")
    
    def obter_linha(self, sheet_id: str, row_index: int, sheet_name: str = "Sheet1") -> Optional[Dict]:
        """
        Obtém os dados de uma linha específica
        
        Args:
            sheet_id: ID da Google Sheet
            row_index: número da linha (1-indexed)
            sheet_name: nome da aba
        
        Returns:
            dict: dicionário com os dados da linha, ou None se não encontrada
        """
        try:
            worksheet = self.abrir_planilha(sheet_id, sheet_name)
            
            # Obter headers
            headers = worksheet.row_values(1)
            
            # Obter valores da linha
            valores = worksheet.row_values(row_index)
            
            # Preencher com valores vazios se necessário
            while len(valores) < len(headers):
                valores.append('')
            
            # Criar dicionário
            linha_dict = {headers[i]: valores[i] for i in range(len(headers))}
            
            return linha_dict
        
        except Exception as e:
            raise Exception(f"Erro ao obter linha {row_index}: {e}")
    
    def contar_linhas(self, sheet_id: str, sheet_name: str = "Sheet1") -> int:
        """
        Conta o número de linhas com dados (excluindo header)
        
        Args:
            sheet_id: ID da Google Sheet
            sheet_name: nome da aba
        
        Returns:
            int: número de linhas com dados
        """
        try:
            df = self.ler_dados(sheet_id, sheet_name)
            return len(df)
        
        except Exception as e:
            raise Exception(f"Erro ao contar linhas: {e}")
    
    def planilha_vazia(self, sheet_id: str, sheet_name: str = "Sheet1") -> bool:
        """
        Verifica se a planilha está vazia
        
        Args:
            sheet_id: ID da Google Sheet
            sheet_name: nome da aba
        
        Returns:
            bool: True se vazia, False caso contrário
        """
        return self.contar_linhas(sheet_id, sheet_name) == 0
    
    @staticmethod
    def _normalizar_matricula(matricula) -> str:
        """
        Normaliza a matrícula para string com 11 dígitos
        
        Args:
            matricula: matrícula (int ou str)
        
        Returns:
            str: matrícula normalizada
        """
        matricula_str = str(int(matricula))
        
        if len(matricula_str) == 9:
            return "00" + matricula_str
        
        return matricula_str


# ============================================================================
# ALIASES PARA FACILITAR USO
# ============================================================================

def criar_gerenciador(credenciais_path: str = 'credenciais/google_sheets_creds.json') -> GoogleSheetsManager:
    """
    Factory function para criar um gerenciador
    
    Args:
        credenciais_path: caminho do arquivo de credenciais
    
    Returns:
        GoogleSheetsManager: gerenciador inicializado
    """
    return GoogleSheetsManager(credenciais_path)