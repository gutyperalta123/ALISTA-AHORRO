import os
import sqlite3
from urllib.parse import quote
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

# ---------------------------
# Config / utilidades
# ---------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "datos.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db():
    """Crea tabla 'promociones' si no existe y puede precargar datos de demo."""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS promociones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            cuerpo TEXT NOT NULL,
            imagen TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

# ---------------------------
# App Flask
# ---------------------------

app = Flask(__name__, template_folder="templates", static_folder="static")

# Variables de entorno (con defaults de desarrollo)
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta")
ADMIN_USER = os.getenv("ADMIN_USER", "gustyadmin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "3844450120")

# Config de uploads en ejecución
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
app.config["PRODUCTOS"] = []
carrito = []

# ---------------------------
# Rutas
# ---------------------------

@app.route("/")
def home():
    conn = get_db_connection()
    promos = conn.execute("SELECT * FROM promociones").fetchall()
    conn.close()
    return render_template("index.html", promos=promos)

@app.route("/quienes-somos")
def quienes_somos():
    return render_template("quienes_somos.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["usuario"]
        password = request.form["contrasena"]
        if user == ADMIN_USER and password == ADMIN_PASS:
            session["rol"] = "admin"
            session["usuario"] = user
            return redirect(url_for("admin"))
        return "Credenciales incorrectas"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("rol", None)
    session.pop("usuario", None)
    return redirect(url_for("home"))

@app.route("/admin")
def admin():
    if session.get("rol") != "admin":
        return redirect(url_for("login"))
    conn = get_db_connection()
    promos = conn.execute("SELECT * FROM promociones").fetchall()
    conn.close()
    return render_template("admin.html", promos=promos)

@app.route("/add_promo", methods=["POST"])
def add_promo():
    if session.get("rol") != "admin":
        return redirect(url_for("login"))

    titulo = request.form.get("titulo", "").strip()
    cuerpo = request.form.get("cuerpo", "").strip()
    imagen = request.files.get("imagen")

    if not titulo or not cuerpo or not imagen or imagen.filename == "":
        return redirect(url_for("admin"))

    filename = secure_filename(imagen.filename)
    ensure_upload_dir()
    imagen.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO promociones (titulo, cuerpo, imagen) VALUES (?, ?, ?)",
        (titulo, cuerpo, filename),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

@app.route("/productos")
def productos():
    return render_template("productos.html", productos=app.config["PRODUCTOS"], rol=session.get("rol"))

@app.route("/add_producto", methods=["POST"])
def add_producto():
    if session.get("rol") != "admin":
        return "No autorizado"
    nombre = request.form.get("nombre", "").strip()
    if nombre:
        app.config["PRODUCTOS"].append(nombre)
    return redirect(url_for("productos"))

@app.route("/delete_producto/<int:index>")
def delete_producto(index):
    if session.get("rol") != "admin":
        return "No autorizado"
    try:
        app.config["PRODUCTOS"].pop(index)
    except IndexError:
        pass
    return redirect(url_for("productos"))

@app.route("/buscar")
def buscar():
    query = request.args.get("query", "").lower()
    resultados = [p for p in app.config["PRODUCTOS"] if query in p.lower()]
    return render_template("productos.html", productos=resultados, rol=session.get("rol"))

@app.route("/agregar_carrito", methods=["POST"])
def agregar_carrito():
    nombre = request.form.get("nombre", "").strip()
    tipo = request.form.get("tipo", "").strip()
    if nombre and tipo:
        carrito.append({"nombre": nombre, "tipo": tipo})
    return redirect(url_for("productos"))

@app.route("/carrito")
def ver_carrito():
    return render_template("carrito.html", carrito=carrito)

@app.route("/quitar_carrito/<int:index>")
def quitar_carrito(index):
    try:
        carrito.pop(index)
    except IndexError:
        pass
    return redirect(url_for("ver_carrito"))

@app.route("/finalizar_compra")
def finalizar_compra():
    if not carrito:
        return redirect(url_for("ver_carrito"))
    mensaje = "¡Hola! Quiero realizar el siguiente pedido:\n"
    for item in carrito:
        mensaje += f"- {item['tipo'].upper()}: {item['nombre']}\n"
    mensaje += "\nForma de pago: a convenir. ¡Gracias!"
    url = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(mensaje)}"
    return redirect(url)

# ---------------------------
# Entrypoint
# ---------------------------

def bootstrap():
    ensure_upload_dir()
    init_db()

bootstrap()

if __name__ == "__main__":
    # Desarrollo local
    app.run(host="0.0.0.0", port=5000, debug=True)
