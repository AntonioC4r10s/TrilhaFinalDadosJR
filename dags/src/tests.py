import sqlite3
import pandas as pd

def read_table_from_sqlite(sqlite_db, table_name):
    """
    Lê uma tabela do banco de dados SQLite e retorna um DataFrame do pandas.

    Args:
    sqlite_db (str): Caminho do banco de dados SQLite.
    table_name (str): Nome da tabela a ser lida.

    Returns:
    pd.DataFrame: DataFrame contendo os dados da tabela.
    """
    conn = sqlite3.connect(sqlite_db)
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def list_tables_in_sqlite(sqlite_db):
    """
    Lista todas as tabelas no banco de dados SQLite.

    Args:
    sqlite_db (str): Caminho do banco de dados SQLite.

    Returns:
    list: Lista contendo os nomes das tabelas.
    """
    conn = sqlite3.connect(sqlite_db)
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql(query, conn)
    conn.close()
    return tables['name'].tolist()

# Configuração do caminho do banco de dados SQLite
sqlite_db = 'dags/src/data/data.db'

# Listar todas as tabelas no banco de dados SQLite
tables = list_tables_in_sqlite(sqlite_db)
print("Tabelas no banco de dados SQLite:", tables)

# Ler dados de uma tabela específica
if tables:
    table_name = tables[0]  # Exemplo: ler a primeira tabela
    df = read_table_from_sqlite(sqlite_db, table_name)
    print(f"Dados da tabela {table_name}:")
    print(df.head())
else:
    print("Nenhuma tabela encontrada no banco de dados SQLite.")
