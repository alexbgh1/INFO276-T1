import socket
import json
import random
# importar constantes desde constants.py
from constants import *


class Response:
    def __init__(self, action, status, position: [], extra=""):
        self.action = action
        self.status = status # 0 = false, 1 = true
        self.position = position
        self.extra = extra
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
# Ships: {p: [x, y, orientation], b: [x, y, orientation], s: [x, y, orientation]}

class Bot:
    def __init__(self):
        self.ships = self.randomShips()
        self.lives = 6
        self.shipsAsCoords = []

    def randomShips(self):
        # {p: [x, y, orientation], b: [x, y, orientation], s: [x, y, orientation]} # 1x1, 2x1, 3x1
        ships = {"p": [], "b": [], "s": []}
        for ship in SHIPS:
            validShip = False
            while (not validShip):
                x = random.randint(0,SIZE_TABLERO-1); y = random.randint(0,SIZE_TABLERO-1); orientation = random.randint(0,1)
                validShip = validateOrientation(x, y, orientation, SHIPS_SIZE[ship]) and validateOverlap(x, y, orientation, SHIPS_SIZE[ship], ships)
            ships[ship] = [x,y,orientation]
        return ships
    
    def printShips(self):
        print("BOT Ships as Coords: ", self.shipsAsCoords)

class Usuario:
    def __init__(self, bot, ships, shipsAsCoords, progress):
        self.bot = bot
        self.againstBot = False
        self.ships = ships
        self.shipsAsCoords = shipsAsCoords
        self.progress = progress
        self.lives = 6

    def printUsuario(self):
        print("Lives: ", self.lives)
        print("Bot: ", self.bot)
        print("AgainstBot: ", self.againstBot)
        print("Ships: ", self.ships)
        print("Ships As Coords: ", self.shipsAsCoords)


