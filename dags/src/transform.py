import pandas as pd
import sqlite3

def format_column_name(column_name):
    """
    Formata o nome da coluna, trocando '_' por ' ' e capitalizando palavras com 3 ou mais letras.
    
    Args:
        column_name (str): Nome da coluna a ser formatado.
    
    Returns:
        str: Nome da coluna formatado.
    """
    # Troca '_' por ' ' no nome da coluna
    formatted_name = column_name.replace('_', ' ')
    # Capitaliza palavras com 3 ou mais letras
    formatted_name = ' '.join(word.capitalize() if len(word) >= 3 else word for word in formatted_name.split())
    return formatted_name

def format_string_value(value):
    """
    Formata um valor de string, trocando '_' por ' ' e capitalizando palavras com 3 ou mais letras.
    
    Args:
        value (str): Valor a ser formatado.
    
    Returns:
        str: Valor formatado.
    """
    if isinstance(value, str):
        # Troca '_' por ' ' e capitaliza palavras com 3 ou mais letras
        formatted_value = value.replace('_', ' ')
        formatted_value = ' '.join(word.capitalize() if len(word) >= 3 else word for word in formatted_value.split())
        return formatted_value
    return value

def read_tables_from_db(sqlite_db):
    """
    Lê todas as tabelas do banco de dados SQLite e retorna um único DataFrame com todos os dados.
    
    Args:
        sqlite_db (str): Caminho do banco de dados SQLite.
    
    Returns:
        pd.DataFrame: Um DataFrame contendo todos os dados de todas as tabelas.
    """
    # Conecta ao banco de dados SQLite
    conn = sqlite3.connect(sqlite_db)
    # Obtém a lista de tabelas no banco de dados
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    
    all_data = []  # Lista para armazenar todos os DataFrames
    
    # Itera sobre cada tabela e lê os dados
    for table_name in tables:
        table_name = table_name[0]  # Extrai o nome da tabela da tupla
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        
        # Formata os nomes das colunas
        df.columns = [format_column_name(col) for col in df.columns]
        
        # Formata a coluna 'Data' para datetime e 'Horas semanais dedicadas' para int
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')  # Converte para datetime, trata erros
            # Converte a coluna 'Data' para string no formato desejado
            df['Data'] = df['Data'].dt.strftime('%Y-%m-%d')  # Converte para string

        if 'Horas semanais dedicadas' in df.columns:
            df['Horas semanais dedicadas'] = df['Horas semanais dedicadas'].astype(int)  # Converte para int

        # Formata todos os valores de string nas colunas, exceto 'Comentario Adicional'
        for col in df.select_dtypes(include=['object']).columns:
            if col != 'Comentario Adicional':  # Ignora a coluna 'Comentario Adicional'
                df[col] = df[col].apply(format_string_value)
        
        all_data.append(df)  # Adiciona o DataFrame à lista
    
    conn.close()  # Fecha a conexão com o banco de dados
    
    # Concatena todos os DataFrames em um único DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)  # Ignora os índices para um novo índice contínuo

    # Mapeia os nomes das colunas para os nomes corrigidos
    corrected_column_names = [
        'Data', 'Nome Completo', 'Atualmente Sou', 'Minha Equipe', 'Reuniões do Time', 
        'Colaboração Entre Membros', 'Ambiente de Aprendizagem', 'Comunicação Entre Membros', 
        'Satisfação Geral Comunidade', 'Feedbacks', 'Horas Semanais Dedicadas', 'Comentário Adicional'
    ]
    
    # Substitui os nomes das colunas se os nomes mapeados forem encontrados no DataFrame
    combined_df.columns = corrected_column_names[:len(combined_df.columns)]
    
    return combined_df

# Caminho do banco de dados SQLite
SQLITE_DB = 'dags/src/data/data.db'

def transform():
    """
    Lê as tabelas do banco de dados e retorna um único DataFrame com todos os dados.
    
    Returns:
        pd.DataFrame: DataFrame combinado com dados de todas as tabelas.
    """
    # Lê as tabelas do banco de dados e retorna um único DataFrame
    combined_dataframe = read_tables_from_db(SQLITE_DB)

    # Retorna o DataFrame combinado
    return combined_dataframe

# Executa a transformação e imprime as primeiras 20 linhas do DataFrame resultante
# df = transform()
# print(df.head(20))  # Imprime as primeiras 20 linhas do DataFrame
