def listar_compras(cursor):
    cursor.execute("SELECT * FROM compras ORDER BY data DESC")
    return cursor.fetchall()

def adicionar_compra(cursor, conn, dados):
    cursor.execute("INSERT INTO compras (data, responsavel, cartao, categoria, descricao, valor) VALUES (?, ?, ?, ?, ?, ?)", dados)
    conn.commit()

def excluir_compra(cursor, conn, id_):
    cursor.execute("DELETE FROM compras WHERE id = ?", (id_,))
    conn.commit()
