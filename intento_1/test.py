class Coordenada:
    def __init__(self, x, y):
        self.x = x # columna
        self.y = y # fila

class Barco:
    def __init__ (self, largo, estado, vertical):
        self.largo = largo
        self.estado = estado # true = vivo, false = hundido
        self.vertical = vertical # true = vertical, false = horizontal
        self.coordenada = []

    def recibirAtaque(self, coordenada: Coordenada):
        # TODO: void
        pass
    def hundir(self):
        # TODO: void
        pass

class Tablero:
    def __init__(self, casillas):
        self.casillas = casillas
        self.barcos = []

    def imprimirTableroString(self):
        tableroSTR = ""
        for i in range(20):
            tableroSTR += str(i) + "\t"
        tableroSTR += "\n"
        for fila in range(len(self.casillas)):
            tableroSTR += str(fila) + "\t"
            for columna in range(len(self.casillas[fila])):
                tableroSTR += self.casillas[fila][columna] + "\t"
            tableroSTR += "\n"
        return tableroSTR

    def imprimirTablero(self):
        # Extra +1 para el número de la columna, y +1 para el número de la fila
        print("\t", end="")
        for i in range(20):
            print(i, end="\t")
        print()
        for fila in range(len(self.casillas)):
            print(fila, end=" \t")
            for columna in range(len(self.casillas[fila])):
                print(self.casillas[fila][columna], end="\t")
            print()

    def colocarBarco(self, barco: Barco, coordenada: Coordenada):
        # TODO: boolean -> true si se pudo colocar, false si no
        # Validamos que no se salga del tablero
        if barco.vertical:
            if ((coordenada.y + barco.largo) > 20):
                return False
        else:
            if ((coordenada.x + barco.largo) > 20):
                return False
            
        # Validamos que no se choque con otro barco
        for i in range(barco.largo):
            if barco.vertical:
                if self.casillas[coordenada.y+i][coordenada.x] == "B":
                    return False
            else:
                if self.casillas[coordenada.y][coordenada.x+i] == "B":
                    return False
                
        # Si se pudo se agrega a los barcos, también se modifica barco y el tablero
        barco.coordenada.append(coordenada)
        for i in range(barco.largo):
            if barco.vertical:
                self.casillas[coordenada.y+i][coordenada.x] = "B"
            else:
                self.casillas[coordenada.y][coordenada.x+i] = "B"

        self.barcos.append(barco)
        return True
    
    def realizarAtaque(self, coordenada: Coordenada):
        # TODO: boolean -> true si se le dio a un barco, false si no
        pass


# casillas = 20x20 
# 'X' como casilla vacía
# 'B' = barco
# 'A' = ataque
# 'H' = hundido
casillas = [ ["_" for i in range(20)] for j in range(20) ]
tablero = Tablero(casillas)
tablero.imprimirTablero()

# Se colocaran 3 barcos
for i in range(3):
    # Validamos x sea un número entre 0 y 19
    barco = Barco(i+1, True, False)
    puesto = False
    while not puesto:
        x = input("Ingrese la coordenada x del barco "+str(i+1)+": ")
        while x.isdigit() == False or int(x) < 0 or int(x) > 19:
            x = input("Ingrese la coordenada x del barco "+str(i+1)+": ")

        # Validamos y sea un número entre 0 y 19
        y = input("Ingrese la coordenada y del barco "+str(i+1)+": ")
        while y.isdigit() == False or int(y) < 0 or int(y) > 19:
            y = input("Ingrese la coordenada y del barco "+str(i+1)+": ")

        # Posición vertical u horizontal
        vertical = input("Ingrese la orientación del barco "+str(i+1)+" (V/H): ")
        while vertical not in ["V", "H"]:
            vertical = input("Ingrese la orientación del barco "+str(i+1)+" (V/H): ")

        barco.vertical = vertical == "V"

        x = int(x);y = int(y)
        coordenada = Coordenada(x, y)
        puesto = tablero.colocarBarco(barco, coordenada)
        if not puesto:
            print("No se pudo colocar el barco en esa posición")

    tablero.imprimirTablero()

jugando = True
while jugando:
    # Realizar ataque
    x = input("Ingrese la coordenada x del ataque: ")
    while x.isdigit() == False or int(x) < 0 or int(x) > 19:
        x = input("Ingrese la coordenada x del ataque: ")

    # Validamos y sea un número entre 0 y 19
    y = input("Ingrese la coordenada y del ataque: ")
    while y.isdigit() == False or int(y) < 0 or int(y) > 19:
        y = input("Ingrese la coordenada y del ataque: ")

    x = int(x);y = int(y)
    coordenada = Coordenada(x, y)
    tablero.realizarAtaque(coordenada)
    tablero.imprimirTablero()

    # Validar si ganó