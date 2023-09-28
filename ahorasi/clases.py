import socket
import json
# importar constantes desde constants.py
from constants import *

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
            print(f"Mensaje recibido: {message}")

            self.serverSocket.sendto(str.encode(message), address)


class MessageStructure:
    def __init__(self, action: str, bot: int, ships: dict, position: []):
        self.action = action
        self.bot = bot
        self.ships = ships
        self.position = position

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

class Cliente:
    def __init__ (self,servidor: Servidor):
        self.servidor = servidor
        self.clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.messageToSend = {} # MessageStructure
        self.lives = 6
    
    def conectarAServidor(self):
        VALID_ACTION = ["c", "a", "l", "b", "d", "s"]
        while(True):
            action = (input("Ingrese la acción que desea realizar:\nc: Conectar\na: Atacar\nl: Perder\nb: Construir\nd: Desconectar\ns: Seleccionar\n")).lower()
            while (action not in VALID_ACTION):
                action = input("Ingrese la acción que desea realizar:  ")
            self.handleAction(action)

            self.sendMessage(self.messageToSend.toJSON())
            # Desconectar
            if (action == "d" or action):
                break
            

    # ====== Función Principal ======
    def sendMessage(self, mensaje):
        bytesToSend = str.encode(mensaje)
        self.clientSocket.sendto(bytesToSend, (self.servidor.SERVER_IP, self.servidor.PORT))
        msgFromServer = self.clientSocket.recvfrom(self.servidor.BUFFER_SIZE)
        msg = f"{msgFromServer[0].decode('utf-8')}"
        print(msg)
        return msg
    
    def handleAction(self, action: str):
        # MessageStructure: action, bot, ships, position
        # CONNECCTION
        if (action == "c"):
            inputBot = input("¿Desea jugar contra un bot? (y/n): ").lower()
            while (inputBot != "y" and inputBot != "n"):
                inputBot = input("¿Desea jugar contra un bot? (y/n): ").lower()
            if (inputBot == "y"):   
                self.messageToSend = MessageStructure(action, 1, {}, [])
            else:
                self.messageToSend = MessageStructure(action, 0, {}, [])
            return
        
        # ATTACK
        elif (action == "a"):
            x = getCoord("x"); y = getCoord("y")
            self.messageToSend = MessageStructure(action, 0, {}, [x, y])
            return
        
        # BUILD
        elif (action == "b"):
            inputShip =getShip(); x = getCoord("x"); y = getCoord("y")
            inputOrientation = getOrientation()
            self.messageToSend = MessageStructure(action, 0, {inputShip: [x, y, inputOrientation]}, [])
            return
        
        # SELECT # // ???
        elif (action == "s"):
            self.messageToSend = MessageStructure(action, 0, {}, [])
            return

        # DISCONNECT or LOSE
        elif (action == "d" or action == "l"):
            self.messageToSend = MessageStructure(action, 0, {}, [])
            return

        pass

def getCoord(inputCoord: str):
    inputValue = input(f"Ingrese la coordenada {inputCoord}: ")
    while (inputValue.isnumeric() == False or int(inputValue) < 0 or int(inputValue) > SIZE_TABLERO):
        inputValue = input(f"Ingrese la coordenada {inputCoord} (Debe ser un número entre 0 y {SIZE_TABLERO}) : ")
    return int(inputValue)

def getShip():
    inputShip = input("¿Qué barco desea construir? (p/b/s)\np: Patito(1x1)\nb: Buque(2x1)\ns: Submarino(3x1)\n").lower()
    while (inputShip != "p" and inputShip != "b" and inputShip != "s"):
        inputShip = input("¿Qué barco desea construir? (p/b/s): ").lower()
    return inputShip

def getOrientation():
    inputOrientation = input("¿Qué orientación desea? (v/h): ").lower()
    while (inputOrientation != "v" and inputOrientation != "h"):
        inputOrientation = input("¿Qué orientación desea? (v/h): ").lower()
    if (inputOrientation == "v"):
        return 0
    return 1

def __main__():
    pass

if __name__ == "__main__":
    __main__()
    