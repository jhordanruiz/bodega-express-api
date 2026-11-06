import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
BD = "bodega.db"

def conectar():
    con = sqlite3.connect(BD)
    con.row_factory = sqlite3.Row
    return con

with conectar() as con:
    con.execute("""create table if not exists pedidos (
        id integer primary key autoincrement,
        cliente text, producto text, cantidad integer,
        fecha text default current_timestamp)""")

@app.get("/pedidos")
def listar():
    with conectar() as con:
        filas = con.execute("select * from pedidos order by id desc limit 50").fetchall()
    return jsonify([dict(f) for f in filas])

@app.post("/pedidos")
def crear():
    d = request.get_json(force=True)
    try:
        cantidad = int(d["cantidad"])
        cliente, producto = d["cliente"].strip(), d["producto"].strip()
    except (KeyError, ValueError, AttributeError):
        return jsonify(error="faltan datos"), 400
    if not cliente or not producto or cantidad <= 0:
        return jsonify(error="datos inválidos"), 400
    with conectar() as con:
        con.execute("insert into pedidos (cliente, producto, cantidad) values (?, ?, ?)",
                    (cliente, producto, cantidad))
    print(f"Nuevo pedido: {cantidad} x {producto} - {cliente}")
    return jsonify(ok=True), 201

@app.get("/")
def inicio():
    return "Servidor de Bodega Express encendido"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)