import socket
import random

SIZE_TABLERO = 5
FONDO_MAPA = "~"
BARCO_MAPA = "B"
HUNDIDO_MAPA = "H"
DISPARO_MAPA = "*"

class Coordenada:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Barco:
    def __init__ (self, largo, estado, vertical):
        self.largo = largo
        self.estado = estado # true = vivo, false = hundido
        self.vertical = vertical # true = vertical, false = horizontal
        self.coordenada = []


class Servidor:
    def __init__(self, SERVER_IP, PORT, BUFFER_SIZE):
        self.SERVER_IP = SERVER_IP
        self.PORT = PORT
        self.BUFFER_SIZE = BUFFER_SIZE
        self.serverSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.usuarios = {}
        self.tablero = []

    def bind(self):
        self.serverSocket.bind((self.SERVER_IP, self.PORT))
        print("UDP server up and listening")
        pass
    
    def recibirMSG(self):
        bytesAddressPair = self.serverSocket.recvfrom(self.BUFFER_SIZE)
        message = bytesAddressPair[0]
        message = message.decode("utf-8")
        address = bytesAddressPair[1]
        return message, address

    def escuchar(self):
        msgFromServer = ""
        bytesToSend = str.encode(msgFromServer)

        while (True):
            # Aceptar una nueva conexión
            message, address = self.recibirMSG()
            print(f"{self.usuarios[address]}: {message}")
            self.serverSocket.sendto(bytesToSend, address)


class Cliente:
    def __init__ (self,servidor: Servidor):
        self.servidor = servidor
        self.clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    
    def conectarAServidor(self):
        while(True):
            enviarMensaje = input("Ingrese su mensaje: ")
            self.enviarMensaje(enviarMensaje)

    # ====== Función Principal ======
    def enviarMensaje(self, mensaje):
        # ====== Enviar mensaje al servidor ======
        msg = self.enviarMensajePrefix(mensaje)
        print(msg)
        pass

def __main__():
    pass

if __name__ == "__main__":
    __main__()
    