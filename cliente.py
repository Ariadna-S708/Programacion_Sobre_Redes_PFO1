import socket
import sqlite3

HOST = "localhost"
PORT = 5000

# Conectar al servidor

def conectar_servidor() -> socket.socket:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        print(f"Conectado al servidor en {HOST}: {PORT}")
        return s
    except socket.error as e:
        print(f"No se pudo conectar al servidor: {e}")


# Enviar mensaje al servidor

def enviar_mensaje(cliente_socket: socket.socket, mensaje: str) -> None:
    while True:
        # Pedir mensaje al usuario
        mensaje = input("Escribe un mensaje (o 'éxito' para salir): ")
        
        if mensaje.lower() == 'éxito':
            print("\nCerrando conexión...\n")
            break
        
        # Enviar el mensaje al servidor
        cliente_socket.send(mensaje.encode())
        
        # Recibir respuesta del servidor
        respuesta = cliente_socket.recv(1024).decode()
        print(f"[SERVIDOR] {respuesta}")
    
    cliente_socket.close()
    ver_mensajes_guardados()


# Mostrar mensajes guardados en la base de datos

def ver_mensajes_guardados():

    ver = input("¿Quiere ver los mensajes guardados? ('si' para ver): ")

    if ver.lower() == "si":
        # Conectar a la base de datos
        conn = sqlite3.connect("mensajes.db")
        cursor = conn.cursor()

        # Consultar los mensajes guardados
        cursor.execute("SELECT * FROM mensajes")
        mensajes = cursor.fetchall()

        # Mostrar los mensajes
        encabezado = f"| {'ID':<5} | {'Contenido':<30} | {'Fecha Envío':<20} | {'IP Cliente':<15} |"
        print("-" * len(encabezado))  # Línea superior
        print(encabezado)
        print("-" * len(encabezado))  # Línea separadora
        
        # Mostrar cada mensaje en formato de tabla
        for mensaje in mensajes:
            print(f"| {mensaje[0]:<5} | {mensaje[1]:<30} | {mensaje[2]:<20} | {mensaje[3]:<15} |")
        
        print("-" * len(encabezado))  # Línea inferior

        # Cerrar conexión a la base de datos
        conn.close()
    else:
        print("No se mostraran los mensajes guardados. Adiós!\n")


# Configuración del cliente

if __name__ == '__main__':
    cliente_socket = conectar_servidor()
    enviar_mensaje(cliente_socket, "")