class Servidor:
    def __init__(self, SERVER_IP, PORT, BUFFER_SIZE):
        self.SERVER_IP = SERVER_IP
        self.PORT = PORT
        self.BUFFER_SIZE = BUFFER_SIZE
        self.serverSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.tableros = {} # {address: tablero}
        self.usuarios = {}
        self.turno_actual = None

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
            validResponse = True
            print(message)
            # === CAMBIAR TURNO ===
            if (messageJSON["action"] == "t"):
                # Si solicita turno, no pasamos de turno
                pass
            elif (address in self.usuarios and self.usuarios[address].progress == 3 and not self.usuarios[address].againstBot and self.turno_actual == address):
                # address existe
                # address está en progreso 3
                # address no está contra bot
                # address es el turno actual
                self.handleChangeTurn(address)

            elif (address in self.usuarios and self.usuarios[address].progress == 3 and not self.usuarios[address].againstBot and self.turno_actual != address):
                print("No es tu turno.")
                validResponse = False

            # === ACTION ===
            if (validResponse):
                response = self.handleMessageJSON(messageJSON, address)
            else:
                response = Response(messageJSON["action"], 0, [0,0], "No es tu turno, este ataque no se registró en el Servidor")
            # === PRINT DATA ===
            if (address in self.usuarios):
                self.usuarios[address].printUsuario()
                if (self.usuarios[address].againstBot):
                    self.usuarios[address].bot.printShips()
            print("\nUsuarios activos: ", self.usuarios)



            # === SEND RESPONSE ===
            self.serverSocket.sendto(str.encode(response.toJSON()), address)


    def handleChangeTurn(self, address: tuple):
        # Change Turn self.turno_actual = address
        try:
            enemyAddress = [addr for addr in self.usuarios.keys() if addr != address][0]
            self.turno_actual = enemyAddress
        except:
            self.turno_actual = address
        pass
        
    def handleMessageJSON(self, messageJSON: dict, address: tuple):
        # MessageStructure: action, bot, ships, position.
        if (address in self.usuarios): # Validamos que el usuario exista y que la acción sea válida
            validActions = validateProgress(self.usuarios[address].progress)
            print("Acciones recibidas: ", messageJSON["action"])
            if (messageJSON["action"] not in validActions):
                print("Acción inválida.")
                return Response(messageJSON["action"], 0, [])

        # CONNECCTION
        if (messageJSON["action"] == "c"): # Actual Progress: 0
            return self.handleConnection(messageJSON, address) # 1
        if (messageJSON["action"] == "s"): # Actual Progress: 1
            return self.handleSelect(messageJSON, address) # 2
        if (messageJSON["action"] == "b"): # Actual Progress: 2
            return self.handleBuild(messageJSON, address) # 2
        if (messageJSON["action"] == "a"): # Actual Progress: 3
            return self.handleAttack(messageJSON, address) # 3
        if (messageJSON["action"] == "d"):
            return self.handleDisconnection(messageJSON, address)
        if (messageJSON["action"] == "t"):
            return self.handleTurn(messageJSON, address)
        return Response(messageJSON["action"], 1, [])
    
    def handleTurn(self, messageJSON: dict, address: tuple):
        # Send turn to the player, 1: Turno, 0: No turno
        if (address == self.turno_actual):
            return Response(messageJSON["action"], 1, [], "Es tu turno.")
        else:
            return Response(messageJSON["action"], 0, [], "No es tu turno.")
    
    def handleAttack(self, messageJSON: dict, address: tuple):
        # {x, y}
        # invalid Attack (out of board)
        # In this case a valid response means that the attack hit a ship
        # A invalid response means that the attack missed
        AttackCoords = (messageJSON["position"][0], messageJSON["position"][1])
        # Out of the board
        if (AttackCoords[0] < 0 or AttackCoords[0] >= SIZE_TABLERO or AttackCoords[1] < 0 or AttackCoords[1] >= SIZE_TABLERO):
            return Response(messageJSON["action"], 0, [AttackCoords[0], AttackCoords[1]], "Tiro fuera del tablero.")
        # Player is against bot
        if (self.usuarios[address].againstBot):
            # Simulation Bot Attack
            botAttackCoords = (random.randint(0,SIZE_TABLERO-1), random.randint(0,SIZE_TABLERO-1))
            if (botAttackCoords in self.usuarios[address].shipsAsCoords):
                self.usuarios[address].lives -= 1
                self.usuarios[address].shipsAsCoords.remove(botAttackCoords)
                # ========= BOT WIN =========
                if (self.usuarios[address].lives == 0):
                    self.usuarios[address].progress = 1 # CONECTADO
                    # Reset lives: 
                    self.usuarios[address].lives = 6
                    return Response("l", 1, [botAttackCoords[0], botAttackCoords[1]], "Perdiste contra el bot") # Lose
                else:
                    pass
                    # return Response(messageJSON["action"], 1, [botAttackCoords[0], botAttackCoords[1]])

            # Attack hit
            if (AttackCoords in self.usuarios[address].bot.shipsAsCoords):
                self.usuarios[address].bot.lives -= 1
                self.usuarios[address].bot.shipsAsCoords.remove(AttackCoords)
                # ========= USER WIN =========
                if (self.usuarios[address].bot.lives == 0):
                    self.usuarios[address].progress = 1 # CONECTADO
                    return Response("w", 1, [AttackCoords[0], AttackCoords[1]], "Ganaste contra el bot") # Win
                else:
                    return Response(messageJSON["action"], 1, [AttackCoords[0], AttackCoords[1]], f"Le diste al bot. Bot atacó en {botAttackCoords[0]},{botAttackCoords[1]}. Bot tiene {self.usuarios[address].bot.lives} vidas restantes.")
            # Attack missed
            else:
                return Response(messageJSON["action"], 0, [AttackCoords[0], AttackCoords[1]], f"No le diste al bot. Bot atacó en {botAttackCoords[0]},{botAttackCoords[1]}")
            
        # Player is against player
        else:
            # Attack hit
            playerAddresses = list(self.usuarios.keys())
            # If there is only one player, return invalid attack
            if (len(self.tableros) < 2):
                user = Usuario({}, {"p":[],"b":[],"s":[]}, [] , 1) # Usuario: {bot: {}, ships: {}, progress: 1}
                user.lives = 6; user.ships = {"p": [], "b": [], "s": []}; user.shipsAsCoords = [];
                self.usuarios[address] = user
                return Response("w", 1, [AttackCoords[0], AttackCoords[1]], "Ganaste,No hay suficientes jugadores.")
                # return Response(messageJSON["action"], 0, [AttackCoords[0], AttackCoords[1]], "No hay suficientes jugadores.")
            
            enemyAddress = [addr for addr in playerAddresses if addr != address][0]
            if (AttackCoords in self.tableros[enemyAddress]):
                print("Attack hit")
                self.usuarios[enemyAddress].lives -= 1
                self.usuarios[enemyAddress].shipsAsCoords.remove(AttackCoords)
                self.tableros[enemyAddress].remove(AttackCoords)
                if (self.usuarios[address].lives == 0):
                    user = Usuario({}, {"p":[],"b":[],"s":[]}, [] , 1) # Usuario: {bot: {}, ships: {}, progress: 1}
                    user.lives = 6; user.ships = {"p": [], "b": [], "s": []}; user.shipsAsCoords = [];
                    self.usuarios[address] = user
                    return Response("l", 1, [AttackCoords[0], AttackCoords[1]]) # Lose

                if (self.usuarios[enemyAddress].lives == 0):
                    self.tableros[address] = []
                    user = Usuario({}, {"p":[],"b":[],"s":[]}, [] , 1) # Usuario: {bot: {}, ships: {}, progress: 1}
                    user.lives = 6; user.ships = {"p": [], "b": [], "s": []}; user.shipsAsCoords = [];
                    self.usuarios[address] = user

                    return Response("w", 1, [AttackCoords[0], AttackCoords[1]], "Ganaste") # Win
                # HIT
                else:
                    return Response(messageJSON["action"], 1, [AttackCoords[0], AttackCoords[1]], "Le diste al jugador")
            # Attack missed
            else:
                if (self.usuarios[address].lives == 0):
                    user = Usuario({}, {"p":[],"b":[],"s":[]}, [] , 1) # Usuario: {bot: {}, ships: {}, progress: 1}
                    user.lives = 6; user.ships = {"p": [], "b": [], "s": []}; user.shipsAsCoords = [];
                    self.usuarios[address] = user
                    return Response("l", 1, [AttackCoords[0], AttackCoords[1]], "Perdiste") # Lose
                
                return Response(messageJSON["action"], 0, [AttackCoords[0], AttackCoords[1]], "No le diste al jugador")


    def handleBuild(self, messageJSON: dict, address: tuple):
        # {p: [x, y, orientation], b: [x, y, orientation], s: [x, y, orientation]}
        try:
            # Check if ships are valid
            for ship in SHIPS:
                shipInfo = messageJSON["ships"][ship]
                validShip = validateOrientation(shipInfo[0], shipInfo[1], shipInfo[2], SHIPS_SIZE[ship]) and validateOverlap(shipInfo[0], shipInfo[1], shipInfo[2], SHIPS_SIZE[ship], self.usuarios[address].ships)
                if (not validShip):
                    print("Barco inválido. Overlap u orientación inválida.")
                    self.usuarios[address].ships = {"p": [], "b": [], "s": []}
                    raise Exception("Barco inválido.")
                self.usuarios[address].ships[ship] = shipInfo
                
            # Ships are valid
            self.usuarios[address].ships = messageJSON["ships"]

            if (not self.usuarios[address].againstBot): # Against Player
               self.tableros[address] = shipsToCoords(self.usuarios[address].ships)

            self.usuarios[address].shipsAsCoords = shipsToCoords(self.usuarios[address].ships)
            self.usuarios[address].progress = 3
            self.turno_actual = address
            return Response(messageJSON["action"], 1, [])
        except:
            try:
                self.usuarios[address].progress = 2
            except:
                return Response(messageJSON["action"], 0, [])
            return Response(messageJSON["action"], 0, [])

    def handleSelect(self, messageJSON: dict, address: tuple):
        try:
            if (messageJSON["bot"] == 1):
                bot = Bot()
                bot.shipsAsCoords = shipsToCoords(bot.ships)
                self.usuarios[address].bot = bot
                self.usuarios[address].againstBot = True
                self.usuarios[address].progress = 2
                self.tableros[address] = []
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
            self.usuarios[address] = Usuario({}, {"p":[],"b":[],"s":[]}, [] , 1) # Usuario: {bot: {}, ships: {}, progress: 1}
            return Response(messageJSON["action"], 1, [])
        # Hay 2 jugadores o más
        else:
            return Response(messageJSON["action"], 0, [])
        
    def handleDisconnection(self, messageJSON: dict, address: tuple):
        # Si el usuario existe
        if (address in self.usuarios):
            if (not self.usuarios[address].againstBot):
                try:
                    del self.tableros[address]
                except:
                    pass
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
        self.ships = {"p": [] , "b": [], "s": []}
        self.attacks = []
        self.shipsAsCoords = []
    
    def conectarAServidor(self):
        VALID_ACTION = ["c", "a", "l", "b", "d", "s","t"]
        print("\nc: Conectar\na: Atacar\nl: Perder\nb: Construir\nd: Desconectar\ns: Seleccionar\n")
        while(True):
            isValid = False
            while (not isValid):
                action = (input(f"\nProgress:{self.progress}/3 \nIngrese la acción que desea realizar: \n")).lower()
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
        
        if (msgFromServer["action"] == "c"): # Paso: 1 Conectarse
            if (msgFromServer["status"]):
                print("Conexión exitosa.")
                return False
            else:
                print("El servidor está lleno o hubo un error.")
                return True
            
        if (msgFromServer["action"] == "s"): # Paso: 2 Seleccionar
            if (msgFromServer["status"]):
                # print("Mensaje recibido correctamente.")
                return False
            else:
                print("Bot no se pudo seleccionar o hubo un error.") # Retrocede un paso
                self.progress = 1
        
        if (msgFromServer["action"] == "b"): # Paso: 3 Construir
            if (msgFromServer["status"]):
                # print("Mensaje recibido correctamente.")
                return False
            else:
                print("Barco no se pudo construir o hubo un error.") # Retrocede un paso
                self.progress = 2

        if(msgFromServer["action"] == "t"):
            print("Consultando turno...")
            return False

        if (msgFromServer["action"] == "a"):
            if (msgFromServer["status"]):
                print("Ataque exitoso.")
            else:
                print("Ataque fallido.")
            self.attacks.append((msgFromServer["position"][0], msgFromServer["position"][1], msgFromServer["status"]))
            printBoard(self.attacks)
            return False
        
        if (msgFromServer["action"] == "w"):
            print("Ganaste!!!")
            print("Ganaste!!!")
            print("Ganaste!!!")
            self.resetStats()
        
        if (msgFromServer["action"] == "l"):
            print("Perdiste!!!")
            print("Perdiste!!!")
            print("Perdiste!!!")
            self.resetStats()

        return False
    
    def resetStats(self):
        self.attacks = []
        self.ships = {"p": [] , "b": [], "s": []}
        self.shipsAsCoords = []
        self.lives = 6
        self.progress = 1

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
            shipsDict = {"p": {} , "b": {}, "s": {}}
            for ship in SHIPS:
                isValidShip = False
                while (not isValidShip):
                    shipSize = SHIPS_SIZE[ship]
                    print(f"Construyendo {ship} {shipSize}x1")
                    x = getCoord("x"); y = getCoord("y"); inputOrientation = getOrientation()
                    # First validation: inside board
                    valid_orientation = validateOrientation(x, y, inputOrientation, shipSize)
                    # Second validation: overlapping
                    valid_overlap = validateOverlap(x, y, inputOrientation, shipSize, self.ships)
                    isValidShip = valid_orientation and valid_overlap

                shipsDict[ship] = [x, y, inputOrientation]
                self.ships[ship] = [x,y,inputOrientation]

            self.progress = 3
            self.shipsAsCoords = shipsToCoords(self.ships)
            self.messageToSend = MessageStructure(action, 0, shipsDict, [])
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
        
        # TURN
        elif (action == "t"):
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

