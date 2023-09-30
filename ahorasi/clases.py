import socket
import json
# importar constantes desde constants.py
from constants import *

class Barco:
    def __init__ (self, largo, estado, vertical):
        self.largo = largo
        self.estado = estado # true = vivo, false = hundido
        self.vertical = vertical # true = vertical, false = horizontal
        self.coordenada = []

class Response:
    def __init__(self, action, status, position: []):
        self.action = action
        self.status = status # 0 = false, 1 = true
        self.position = position
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
# Ships: {p: [x, y, orientation], b: [x, y, orientation], s: [x, y, orientation]}

class Bot:
    def __init__(self, ships, progress, lives):
        self.ships = ships
        self.progress = progress
        self.lives = lives

class Usuario:
    def __init__(self, bot, ships, progress):
        self.bot = bot
        self.againstBot = False
        self.ships = ships
        self.progress = progress

    def printUsuario(self):
        print("Bot: ", self.bot)
        print("AgainstBot: ", self.againstBot)
        print("Ships: ", self.ships)
        print("Progress: ", self.progress)

class Servidor:
    def __init__(self, SERVER_IP, PORT, BUFFER_SIZE):
        self.SERVER_IP = SERVER_IP
        self.PORT = PORT
        self.BUFFER_SIZE = BUFFER_SIZE
        self.serverSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.tablero = []
        self.usuarios = {}

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
        while (True):
            # Aceptar una nueva conexión
            message, address = self.recibirMSG(); messageJSON = json.loads(message);

            # === ACTION ===
            response = self.handleMessageJSON(messageJSON, address)
            if (address in self.usuarios):
                self.usuarios[address].printUsuario()
            print("\nUsuarios activos: ", self.usuarios)


            # === SEND RESPONSE ===
            self.serverSocket.sendto(str.encode(response.toJSON()), address)

    def handleMessageJSON(self, messageJSON: dict, address: tuple):
        # MessageStructure: action, bot, ships, position.
        if (address in self.usuarios): # Validamos que el usuario exista y que la acción sea válida
            validActions = validateProgress(self.usuarios[address].progress)
            if (messageJSON["action"] not in validActions):
                print("Acción inválida.")
                return Response(messageJSON["action"], 0, [])

        # CONNECCTION
        if (messageJSON["action"] == "c"): # Actual Progress: 1
            return self.handleConnection(messageJSON, address)
        if (messageJSON["action"] == "s"): # Actual Progress: 2
            return self.handleSelect(messageJSON, address)
        if (messageJSON["action"] == "b"): # Actual Progress: 3
            return self.handleBuild(messageJSON, address)
        if (messageJSON["action"] == "d"):
            return self.handleDisconnection(messageJSON, address)
        return Response(messageJSON["action"], 1, [])
        
    def handleBuild(self, messageJSON: dict, address: tuple):
        # {p: [x, y, orientation], b: [x, y, orientation], s: [x, y, orientation]}
        return Response(messageJSON["action"], 1, [])

    def handleSelect(self, messageJSON: dict, address: tuple):
        try:
            if (messageJSON["bot"] == 1):
                self.usuarios[address].bot = Bot({}, 0, 6)
                self.usuarios[address].againstBot = True
                self.usuarios[address].progress = 2
                return Response(messageJSON["action"], 1, [])
            else:
                self.usuarios[address].bot = {}
                self.usuarios[address].againstBot = False
                self.usuarios[address].progress = 2
                return Response(messageJSON["action"], 1, [])
        except:
            try:
                self.usuarios[address].progress = 1
            except:
                Response(messageJSON["action"], 0, [])
            return Response(messageJSON["action"], 0, [])
        
    def handleConnection(self, messageJSON: dict, address: tuple):
        # Hay menos de 2 jugadores
        if (len(self.usuarios) < 2):
            self.usuarios[address] = Usuario({}, {}, 1) # Usuario: {bot: {}, ships: {}, progress: 1}
            return Response(messageJSON["action"], 1, [])
        # Hay 2 jugadores o más
        else:
            return Response(messageJSON["action"], 0, [])
        
    def handleDisconnection(self, messageJSON: dict, address: tuple):
        # Si el usuario existe
        if (address in self.usuarios):
            del self.usuarios[address]
            return Response(messageJSON["action"], 1, [])
        # Si el usuario no existe
        else:
            return Response(messageJSON["action"], 0, [])

