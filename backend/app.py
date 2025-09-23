

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
from werkzeug.utils import secure_filename
from urllib.parse import quote
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('datos.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
app.secret_key = 'clave-secreta'

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PRODUCTOS'] = []
carrito = []

ADMIN_USER = "gustyadmin"
ADMIN_PASS = "admin123"

@app.route('/')
def home():
    conn = get_db_connection()
    promos = conn.execute('SELECT * FROM promociones').fetchall()
    conn.close()
    return render_template('index.html', promos=promos)

@app.route('/quienes-somos')
def quienes_somos():
    return render_template('quienes_somos.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['usuario']
        password = request.form['contrasena']
        if user == ADMIN_USER and password == ADMIN_PASS:
            session['rol'] = 'admin'
            session['usuario'] = user
            return redirect(url_for('admin'))
        else:
            return "Credenciales incorrectas"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('rol', None)
    session.pop('usuario', None)
    return redirect(url_for('home'))

@app.route('/admin')
def admin():
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))
    conn = get_db_connection()
    promos = conn.execute('SELECT * FROM promociones').fetchall()
    conn.close()
    return render_template('admin.html', promos=promos)

@app.route('/add_promo', methods=['POST'])
def add_promo():
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))
    titulo = request.form['titulo']
    cuerpo = request.form['cuerpo']
    imagen = request.files['imagen']
    filename = secure_filename(imagen.filename)
    imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    conn = get_db_connection()
    conn.execute('INSERT INTO promociones (titulo, cuerpo, imagen) VALUES (?, ?, ?)', (titulo, cuerpo, filename))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/productos')
def productos():
    return render_template('productos.html', productos=app.config['PRODUCTOS'], rol=session.get('rol'))

@app.route('/add_producto', methods=['POST'])
def add_producto():
    if session.get('rol') != 'admin':
        return "No autorizado"
    nombre = request.form['nombre']
    app.config['PRODUCTOS'].append(nombre)
    return redirect(url_for('productos'))

@app.route('/delete_producto/<int:index>')
def delete_producto(index):
    if session.get('rol') != 'admin':
        return "No autorizado"
    try:
        app.config['PRODUCTOS'].pop(index)
    except:
        pass
    return redirect(url_for('productos'))

@app.route('/buscar')
def buscar():
    query = request.args.get('query', '').lower()
    resultados = [p for p in app.config['PRODUCTOS'] if query in p.lower()]
    return render_template('productos.html', productos=resultados, rol=session.get('rol'))

@app.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    nombre = request.form['nombre']
    tipo = request.form['tipo']
    carrito.append({'nombre': nombre, 'tipo': tipo})
    return redirect(url_for('productos'))

@app.route('/carrito')
def ver_carrito():
    return render_template('carrito.html', carrito=carrito)

@app.route('/quitar_carrito/<int:index>')
def quitar_carrito(index):
    try:
        carrito.pop(index)
    except:
        pass
    return redirect(url_for('ver_carrito'))

@app.route('/finalizar_compra')
def finalizar_compra():
    if not carrito:
        return redirect(url_for('ver_carrito'))
    mensaje = "¡Hola! Quiero realizar el siguiente pedido:\n"
    for item in carrito:
        mensaje += f"- {item['tipo'].upper()}: {item['nombre']}\n"
    mensaje += "\nForma de pago: a convenir. ¡Gracias!"
    mensaje_codificado = quote(mensaje)
    numero = '3844450120'
    url = f"https://wa.me/{numero}?text={mensaje_codificado}"
    return redirect(url)

if __name__ == '__main__':
    app.run(debug=True)