def validateOverlap(x, y, orientation, shipSize, selfShips):
    # Examples of selfShips: {"p": [0,0,0] : "b": [] : "s": []} ; # [x,y,orientation]
    # Examples of selfShips: {"p": [0,0,0] : "b": [1,1,0] : "s": []}
    # Examples of selfShips: {"p": [0,0,0] : "b": [1,1,0] : "s": [2,2,1]}
    # Possible ship
    currentCoords = shipXYOToCoords(x,y,orientation,shipSize) # [(x,y),(x1,x2)...]
    for ship in SHIPS:
        shipInformation = selfShips[ship]
        if ((shipInformation == []) or (shipSize == SHIPS_SIZE[ship])):
            pass
        else: 
            newCoords = shipXYOToCoords(shipInformation[0],shipInformation[1], shipInformation[2], SHIPS_SIZE[ship])
            if (overlapped(currentCoords, newCoords)):
                return False
    return True

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
    elif (progress == 3):
        print("Acciones que puede realizar: t, a, d")
        return ["t","a", "d"]
    return []

def overlapped(list_coords_1, list_coords_2):
    for punto1 in list_coords_1:
        for punto2 in list_coords_2:
            if punto1 == punto2:
                return True
    return False

def shipXYOToCoords(x,y,o,shipSize):
    # [3,0,0,1] -> [(0,0), (1,0), (2,0)]
    coords = []
    if (o == 0): # vertical
        for alongY in range(shipSize):
            coords.append((x,y+alongY))
    else:
        for alongX in range(shipSize):
            coords.append((x+alongX, y))
    return coords

