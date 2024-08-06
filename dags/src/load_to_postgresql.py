import psycopg2
from psycopg2 import sql
import pandas as pd
import credentials
import credentials.pgdb_acess

def create_database(conn, db_name):
    """
    Cria um novo banco de dados com o nome especificado se não existir.

    Parâmetros:
    conn -- Conexão com o banco de dados PostgreSQL.
    db_name -- Nome do novo banco de dados a ser criado.
    """
    # Cria um novo cursor sem usar uma transação
    with conn.cursor() as cur:
        try:
            # Verifica se o banco de dados já existe
            cur.execute(sql.SQL("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s"), (db_name,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(sql.SQL("COMMIT"))  # Sai de uma possível transação
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
                print(f'Banco de dados "{db_name}" criado com sucesso.')
            else:
                print(f'O banco de dados "{db_name}" já existe.')
        except Exception as e:
            print(f'Erro ao criar banco de dados: {e}')
            conn.rollback()

def create_schema_and_table(conn):
    """
    Cria o schema 'survey' e a tabela 'survey_records' se não existirem.
    
    Parâmetros:
    conn -- Conexão com o banco de dados PostgreSQL.
    """
    with conn.cursor() as cur:
        try:
            # Criar o schema 'survey' se não existir
            cur.execute('CREATE SCHEMA IF NOT EXISTS survey')
            print('Schema "survey" verificado ou criado com sucesso.')

            # Criar a tabela 'survey_records' no schema 'survey' se não existir
            cur.execute(sql.SQL("""
                CREATE TABLE IF NOT EXISTS survey.survey_records (
                    id SERIAL PRIMARY KEY,
                    data TIMESTAMP WITHOUT TIME ZONE,
                    nome_completo VARCHAR,
                    atualmente_sou VARCHAR,
                    minha_equipe VARCHAR,
                    reunioes_do_time VARCHAR,
                    colaboracao_entre_membros VARCHAR,
                    ambiente_de_aprendizagem VARCHAR,
                    comunicacao_entre_membros VARCHAR,
                    satisfacao_geral_comunidade VARCHAR,
                    feedbacks VARCHAR,
                    horas_semanais_dedicadas INTEGER,
                    comentario_adicional VARCHAR,
                    UNIQUE (data, nome_completo)
                )
            """))
            print('Tabela criada com sucesso no schema "survey".')
        except Exception as e:
            print(f'Erro ao criar schema ou tabela: {e}')
        finally:
            # Commit das alterações
            conn.commit()

def insert_dataframe_to_db(df, conn):
    """
    Insere os dados do DataFrame na tabela 'survey_records', evitando duplicatas.
    
    Parâmetros:
    df -- DataFrame contendo os dados a serem inseridos.
    conn -- Conexão com o banco de dados PostgreSQL.
    """
    with conn.cursor() as cur:
        for index, row in df.iterrows():
            try:
                cur.execute(sql.SQL("""
                    INSERT INTO survey.survey_records (data, nome_completo, atualmente_sou, minha_equipe, reunioes_do_time, 
                        colaboracao_entre_membros, ambiente_de_aprendizagem, comunicacao_entre_membros, 
                        satisfacao_geral_comunidade, feedbacks, horas_semanais_dedicadas, comentario_adicional)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (data, nome_completo) DO NOTHING
                """), (row['data'], row['nome_completo'], row['atualmente_sou'], row['minha_equipe'],
                        row['reunioes_do_time'], row['colaboracao_entre_membros'], row['ambiente_de_aprendizagem'],
                        row['comunicacao_entre_membros'], row['satisfacao_geral_comunidade'], row['feedbacks'],
                        row['horas_semanais_dedicadas'], row['comentario_adicional']))
            except Exception as e:
                print(f'Erro ao inserir dados na linha {index}: {e}')
        # Commit das inserções
        conn.commit()
        print('Dados inseridos na tabela com sucesso.')

def load_to_postgresql(df: pd.DataFrame):
    """
    Conecta ao banco de dados PostgreSQL, cria o banco de dados 'Records' se necessário,
    cria o schema e a tabela se necessário e insere os dados do DataFrame.
    
    Parâmetros:
    df -- DataFrame contendo os dados a serem carregados.
    """
    PSQL = credentials.pgdb_acess.PSQL
    db_name = 'Records'
    
    try:
        # Estabelecer conexão com o banco de dados padrão
        conn = psycopg2.connect(PSQL)
        print('Conexão com o banco de dados estabelecida.')
        
        # Criar o banco de dados se não existir
        create_database(conn, db_name)
        
        # Fechar a conexão com o banco de dados padrão antes de conectar ao novo banco
        conn.close()
        
        # Conectar ao novo banco de dados
        conn = psycopg2.connect(f'{credentials.pgdb_acess.PSQL_server}{db_name}')
        print(f'Conexão com o banco de dados "{db_name}" estabelecida.')
        
        # Criar o schema e a tabela se necessário
        create_schema_and_table(conn)
        
        # Renomear as colunas do DataFrame para corresponder às colunas da tabela
        df.rename(columns={
            'Data': 'data',
            'Nome Completo': 'nome_completo',
            'Atualmente Sou': 'atualmente_sou',
            'Minha Equipe': 'minha_equipe',
            'Reuniões do Time': 'reunioes_do_time',
            'Colaboração Entre Membros': 'colaboracao_entre_membros',
            'Ambiente de Aprendizagem': 'ambiente_de_aprendizagem',
            'Comunicação Entre Membros': 'comunicacao_entre_membros',
            'Satisfação Geral Comunidade': 'satisfacao_geral_comunidade',
            'Feedbacks': 'feedbacks',
            'Horas Semanais Dedicadas': 'horas_semanais_dedicadas',
            'Comentário Adicional': 'comentario_adicional'
        }, inplace=True)

        # Converter a coluna 'data' para o tipo datetime
        df['data'] = pd.to_datetime(df['data'])

        # Inserir os dados do DataFrame na tabela
        insert_dataframe_to_db(df, conn)

    except Exception as e:
        print(f'Erro ao conectar com o banco de dados: {e}')
    finally:
        if conn:
            # Fechar a conexão com o banco de dados
            conn.close()
            print('Conexão com o banco de dados fechada.')
