# ver_pedidos.py - Leer la base de datos SQLite de Bodega Express (IaaS en Codespaces)
#
# Cómo usarlo:
#   1. Deja corriendo el servidor (python app.py) en la primera terminal.
#   2. Abre OTRA terminal con el botón "+" del panel de terminal.
#   3. Escribe:  python ver_pedidos.py
#
# Este archivo debe estar en la misma carpeta que app.py y bodega.db.

import os
import sqlite3

BD = "bodega.db"


def conectar():
    if not os.path.exists(BD):
        print(f"No existe {BD}. Primero ejecuta 'python app.py' y envía un pedido desde la app.")
        raise SystemExit
    con = sqlite3.connect(BD)
    con.row_factory = sqlite3.Row
    return con


def imprimir_tabla(filas, columnas):
    """Muestra filas como una tabla con columnas alineadas."""
    if not filas:
        print("  (sin datos)")
        return
    anchos = [max(len(str(c)), *(len(str(f[c])) for f in filas)) for c in columnas]
    linea = "  ".join(str(c).ljust(a) for c, a in zip(columnas, anchos))
    print(linea)
    print("-" * len(linea))
    for f in filas:
        print("  ".join(str(f[c]).ljust(a) for c, a in zip(columnas, anchos)))


def ver_todos(con):
    filas = con.execute("SELECT * FROM pedidos ORDER BY id DESC").fetchall()
    imprimir_tabla(filas, ["id", "cliente", "producto", "cantidad", "fecha"])


def total_por_producto(con):
    filas = con.execute("""SELECT producto, SUM(cantidad) AS total, COUNT(*) AS pedidos
                           FROM pedidos GROUP BY producto ORDER BY total DESC""").fetchall()
    imprimir_tabla(filas, ["producto", "total", "pedidos"])


def total_por_cliente(con):
    filas = con.execute("""SELECT cliente, COUNT(*) AS pedidos, SUM(cantidad) AS unidades
                           FROM pedidos GROUP BY cliente ORDER BY pedidos DESC""").fetchall()
    imprimir_tabla(filas, ["cliente", "pedidos", "unidades"])


def contar(con):
    n = con.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    print(f"  Hay {n} pedidos guardados en {BD}")


def buscar(con):
    texto = input("  Producto o cliente a buscar: ").strip()
    filas = con.execute("""SELECT * FROM pedidos
                           WHERE producto LIKE ? OR cliente LIKE ? ORDER BY id DESC""",
                        (f"%{texto}%", f"%{texto}%")).fetchall()
    imprimir_tabla(filas, ["id", "cliente", "producto", "cantidad", "fecha"])


def borrar(con):
    try:
        id_ = int(input("  id del pedido a borrar: "))
    except ValueError:
        print("  Debe ser un número")
        return
    cur = con.execute("DELETE FROM pedidos WHERE id = ?", (id_,))
    con.commit()
    print("  Pedido borrado" if cur.rowcount else "  No existe ese id")


def borrar_todo(con):
    if input("  ¿Seguro que quieres borrar TODOS los pedidos? (si/no): ").strip().lower() == "si":
        con.execute("DELETE FROM pedidos")
        con.commit()
        print("  Todos los pedidos fueron borrados")


def sql_libre(con):
    print("  Escribe una consulta SQL (ej. SELECT * FROM pedidos WHERE cantidad > 5)")
    consulta = input("  SQL> ").strip()
    try:
        cur = con.execute(consulta)
        if cur.description:  # fue un SELECT
            columnas = [d[0] for d in cur.description]
            imprimir_tabla(cur.fetchall(), columnas)
        else:
            con.commit()
            print(f"  Listo. Filas afectadas: {cur.rowcount}")
    except sqlite3.Error as e:
        print(f"  Error de SQL: {e}")


def estructura(con):
    sql = con.execute("SELECT sql FROM sqlite_master WHERE name = 'pedidos'").fetchone()[0]
    print(sql)


OPCIONES = {
    "1": ("Ver todos los pedidos", ver_todos),
    "2": ("Total vendido por producto", total_por_producto),
    "3": ("Pedidos por cliente", total_por_cliente),
    "4": ("Contar pedidos", contar),
    "5": ("Buscar por producto o cliente", buscar),
    "6": ("Borrar un pedido", borrar),
    "7": ("Borrar todos los pedidos", borrar_todo),
    "8": ("Escribir SQL libre", sql_libre),
    "9": ("Ver la estructura de la tabla", estructura),
}

if __name__ == "__main__":
    con = conectar()
    while True:
        print("\n=== Bodega Express · base de datos SQLite ===")
        for k, (texto, _) in OPCIONES.items():
            print(f"  {k}. {texto}")
        print("  0. Salir")
        op = input("Elige una opción: ").strip()
        if op == "0":
            break
        if op in OPCIONES:
            print()
            OPCIONES[op][1](con)
        else:
            print("  Opción no válida")
    con.close()