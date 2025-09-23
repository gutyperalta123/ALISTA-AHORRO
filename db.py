import sqlite3

DB_NAME = 'datos.db'

def crear_tablas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promociones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            cuerpo TEXT NOT NULL,
            imagen TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carrito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# 🔹 FUNCIONES PROMOCIONES
def agregar_promocion(titulo, cuerpo, imagen):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO promociones (titulo, cuerpo, imagen) VALUES (?, ?, ?)", (titulo, cuerpo, imagen))
    conn.commit()
    conn.close()

def obtener_promociones():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM promociones")
    promos = cursor.fetchall()
    conn.close()
    return promos

def eliminar_promocion(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM promociones WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# 🔹 FUNCIONES PRODUCTOS
def agregar_producto(nombre):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO productos (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()

def obtener_productos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

def eliminar_producto(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# 🔹 FUNCIONES CARRITO
def agregar_al_carrito(nombre, tipo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO carrito (nombre, tipo) VALUES (?, ?)", (nombre, tipo))
    conn.commit()
    conn.close()

def obtener_carrito():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM carrito")
    items = cursor.fetchall()
    conn.close()
    return items

def quitar_del_carrito(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carrito WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def vaciar_carrito():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carrito")
    conn.commit()
    conn.close()
