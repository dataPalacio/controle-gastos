import sqlite3

def conectar():
    conn = sqlite3.connect("data/compras.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            responsavel TEXT,
            cartao TEXT,
            categoria TEXT,
            descricao TEXT,
            valor REAL
        )
    ''')
    conn.commit()
    return conn, cursor
