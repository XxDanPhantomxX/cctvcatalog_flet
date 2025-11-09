import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "storage", "data", "inventory.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabla de productos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo TEXT NOT NULL,
        precio REAL NOT NULL,
        stock INTEGER DEFAULT 0,
        imagen TEXT
    )
    """)

    # Tabla de configuración general (mano de obra, logo, etc.)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS config (
        clave TEXT PRIMARY KEY,
        valor TEXT
    )
    """)

    # Inserta mano de obra por defecto si no existe
    cursor.execute("INSERT OR IGNORE INTO config (clave, valor) VALUES ('mano_obra', '150')")
    cursor.execute("INSERT OR IGNORE INTO config (clave, valor) VALUES ('logo', '')")

    conn.commit()
    conn.close()


def get_connection():
    return sqlite3.connect(DB_PATH)


def add_product(nombre, tipo, precio, stock, imagen):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO productos (nombre, tipo, precio, stock, imagen) VALUES (?, ?, ?, ?, ?)",
                (nombre, tipo, precio, stock, imagen))
    conn.commit()
    conn.close()


def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, tipo, precio, stock, imagen FROM productos")
    data = cur.fetchall()
    conn.close()
    return data


def delete_product(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM productos WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def update_config(key, value):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO config (clave, valor) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


def get_config(key):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT valor FROM config WHERE clave = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def reset_autoincrement():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM sqlite_sequence WHERE name='productos';")
    conn.commit()
    conn.close()
    print("✅ Contador de IDs reiniciado correctamente.")