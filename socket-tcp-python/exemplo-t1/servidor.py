import socket
import _thread
from messages import *

HOST = ''              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
BUFFERSIZE = 1024

def recvMsg (socket, cliente):
	try:
		# Ler: https://newbedev.com/python-socket-receive-incoming-packets-always-have-a-different-size
		buffer = socket.recv(BUFFERSIZE)
		print("######################################")
		print ("Buffer: ", cliente, ": ", buffer)

		while True:

			#Ler: https://stackoverflow.com/questions/20024490/how-to-split-a-byte-string-into-separate-bytes-in-python/20024864
			codeData = buffer[:4] #O código está nos 4 primeiros bytes
			#Ler: https://docs.python.org/3/library/struct.html
			code, = struct.unpack('!I', codeData)
			print("######################################")
			print ("Código da mensagem recebida: ", cliente, ": ", code)    	

			if code == 1:
				msg1 = MessageType1()
				print("Descrição: ", cliente, ": ", msg1.description())
				length = msg1.length
				msg = buffer[:length]
				buffer = buffer[length:]
				msg1.unpack(msg)
				print("Mensagem decodificada: ", cliente, ": ", msg1.data())
				print("######################################")
			elif code == 2:
				msg2 = MessageType2()
				print("Descrição: ", cliente, ": ", msg2.description())
				length = msg2.length
				msg = buffer[:length]
				buffer = buffer[length:]
				msg2.unpack(msg)
				print("Mensagem decodificada: ", cliente, ": ", msg2.data())
				print("######################################")

			if len(buffer) == 0:
				print("Todo o buffer foi lido")
				break				
		
		return msg

	except:
		return None

def conectado(con, cliente):
	print("Conectado ao cliente: ", cliente)	
	while True:
		msg = recvMsg(con, cliente)
		if not msg: break
	print("Cliente desconectado: ", cliente)
	_thread.exit()

# Main
def main():
	### Inicio da execucao do programa
	print("O Servidor foi iniciado")
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	orig = (HOST, PORT)
	tcp.bind(orig)
	tcp.listen(1)
	while True:
		con, cliente = tcp.accept()
		#Ler: https://realpython.com/intro-to-python-threading/
		_thread.start_new_thread(conectado, tuple([con, cliente]))

	tcp.close()

main()