import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def connect_to_database():
    try:
        conexao_banco = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT"),
            ssl_disabled=False
        )
        return conexao_banco
    except mysql.connector.Error as erro_conexao:
        print(f"Erro ao conectar ao banco de dados: {erro_conexao}")
        return None


conexao_inicial = connect_to_database()

if conexao_inicial:
    print("Conexão bem-sucedida!")
else:
    print("Falha na conexão ao banco de dados.")
