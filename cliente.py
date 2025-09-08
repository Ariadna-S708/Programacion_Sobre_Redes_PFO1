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
            print("Cerrando conexión...")
            break
        
        # Enviar el mensaje al servidor
        cliente_socket.send(mensaje.encode())
        
        # Recibir respuesta del servidor
        respuesta = cliente_socket.recv(1024).decode()
        print(f"[SERVIDOR] {respuesta}")
    
    cliente_socket.close()
    
    
# Configuración del cliente

if __name__ == '__main__':
    cliente_socket = conectar_servidor()
    enviar_mensaje(cliente_socket, "")