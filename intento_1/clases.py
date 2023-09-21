import socket
import random

SIZE_TABLERO = 5
FONDO_MAPA = "~"

class Coordenada:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Jugador:
    def __init__(self, nombre):
        self.nombre = nombre
    def realizarAccion(coordenada: Coordenada):
        # TODO: void
        pass

class Barco:
    def __init__ (self, largo, estado, vertical):
        self.largo = largo
        self.estado = estado # true = vivo, false = hundido
        self.vertical = vertical # true = vertical, false = horizontal
        self.coordenada = []

class Tablero:
    def __init__(self, casillas):
        self.casillas = casillas
        self.barcos = []

    def imprimirTableroString(self):
        tableroSTR = "\t"
        for i in range(SIZE_TABLERO):
            tableroSTR += str(i) + "\t"
        tableroSTR += "\n"
        for fila in range(len(self.casillas)):
            tableroSTR += str(fila) + "\t"
            for columna in range(len(self.casillas[fila])):
                tableroSTR += self.casillas[fila][columna] + "\t"
            tableroSTR += "\n"
        return tableroSTR
    
    def imprimirTableroStringOculto(self):
        tableroSTR = "\t"
        for i in range(SIZE_TABLERO):
            tableroSTR += str(i) + "\t"
        tableroSTR += "\n"
        for fila in range(len(self.casillas)):
            tableroSTR += str(fila) + "\t"
            for columna in range(len(self.casillas[fila])):
                # Si es un barco, no se muestra
                if self.casillas[fila][columna] == "B":
                    tableroSTR += FONDO_MAPA + "\t"
                else:
                    tableroSTR += self.casillas[fila][columna] + "\t"
            tableroSTR += "\n"
        return tableroSTR

    def imprimirTablero(self):
        # Extra +1 para el número de la columna, y +1 para el número de la fila
        print("\t", end="")
        for i in range(SIZE_TABLERO):
            print(i, end="\t")
        print()
        for fila in range(len(self.casillas)):
            print(fila, end=" \t")
            for columna in range(len(self.casillas[fila])):
                print(self.casillas[fila][columna], end="\t")
            print()

    def revisarBarco(self, barco: Barco):
        # Revisamos integridad del barco
        # True: sigue con vida, False: hundido
        for coordenada in barco.coordenada:
            if self.casillas[coordenada.y][coordenada.x] == "B": # El barco tiene una coordenada que no ha sido atacada
                barco.estado = True
                return 
        barco.estado = False
        return 
    
    def revisarBarcos(self):
        for barco in self.barcos:
            if barco.estado: # Si hay un barco vivo, no se ha ganado
                return False
        return True


    
    def colocarBarco(self, barco: Barco, coordenada: Coordenada):
        # TODO: boolean -> true si se pudo colocar, false si no
        # Validamos que no se salga del tablero
        print("Colocando barco", barco.largo, barco.vertical)
        if barco.vertical:
            if ((coordenada.y + barco.largo) > SIZE_TABLERO):
                print("Y: No se pudo colocar, se salió del tablero")
                return False
        else:
            if ((coordenada.x + barco.largo) > SIZE_TABLERO):
                print("X: No se pudo colocar, se salió del tablero")
                return False
            
        # Validamos que no se choque con otro barco
        for i in range(barco.largo):
            if barco.vertical:
                if self.casillas[coordenada.y+i][coordenada.x] == "B":
                    print("X: No se pudo colocar, se chocó con otro barco")
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

        # Si le dio al "mar" (fondo del mapa)
        if self.casillas[coordenada.y][coordenada.x] == FONDO_MAPA:
            self.casillas[coordenada.y][coordenada.x] = "*"
            return False
        
        # Si le dio a un barco:
        if self.casillas[coordenada.y][coordenada.x] == "B":
            self.casillas[coordenada.y][coordenada.x] = "H"
            return True
        return False


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
        msgFromServer = "Hello UDP Client"
        bytesToSend = str.encode(msgFromServer)

        while (True):
            # Aceptar una nueva conexión
            # message, address = self.recibirMSG()
            bytesAddressPair = self.serverSocket.recvfrom(self.BUFFER_SIZE)
            message = bytesAddressPair[0]
            message = message.decode("utf-8")
            address = bytesAddressPair[1]
        
            # NOMBRE= -> Agregar usuario
            if message.startswith("NOMBRE="):
                self.validarUsuario(message, address)
                print(self.usuarios)
            
            # DESCONECTAR= -> Eliminar usuario
            elif (message.startswith("DESCONECTAR;")):
                self.desconectarUsuario(message, address)
                print(self.usuarios)

            elif (message.startswith("JUGAR;")):
                self.iniciarPartida(address)

            else:
                print(f"{self.usuarios[address]}: {message}")
                self.serverSocket.sendto(bytesToSend, address)

    def iniciarPartida(self, address):
        # Creamos 1 tablero para un "bot" y 1 tablero para el jugador
        self.tablero = [self.iniciarTablero(), self.iniciarTablero()]
        tableroSTR = self.tablero[0].imprimirTableroString()
        poniendo_barcos = True
        self.serverSocket.sendto(str.encode("Iniciando partida... Posiciona tus barcos diciendo\nTendras 3 barcos: 1x1, 2x1, 3x1 \nCOORDENADA=X,Y,V/H\n"+tableroSTR), address)

        msgFromServer = "Hello UDP Client"
        bytesToSend = str.encode(msgFromServer)
        usuario_disconnect = False
        finalMsg = ""
        jugando = True
        while(jugando):
            if (poniendo_barcos):
                print("Poniendo barcos")
                for i in range(3):
                    if usuario_disconnect:
                        break

                    print("Pon barco", i+1)
                    barco = Barco(i+1, True, False)
                    puesto = False
                    while not puesto:
                        bytesAddressPair = self.serverSocket.recvfrom(self.BUFFER_SIZE)
                        message = bytesAddressPair[0]
                        message = message.decode("utf-8")
                        address = bytesAddressPair[1]
                        if (message.startswith("DESCONECTAR;")):
                            self.desconectarUsuario(message, address)
                            usuario_disconnect = True
                            print(self.usuarios)
                            break

                        if (message.startswith("COORDENADA=")):
                            try:
                                coordenada = message.split("=")[1]
                                coordenada = coordenada.split(",")
                                x = coordenada[0]
                                y = coordenada[1]
                                vertical = coordenada[2]
                                vertical = vertical == "V"
                                
                                barco.vertical = vertical
                                print(f"Barco {i+1}, x: {x}, y: {y}, vertical: {vertical}")
                                puesto = self.tablero[0].colocarBarco(barco, Coordenada(int(x), int(y)))
                                if puesto:
                                    tableroSTR = self.tablero[0].imprimirTableroString()
                                    print(tableroSTR)
                                    msgFromServer = tableroSTR+"\n\nBarco colocado con éxito."
                                    # Colocamos también el barco en el tablero del bot
                                    barcoBOTpuesto = False
                                    while not barcoBOTpuesto:
                                        xBOT = random.randint(0, SIZE_TABLERO-1)
                                        yBOT = random.randint(0, SIZE_TABLERO-1)
                                        verticalBOT = random.choice([True, False])
                                        barcoBOT = Barco(i+1, True, verticalBOT)
                                        barcoBOTpuesto = self.tablero[1].colocarBarco(barcoBOT, Coordenada(int(xBOT), int(yBOT)))
                                    print("Barco bot puesto", i+1)
                                    self.tablero[1].imprimirTablero()
                                    self.serverSocket.sendto(str.encode(msgFromServer), address)
                                else:
                                    self.serverSocket.sendto(str.encode("False;Barco no se pudo colocar."), address)
                            except:
                                self.serverSocket.sendto(str.encode("False;Barco no se pudo colocar. Tu mensaje no fue valido, debe ser: COORDENADA=X,Y,V/H"), address)
                        else:
                            self.serverSocket.sendto(str.encode("False;Barco no se pudo colocar. Tu mensaje no fue valido"), address)
                            
                poniendo_barcos = False
                if usuario_disconnect:
                    break
                # Ataque
                print("Atacando")
                bytesAddressPair = self.serverSocket.recvfrom(self.BUFFER_SIZE)
                message = bytesAddressPair[0]
                message = message.decode("utf-8")
                address = bytesAddressPair[1]
                self.serverSocket.sendto(str.encode("Ahora tienes que atacar"), address)
                while jugando:
                    bytesAddressPair = self.serverSocket.recvfrom(self.BUFFER_SIZE)
                    message = bytesAddressPair[0]
                    message = message.decode("utf-8")
                    address = bytesAddressPair[1]

                    if (message.startswith("DESCONECTAR;")):
                        self.desconectarUsuario(message, address)
                        usuario_disconnect = True
                        print(self.usuarios)
                        break

                    if (message.startswith("COORDENADA=")):
                        try:
                            coordenada = message.split("=")[1]
                            coordenada = coordenada.split(",")
                            x = coordenada[0]
                            y = coordenada[1]
                            self.tablero[1].realizarAtaque(Coordenada(int(x), int(y)))

                            # Ataque del bot
                            xBOT = random.randint(0, SIZE_TABLERO-1); yBOT = random.randint(0, SIZE_TABLERO-1)
                            self.tablero[0].realizarAtaque(Coordenada(int(xBOT), int(yBOT)))

                            tableroSTRUsuario = self.tablero[0].imprimirTableroStringOculto()                            
                            tableroSTRBot = self.tablero[1].imprimirTableroStringOculto()
                            msgFromServer = "Tu\n"+tableroSTRUsuario+"\nBot\n"+tableroSTRBot

                            # Verificamos si el usuario ganó
                            # TODO: Verificar si el usuario ganó
                            # Actualiza el estado de "salud" de los barcos del bot
                            for barco in self.tablero[1].barcos:
                                self.tablero[1].revisarBarco(barco)
                            
                            if self.tablero[1].revisarBarcos():
                                finalMsg = "GANASTE!!!!\n"+tableroSTRUsuario+"\nBot\n"+tableroSTRBot
                                jugando = False
                                break


                            # Verificamos si el bot ganó
                            # TODO: Verificar si el bot ganó
                            # Actualiza el estado de "salud" de los barcos del usuario
                            for barco in self.tablero[0].barcos:
                                self.tablero[0].revisarBarco(barco)
                            
                            if self.tablero[0].revisarBarcos():
                                finalMsg = "Perdiste\n"+tableroSTRUsuario+"\nBot\n"+tableroSTRBot
                                jugando = False
                                break

                            print("Ataque exitoso (bot y usuario)")
                            self.serverSocket.sendto(str.encode(msgFromServer), address)
                        except:
                            self.serverSocket.sendto(str.encode("False;EXCEPT;Ataque no valido, debe ser: COORDENADA=X,Y"), address)
                    else:
                        self.serverSocket.sendto(str.encode("False;Ataque no valido, debe ser: COORDENADA=X,Y"), address)
                print("Terminó la partida")
                # Reset tablero
            break
        
        if usuario_disconnect:
            return
        # Terminó la partida
        self.serverSocket.sendto(str.encode(finalMsg), address)
    
    def iniciarTablero(self):
        casillas = [ [FONDO_MAPA for i in range(SIZE_TABLERO)] for j in range(SIZE_TABLERO) ]
        tablero = Tablero(casillas)
        tablero.imprimirTablero()
        return tablero
    
    def desconectarUsuario(self, mensaje, address):
        if mensaje.startswith("DESCONECTAR;"):
            if self.eliminarUsuario(address):
                self.serverSocket.sendto(str.encode("Usuario eliminado con éxito de la conexión."), address)
            else:
                self.serverSocket.sendto(str.encode("Usuario no existe."), address)


    def eliminarUsuario(self, address):
        # address existe? en self.usuarios?
        if address in self.usuarios:
            del self.usuarios[address]
            return True
        return False
    
    def validarUsuario(self, mensaje, address):
        # Expected: NOMBRE=nombre
        if mensaje.startswith("NOMBRE="):
            nombre = mensaje.split("=")[1]

            # Si hay mas de X usuarios, no se puede agregar
            X = 1
            if len(self.usuarios) >= X:
                self.serverSocket.sendto(str.encode("False;No se pueden agregar más usuarios."), address)
                return

            # Tomaremos el nombre y adress
            if self.agregarUsuario(nombre, address):
                self.serverSocket.sendto(str.encode("True;Usuario agregado con éxito."), address)
            else:
                self.serverSocket.sendto(str.encode("False;Usuario ya existe."), address)
        pass

    def agregarUsuario(self, nombre, address):
        # Si existe, False
        if address in self.usuarios:
            return False
        
        # Si no existe, lo agregamos {(ip,port) = nombre}
        self.usuarios[address] = nombre
        return True


    def finalizarPartida(self):
        # TODO: void
        pass 

