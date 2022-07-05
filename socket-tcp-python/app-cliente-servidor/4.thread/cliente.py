import socket
import struct

HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
# Campos da mensagem
idSensor = 70000
tpSensor = 50000
vlSensor = -169

# Funcao de empacotamento e envio de da mensagem
def mySend (socket, idSensor, tpSensor, vlSensor):
	msg = struct.pack('!IHh', idSensor, tpSensor, vlSensor)
	print (msg)
	socket.send (msg)

######### Inicio do programa	
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)

######### Envia uma mensagem
mySend (tcp, idSensor, tpSensor, vlSensor)

tcp.close()
