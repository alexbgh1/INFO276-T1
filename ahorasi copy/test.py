import random
from constants import SHIPS, SHIPS_SIZE, SIZE_TABLERO

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

def shipsToCoords(ships):
    shipsCoords = []
    for ship in SHIPS:
        shipInfo = ships[ship]
        shipCoords = shipXYOToCoords(shipInfo[0], shipInfo[1], shipInfo[2], SHIPS_SIZE[ship] )
        for shipCoord in shipCoords:
            shipsCoords.append(shipCoord)
    return shipsCoords

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
    
 



b = Bot()


# import socket

# # Create a UDP socket
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# # Set up the server address
# # servidor = Servidor("172.20.33.241", 20002, BUFFER_SIZE)

# # server_address = ('172.20.33.241', 8255)
# server_address = ('172.20.57.191', 8255)

# # Send data to the server
# message = b"www.poroto.com"
# client_socket.sendto(message, server_address)

# # Receive a response from the server
# buffer_size = 1024
# print("res, sv")
# response, server_address = client_socket.recvfrom(buffer_size)

# # Print the server's response
# print("Server response:", response.decode())

# # Close the socket
# client_socket.close()