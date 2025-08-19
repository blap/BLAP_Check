# database/manager.py

import duckdb
import os

# Define o caminho para o ficheiro da base de dados dentro da pasta 'data'
DB_FILE = os.path.join('data', 'app_database.db')

def initialize_database():
    """
    Cria a base de dados e a tabela de aplicações se elas não existirem.
    """
    # Garante que a pasta 'data' existe
    os.makedirs('data', exist_ok=True)

    # Conecta-se à base de dados. O ficheiro será criado se não existir.
    con = duckdb.connect(database=DB_FILE, read_only=False)

    # Cria a tabela 'applications' se ela ainda não existir.
    # Usamos VARCHAR para texto e INTEGER PRIMARY KEY para um ID único.
    con.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY,
        name VARCHAR NOT NULL,
        extension_id VARCHAR,
        extension_config VARCHAR,
        local_version VARCHAR,
        latest_version VARCHAR
    );
    """)

    # Fecha a conexão com a base de dados.
    con.close()
    print("Base de dados inicializada com sucesso.")


def get_all_applications():
    """
    Busca todas as aplicações da base de dados.
    Retorna uma lista de dicionários, onde cada dicionário representa uma aplicação.
    """
    con = duckdb.connect(database=DB_FILE, read_only=True)
    # Retorna os resultados como uma lista de dicionários para ser mais fácil de usar
    apps = con.execute("SELECT * FROM applications ORDER BY name;").fetchdf().to_dict('records')
    con.close()
    return apps

def add_application(app_data):
    """
    Adiciona uma nova aplicação à base de dados.
    app_data deve ser um dicionário com as chaves correspondentes às colunas.
    """
    con = duckdb.connect(database=DB_FILE, read_only=False)
    con.execute("INSERT INTO applications (name, local_version, extension_id, extension_config) VALUES (?, ?, ?, ?);",
                [app_data['name'], app_data['local_version'], app_data['extension_id'], app_data['extension_config']])
    con.close()

def update_application(app_id, app_data):
    """
    Atualiza uma aplicação existente na base de dados.
    """
    con = duckdb.connect(database=DB_FILE, read_only=False)
    con.execute("UPDATE applications SET name = ?, local_version = ?, extension_id = ?, extension_config = ? WHERE id = ?;",
                [app_data['name'], app_data['local_version'], app_data['extension_id'], app_data['extension_config'], app_id])
    con.close()

def delete_application(app_id):
    """
    Remove uma aplicação da base de dados pelo seu ID.
    """
    con = duckdb.connect(database=DB_FILE, read_only=False)
    con.execute("DELETE FROM applications WHERE id = ?;", [app_id])
    con.close()


def update_app_latest_version(app_id, latest_version):
    """
    Atualiza apenas o campo latest_version de uma aplicação.
    """
    con = duckdb.connect(database=DB_FILE, read_only=False)
    con.execute("UPDATE applications SET latest_version = ? WHERE id = ?;",
                [latest_version, app_id])
    con.close()