def validateOrientation(x, y, orientation, shipSize):
    if (orientation == 0): # Vertical
        if (y + (shipSize-1) >= SIZE_TABLERO): # Out of board (vertical) # ex: y = 4, shipSize = 2, SIZE_TABLERO = 0,1,2,3,4
            print("Barco fuera del tablero en vertical.")
            return False
    else: # Horizontal
        if (x + (shipSize-1) >= SIZE_TABLERO): # Out of board (horizontal), ex: x = 4, shipSize = 2, SIZE_TABLERO = 0,1,2,3,4 
            print("Barco fuera del tablero en horizontal.")
            return False
    return True
        
def getCoord(inputCoord: str):
    inputValue = input(f"Ingrese la coordenada {inputCoord}: ")
    while (inputValue.isnumeric() == False or int(inputValue) < 0 or int(inputValue) >= SIZE_TABLERO):
        inputValue = input(f"Ingrese la coordenada {inputCoord} (Debe ser un número entre 0 y {SIZE_TABLERO-1}) : ")
    return int(inputValue)

def getOrientation():
    inputOrientation = input("¿Qué orientación desea? (v/h): ").lower()
    while (inputOrientation != "v" and inputOrientation != "h"):
        inputOrientation = input("¿Qué orientación desea? (v/h): ").lower()
    if (inputOrientation == "v"):
        return 0
    return 1

def shipsToCoords(ships):
    # {p: [x, y, orientation], b: [x, y, orientation], s: [x, y, orientation]} # 1x1, 2x1, 3x1
    shipsCoords = []
    for ship in SHIPS:
        shipInfo = ships[ship]
        shipCoords = shipXYOToCoords(shipInfo[0], shipInfo[1], shipInfo[2], SHIPS_SIZE[ship] )
        for shipCoord in shipCoords:
            shipsCoords.append(shipCoord)
    return shipsCoords

def printBoard(attacks):
    # atacks: [(x,y, status), (x,y, status)]
    board = [[FONDO_MAPA for i in range(SIZE_TABLERO)] for j in range(SIZE_TABLERO)]
    for attack in attacks:
        if (attack[2] == 1):
            board[attack[1]][attack[0]] = HUNDIDO_MAPA
        else:
            board[attack[1]][attack[0]] = DISPARO_MAPA
    
    for row in board:
        for element in row:
            print(element, end="\t")
        print()
    print()
    pass

    


def __main__():
    pass

if __name__ == "__main__":
    __main__()
    