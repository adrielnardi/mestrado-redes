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
    login = None # String de ate 10 bytes
    senha = None # String de ate 6 bytes

    def __init__(self):
        self.code = 1
        self.length = 20 # 4+10+6
        self.msgtype = "Auth Request"

    def data(self):
        if(self.login != None and self.senha != None):
            return f"{self.code}, {self.login.decode()}, {self.senha.decode()}"
        else:
            return "Mensagem não inicializada"

    # ! network (= big-endian)
    # I unsigned int integer 4 bytes
    # H unsigned short integer 2  bytes
    # h short integer 2  bytes
    # s char[] bytes
    # Funcao de empacotamento de mensagem
    def pack(self, login, senha):
        self.login = login.encode()   
        self.senha = senha.encode()
        msg = struct.pack('!I10s6s', self.code, self.login, self.senha)
        return msg

    def unpack(self, msg):
        code, self.login, self.senha = struct.unpack('!I10s6s', msg)


class MessageType2(Message):

    #Campos da mensagem
    statusCode = None # inteiro de 4 bytes sem sinal
    statusMsg = None # String de ate 20 bytes
    token = None # String de ate 20 bytes

    def __init__(self):
        self.code = 2
        self.length = 48 # 4+4+20+20
        self.msgtype = "Auth Reply"

    def data(self):
        if(self.statusCode != None and self.statusMsg != None):
            return f"{self.code}, {self.statusCode}, {self.statusMsg.decode()}, {self.token.decode()}"
        else:
            return "Mensagem não inicializada"        

    # ! network (= big-endian)
    # I unsigned int integer 4 bytes
    # H unsigned short integer 2  bytes
    # h short integer 2  bytes
    # s char[] bytes
    # Funcao de empacotamento de mensagem
    def pack(self, statusCode, statusMsg, token):
        self.statusCode = statusCode   
        self.statusMsg = statusMsg.encode()
        self.token = token.encode()
        msg = struct.pack('!II20s20s', self.code, self.statusCode, self.statusMsg, self.token)
        return msg

    def unpack(self, msg):
        code, self.statusCode, self.statusMsg, self.token = struct.unpack('!II20s20s', msg)

