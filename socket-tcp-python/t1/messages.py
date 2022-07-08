import struct

#Ler: https://realpython.com/python3-object-oriented-programming/

class Message():
    code = None # inteiro de 4 bytes sem sinal
    length = None # quantidade de bytes da mensagem
    msgtype = None # tipo da mensagem

    def __init__(self):
        self.code = 0
        self.msgtype = ""
        self.length = 0

    def length(self):
        return self.length

    def description(self):
        return f"Código: {self.code} - Tipo: {self.msgtype} - Tamanho: {self.length}"

    def data(self):
        pass

    def unpack(self):
        pass


class MessageType1(Message):

    #Campos da mensagem
    banco = None # inteiro de 4 bytes sem sinal

    def __init__(self):
        self.code = 1
        self.length = 8 # 4+4
        self.msgtype = "View BD"

    def data(self):
        if(self.banco != None ):
            return f"{self.code}, {self.banco}"
        else:
            return "Mensagem não inicializada"

    # ! network (= big-endian)
    # I unsigned int integer 4 bytes
    # I unsigned int integer 4 bytes
    # Funcao de empacotamento de mensagem
    def pack(self, banco):
        self.banco = banco 
        msg = struct.pack('!II', self.code, self.banco)
        return msg

    def unpack(self, msg):
        code, self.banco = struct.unpack('!II', msg)


class MessageType2(Message):

    #Campos da mensagem
    dispositivo = None # inteiro de 4 bytes sem sinal
    ambiente = None #  inteiro de 4 bytes sem sinal
    valor = None # String de ate 10 bytes

    def __init__(self):
        self.code = 2
        self.length = 22 # 4+4+4+10
        self.msgtype = "Send Data"

    def data(self):
        if(self.dispositivo != None and self.ambiente != None and self.valor != None):
            return f"{self.code}, {self.dispositivo}, {self.ambiente}, {self.valor.decode()}"
        else:
            return "Mensagem não inicializada"        

    # ! network (= big-endian)
    # I unsigned int integer 4 bytes
    # H unsigned short integer 2  bytes
    # h short integer 2  bytes
    # s char[] bytes
    # Funcao de empacotamento de mensagem
    def pack(self, dispositivo, ambiente, valor):
        self.dispositivo = dispositivo   
        self.ambiente = ambiente
        self.valor = valor.encode()
        msg = struct.pack('!III10s', self.code, self.dispositivo, self.ambiente, self.valor)
        return msg

    def unpack(self, msg):
        code, self.dispositivo, self.ambiente, self.valor = struct.unpack('!III10s', msg)