# ===========================================================================

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
        self.progress = 0
    
    def conectarAServidor(self):
        VALID_ACTION = ["c", "a", "l", "b", "d", "s"]
        print("\nc: Conectar\na: Atacar\nl: Perder\nb: Construir\nd: Desconectar\ns: Seleccionar\n")
        while(True):
            isValid = False
            while (not isValid):
                action = (input(f"Progress:{self.progress}/5 \nIngrese la acción que desea realizar: (c/a/l/b/d/s)")).lower()
                while (action not in VALID_ACTION):
                    action = input("Ingrese la acción que desea realizar:  ")
                isValid = self.handleAction(action)

            # Enviar mensaje
            self.sendMessage(self.messageToSend.toJSON())

            # Recibir mensaje
            msgFromServer = self.receiveMessage()
            # Manejar mensaje
            shouldEnd = self.handleMessageFromServer(msgFromServer)

            # Desconectar
            if (action == "d" or shouldEnd):
                break
            

    # ====== Función Principal ======
    def receiveMessage(self):
        msgFromServer = self.clientSocket.recvfrom(self.servidor.BUFFER_SIZE)
        msgFromServer = msgFromServer[0].decode('utf-8')
        print(msgFromServer)
        return msgFromServer

    def sendMessage(self, mensaje):
        bytesToSend = str.encode(mensaje)
        self.clientSocket.sendto(bytesToSend, (self.servidor.SERVER_IP, self.servidor.PORT))
        pass
    
    def handleMessageFromServer(self, message: str):
        # message: action, status, x, y
        # True : Repeat
        # False: Continue
        msgFromServer = json.loads(message)
        if (msgFromServer["action"] == "d"):
            self.clientSocket.close()
            return True
        
        if (msgFromServer["action"] == "c"): # Paso: 1
            if (msgFromServer["status"]):
                print("Conexión exitosa.")
                return False
            else:
                print("El servidor está lleno o hubo un error.")
                return False
            
        if (msgFromServer["action"] == "s"): # Paso: 2
            if (msgFromServer["status"]):
                print("Mensaje recibido correctamente.")
                return False
            else:
                print("Bot no se pudo seleccionar o hubo un error.") # Retrocede un paso
                self.progress = 1
        return False
    


    def handleAction(self, action: str):
        # MessageStructure: action, bot, ships, position
        # True: Continue, False: Repeat
        validActions = validateProgress(self.progress)
        if (action not in validActions):
            print("Acción inválida.")
            return False

        # CONNECCTION
        if (action == "c"):
            self.progress = 1
            self.messageToSend = MessageStructure(action, 0, {}, [])
            return True
        
        # ATTACK
        elif (action == "a"):
            x = getCoord("x"); y = getCoord("y")
            self.messageToSend = MessageStructure(action, 0, {}, [x, y])
            return True
        
        # BUILD
        elif (action == "b"):
            inputShip = getShip(); x = getCoord("x"); y = getCoord("y")
            inputOrientation = getOrientation()
            self.messageToSend = MessageStructure(action, 0, {inputShip: [x, y, inputOrientation]}, [])
            return True
        
        # SELECT # BOT or NO BOT
        elif (action == "s"):
            inputBot = input("¿Desea jugar contra un bot? (y/n): ").lower()
            while (inputBot != "y" and inputBot != "n"):
                inputBot = input("¿Desea jugar contra un bot? (y/n): ").lower()
            self.progress = 2
            if (inputBot == "y"):   
                self.messageToSend = MessageStructure(action, 1, {}, [])
            else:
                self.messageToSend = MessageStructure(action, 0, {}, [])
            return True

        # DISCONNECT or LOSE
        elif (action == "d" or action == "l"):
            self.messageToSend = MessageStructure(action, 0, {}, [])
            return True

        pass
    
    def disconnect(self):
        self.messageToSend = MessageStructure("d", 0, {}, [])
        self.sendMessage(self.messageToSend.toJSON())
        self.clientSocket.close()
        pass

def validateProgress(progress):
    if (progress == 0):
        print("Acciones que puede realizar: c")
        return ["c"]
    elif (progress == 1):
        print("Acciones que puede realizar: s, d")
        return ["s", "d"]
    elif (progress == 2):
        print("Acciones que puede realizar: b, d")
        return ["b", "d"]
    return []

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
    