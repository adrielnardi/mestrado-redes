import socket
import struct
import _thread
HOST = ''              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

# Campos da mensagem
idSensor = None
tpSensor = None
vlSensor = None
structsize = 8

# Funcao de recepcao e desempacotamento da mensagem
def myRecv (socket):
	try:	
		msg = socket.recv(structsize)
		print (cliente, msg)
		return struct.unpack('!IHh', msg)
	except:
		return None
	
def conectado(con, cliente):
	idSensor, tpSensor, vlSensor = myRecv(con)
	print (cliente, idSensor, tpSensor, vlSensor)
	print ('Finalizando conexao do cliente', cliente)
	con.close()
	_thread.exit()

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT)
tcp.bind(orig)
tcp.listen(1)
while True:
    con, cliente = tcp.accept()
    _thread.start_new_thread(conectado, tuple([con, cliente]))

tcp.close()