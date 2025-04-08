import sqlite3
from ui.app import criar_interface
from database.init_db import inicializar_banco

def main():
    conn = sqlite3.connect("controle_gastos.db")
    cursor = conn.cursor()

    # Inicializa o banco se necessário
    inicializar_banco(conn)

    # Executa a interface
    criar_interface(conn, cursor)

if __name__ == "__main__":
    main()