class Cliente:
    def __init__ (self, nombre, servidor: Servidor):
        self.nombre = nombre
        self.servidor = servidor
        self.clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def conectarAServidor(self):
        while(True):
            enviarMensaje = input("Ingrese su mensaje: ")
            self.enviarMensaje(enviarMensaje)
        pass

    def listarComandos(self):
        print("HELP; -> Lista los comandos disponibles")
        print("DESCONECTAR; -> Desconecta al usuario del servidor")
        print("JUGAR; -> Inicia el juego")
        pass

    def enviarMensaje(self, mensaje):
        if mensaje.startswith("HELP;"):
            self.listarComandos()
            return
        if mensaje.startswith("DESCONECTAR;"):
            self.desconectar()
            return
        
        bytesToSend = str.encode(mensaje)
        self.clientSocket.sendto(bytesToSend, (self.servidor.SERVER_IP, self.servidor.PORT))
        msgFromServer = self.clientSocket.recvfrom(self.servidor.BUFFER_SIZE)
        msg = "{}".format(msgFromServer[0].decode("utf-8"))
        print(msg)
        pass

    def enviarMensajeInicio(self, mensaje):
        bytesToSend = str.encode(mensaje)
        self.clientSocket.sendto(bytesToSend, (self.servidor.SERVER_IP, self.servidor.PORT))
        msgFromServer = self.clientSocket.recvfrom(self.servidor.BUFFER_SIZE)
        msg = "{}".format(msgFromServer[0].decode("utf-8"))

        msg = msg.split(";")

        # Mensaje
        print(msg[1])

        # Boolean handler
        boolean = msg[0] in ["True", "true", "TRUE"]
        return boolean
    
    def desconectar(self):
        bytesToSend = str.encode("DESCONECTAR;")
        self.clientSocket.sendto(bytesToSend, (self.servidor.SERVER_IP, self.servidor.PORT))
        msgFromServer = self.clientSocket.recvfrom(self.servidor.BUFFER_SIZE)
        msg = "SERVER DICE: {}".format(msgFromServer[0].decode("utf-8"))
        print(msg)
        self.clientSocket.close()
        exit(0)

    def jugarTurno(self):
        # TODO: void
        pass

def __main__():
    pass

if __name__ == "__main__":
    __main__()
    
