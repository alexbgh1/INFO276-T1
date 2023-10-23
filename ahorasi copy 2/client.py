import os
from dotenv import load_dotenv
from clases import Servidor, Cliente

# Load environment variables
load_dotenv()

# ====== Setup - Params ======
SERVER_IP = os.getenv("SERVER_IP")
PORT = int(os.getenv("PORT"))
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE"))

# =========== MAIN ===========
servidor = Servidor(SERVER_IP, PORT, BUFFER_SIZE)
cliente = Cliente(servidor)

cliente.conectarAServidor()


print("Conexión finalizada. Saliendo...")