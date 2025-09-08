import socket
import sqlite3
import threading
from datetime import datetime


# Configuracion del servidor

HOST = "localhost"
PORT = 5000
DB_PATH = "mensajes.db"
BACKLOG = 5
db_lock = threading.Lock()


# Inicializacion de la base de datos

def inicializar_db() -> None:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contenido TEXT NOT NULL,
                    fecha_envio TEXT NOT NULL,
                    ip_cliente TEXT NOT NULL
                )
            """)
            conn.commit()
            print(f"Base de datos inicializada correctamente.")
    except sqlite3.Error as e:
        print(f"No se pudo inicializar la base de datos: {e}")
        raise


# Guardar mensaje en la base de datos

def guardar_mensaje(contenido: str, ip_cliente: str) -> None:
    try:
        fecha_envio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with db_lock:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mensajes (contenido, fecha_envio, ip_cliente)
                    VALUES (?, ?, ?)
                    """,
                    (contenido, fecha_envio, ip_cliente)
                )
                conn.commit()
                print(f"Mensaje guardado desde {ip_cliente} a las {fecha_envio}")
    except sqlite3.Error as e:
        print(f"No se pudo guardar el mensaje: {e}")
        raise


# Iniciar socket

def inicializar_socket() -> socket.socket:
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(BACKLOG)
        print(f"[SERVIDOR] Escuchando en {HOST}:{PORT} ...")
        return server_socket
    except OSError as e:
        print(f"[ERROR][SOCKET] No se pudo iniciar el servidor: {e}")
        raise


# Manejar cliente

def manejar_cliente(cliente_socket: socket.socket, direccion: tuple) -> None:
    ip_cliente = direccion[0]
    print(f"[+] Nueva conexión desde {ip_cliente}")
    try:
        while True:
            datos = cliente_socket.recv(1024)
            if not datos:
                break  # El cliente cerró la conexión

            mensaje = datos.decode(errors="ignore").strip()
            if mensaje.lower() == "exit":  # Palabra clave para desconectar
                break

            # Guardar el mensaje en la base de datos
            guardar_mensaje(mensaje, ip_cliente)

            # Responder al cliente
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            respuesta = f"Mensaje recibido: {ts}"
            cliente_socket.sendall(respuesta.encode())

    except ConnectionResetError:
        print(f"[!] Conexión reiniciada por {ip_cliente}")
    except Exception as e:
        print(f"[ERROR] Cliente {ip_cliente}: {e}")
    finally:
        try:
            cliente_socket.close()
        except Exception:
            pass
        print(f"[-] Conexión cerrada: {ip_cliente}")


# Aceptar conexiones entrantes

def aceptar_conexiones(server_socket: socket.socket) -> None:
    try:
        while True:
            cliente_socket, direccion = server_socket.accept()
            # Crear hilo para manejar cliente
            hilo = threading.Thread(
                target=manejar_cliente,
                args=(cliente_socket, direccion),
                daemon=True
            )
            hilo.start()
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Interrupción recibida. Cerrando...")


# Cerrar servidor

def cerrar_servidor(server_socket: socket.socket) -> None:
    try:
        server_socket.close()
    except Exception:
        pass
    print("[SERVIDOR] Apagado.")


# Ejecutar servidor

def ejecutar() -> None:
    inicializar_db()      # Inicializa la base de datos
    server_socket = inicializar_socket()  # Inicializa el servidor
    aceptar_conexiones(server_socket)    # Comienza a aceptar conexiones
    cerrar_servidor(server_socket)  # Cierra el servidor cuando termine


# Ejecutar el servidor

if __name__ == "__main__":
    ejecutar()