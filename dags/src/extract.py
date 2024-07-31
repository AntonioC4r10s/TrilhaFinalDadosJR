import os
import requests
import pandas as pd
import sqlite3

def download_file_from_github(repo_owner, repo_name, folder_path, file_name, save_dir):
    """
    Faz o download de um arquivo específico do repositório GitHub.

    Args:
        repo_owner (str): Nome do proprietário do repositório.
        repo_name (str): Nome do repositório.
        folder_path (str): Caminho da pasta dentro do repositório.
        file_name (str): Nome do arquivo a ser baixado.
        save_dir (str): Diretório local onde o arquivo será salvo.
    """
    # Monta a URL para o arquivo específico
    url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{folder_path}/{file_name}"
    response = requests.get(url)

    if response.status_code == 200:
        file_path = os.path.join(save_dir, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)  # Salva o conteúdo do arquivo
        print(f"Downloaded: {file_name}")
    else:
        print(f"Failed to download {file_name}. Status code: {response.status_code}")

def download_files_from_github(repo_owner, repo_name, folder_path, save_dir):
    """
    Faz o download de todos os arquivos CSV de uma pasta específica do repositório GitHub.

    Args:
        repo_owner (str): Nome do proprietário do repositório.
        repo_name (str): Nome do repositório.
        folder_path (str): Caminho da pasta dentro do repositório.
        save_dir (str): Diretório local onde os arquivos serão salvos.
    """
    # Monta a URL para acessar os conteúdos da pasta
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}"
    response = requests.get(url)

    if response.status_code == 200:
        files = response.json()
        # Faz o download de cada arquivo CSV
        for file in files:
            if file['type'] == 'file' and file['name'].endswith('.csv'):
                download_file_from_github(repo_owner, repo_name, folder_path, file['name'], save_dir)
    else:
        print(f"Failed to retrieve file list. Status code: {response.status_code}")

def update_sqlite_with_new_records(save_dir, sqlite_db):
    """
    Atualiza o banco de dados SQLite com novos registros a partir dos arquivos CSV.

    Args:
        save_dir (str): Diretório onde os arquivos CSV estão salvos.
        sqlite_db (str): Caminho do banco de dados SQLite.
    """
    conn = sqlite3.connect(sqlite_db)  # Conecta ao banco de dados SQLite

    # Itera sobre os arquivos CSV no diretório
    for file_name in os.listdir(save_dir):
        if file_name.endswith('.csv'):
            file_path = os.path.join(save_dir, file_name)
            new_df = pd.read_csv(file_path)  # Lê o arquivo CSV em um DataFrame
            table_name = os.path.splitext(file_name)[0]  # Nome da tabela sem a extensão do arquivo
            
            # Verifica se a tabela existe
            query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
            table_exists = conn.execute(query).fetchone()
            
            if table_exists:
                # Carrega registros existentes
                existing_df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                
                # Encontrar novos registros
                new_records = new_df[~new_df.isin(existing_df.to_dict(orient='list')).all(axis=1)]
                
                if not new_records.empty:
                    new_records.to_sql(table_name, conn, if_exists='append', index=False)  # Adiciona novos registros
                    print(f"Appended new records to table {table_name} in SQLite")
                else:
                    print(f"No new records to append for {file_name}")
            else:
                # Se a tabela não existe, cria e insere todos os registros
                new_df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"Created table {table_name} and inserted all records in SQLite")

    conn.close()  # Fecha a conexão com o banco de dados

# Configurações
REPO_OWNER = '68vinicius'  # Nome do proprietário do repositório
REPO_NAME = 'TrilhaFinalDadosJR'  # Nome do repositório
FOLDER_PATH = 'Data'  # Caminho da pasta dentro do repositório
SAVE_DIR = 'dags/src/data'  # Diretório local onde os arquivos serão salvos
SQLITE_DB = 'dags/src/data/data.db'  # Caminho do banco de dados SQLite

def extract():
    """
    Função principal para executar a extração de dados do GitHub e atualização do banco de dados SQLite.
    """
    # Certifique-se de que o diretório de salvamento existe
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Baixar arquivos da pasta específica no GitHub
    download_files_from_github(REPO_OWNER, REPO_NAME, FOLDER_PATH, SAVE_DIR)

    # Atualizar o banco de dados SQLite com novos registros
    update_sqlite_with_new_records(SAVE_DIR, SQLITE_DB)

    print("Todos os arquivos foram baixados e o banco de dados SQLite foi atualizado com novos registros.")
