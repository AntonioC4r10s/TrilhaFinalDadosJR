import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
# from transform import transform

def load_to_google_sheets(df, spreadsheet_id, range_name):
    """
    Carrega os dados do DataFrame para uma planilha do Google Sheets.
    
    Args:
        df (pd.DataFrame): DataFrame com os dados a serem carregados.
        spreadsheet_id (str): ID da planilha do Google Sheets.
        range_name (str): Nome do intervalo onde os dados serão escritos (ex: 'Sheet1!A1').
    """
    # Configura as credenciais para acessar a API do Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('dags/src/credentials/credentials.json', scope)
    client = gspread.authorize(creds)  # Autoriza o cliente gspread com as credenciais

    # Abre a planilha usando o ID fornecido e seleciona a primeira aba
    sheet = client.open_by_key(spreadsheet_id).sheet1  
    
    # Limpa a aba antes de carregar novos dados para evitar sobreposição
    sheet.clear()
    
    # Carrega os dados do DataFrame na planilha
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("Dados carregados com sucesso na planilha do Google Sheets.")

def load(df):
    """
    Função para carregar dados do DataFrame na planilha do Google Sheets.
    
    Args:
        df (pd.DataFrame): DataFrame com os dados a serem carregados.
    """
    # ID da planilha do Google Sheets
    SPREADSHEET_ID = '1PsGzXlkodOKpFEFm0O7kREv3wGP4pEU8q63LMCgjMI8'
    
    # Nome da aba e intervalo para carregar os dados
    RANGE_NAME = 'Sheet1!A1'  # O intervalo onde os dados começarão a ser inseridos
    
    # Carregar dados para o Google Sheets
    load_to_google_sheets(df, SPREADSHEET_ID, RANGE_NAME)
