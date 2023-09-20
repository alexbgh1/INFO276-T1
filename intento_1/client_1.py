import os
import atexit
from dotenv import load_dotenv
from clases import Servidor, Cliente
import signal

# Load environment variables
load_dotenv()

# ====== Setup - Params ======
SERVER_IP = os.getenv("SERVER_IP")
PORT = int(os.getenv("PORT"))
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE"))

# =========== SIGNALS ===========
def handler(signum, frame):
    print("Señal recibida: ", signum)
    if signum == 2:
        print("Señal SIGINT recibida. Desconectando...")
        cliente.desconectar()
    pass

# =========== MAIN ===========
servidor = Servidor(SERVER_IP, PORT, BUFFER_SIZE)


jugador = input("Ingrese su nombre: ")
while jugador in ["", " ", "DESCONECTAR="]:
    jugador = input("Ingrese su nombre: ")

cliente = Cliente(jugador,servidor)

signal.signal(signal.SIGINT, handler)

response = cliente.enviarMensajeInicio("NOMBRE="+cliente.nombre)
if response:
    print("Escribe 'HELP;' para ver los comandos disponibles")
    cliente.conectarAServidor()

print("Conexión finalizada. Saliendo...")