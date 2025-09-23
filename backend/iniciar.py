import webbrowser
import threading
import subprocess
import time

import json

def cargar_datos():
    with open('datos.json', 'r') as archivo:
        return json.load(archivo)

def guardar_datos(data):
    with open('datos.json', 'w') as archivo:
        json.dump(data, archivo)


def abrir_navegador():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

threading.Thread(target=abrir_navegador).start()
subprocess.run(["python", "app.py"])
