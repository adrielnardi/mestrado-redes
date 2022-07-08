###################################################################################
#                                                                                 #
# Trabalho 1 - Programaçao Socket                                                 #
#                                                                                 #
# Nome: Adriel Monti De Nardi                                                     #
# Matrícula: 20202MPCA0014                                                        #
# Data: 09/05/2022                                                                #
# Disciplina: Rede de Computadores                                                #
#                                                                                 #
###################################################################################

import socket
import _thread
from messages import *

HOST = ''              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
BUFFERSIZE = 1024      # Tamanho do Buffer


listaAmbiente = {
	"1":"Garagem", "2":"Corredor Garagem", 
	"3":"Escada", "4":"Sala",
	"5":"Copa", "6":"Cozinha",
	"7":"Banheiro", "8":"Área de Serviço",
	"9":"Quarto 1", "10":"Quarto 2"
	}


listaDispositivo = {"1":"termômetro", "2":"lâmpada", "3":"sensor de presença"}

bd = [['0',"desligada",'0'],['0',"desligada",'0'],
	  ['0',"desligada",'0'],['0',"desligada",'0'],
	  ['0',"desligada",'0'],['0',"desligada",'0'],
	  ['0',"desligada",'0'],['0',"desligada",'0'],
	  ['0',"desligada",'0'],['0',"desligada",'0']]

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
			#print(bd)    	

			if code == 1:
				msg1 = MessageType1()
				print("Descrição: ", cliente, ": ", msg1.description())
				length = msg1.length
				msg = buffer[:length]
				buffer = buffer[length:]
				msg1.unpack(msg)
				print("Mensagem decodificada: ", cliente, ": ", msg1.data())
				print("######################################")
				print(bd)
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
				separa = msg2.data().split()
				indice1 = separa[1].replace(",","")
				indice2 = separa[2].replace(",","")
				indice3 = separa[3]
				bd[int(indice2)-1][int(indice1)] = indice3
				print(bd)
				print("######################################")

				

			if len(buffer) == 0:
				print("Todo o buffer foi lido")
				break				
		
		return msg

	except:
		return None

def conectado(con, cliente):
	print("Conectado ao cliente: ", cliente)
	#------- inicio da comunicação com os clientes --------------
	
	msg = con.recv(1024)		
	msg = msg.decode('UTF-8')
	if msg == '1':
		print (cliente, f"Dispositivo termômetro suportado ; ID: {msg}")
		print()
	elif msg == '2':
		print(cliente, f"Dispositivo lâmpada suportado ; ID: {msg}" )
		print()
	elif msg == '3':
		print(cliente, f"Dispositivo sensor suportado ; ID: {msg}" )
		print()
	else:
		print(cliente, f"Dispositivo não suportado ; ID: {msg}")
	
	msg_inicial = str(listaAmbiente)
	msg_inicial = msg_inicial.encode('UTF-8')
	con.send (msg_inicial)   
	
	#-------------------------------------------------------------
	while True:
		msg = recvMsg(con, cliente)
		if not msg: break
	print("Cliente desconectado: ", cliente)
	_thread.exit()

# Main
def main():
	### Inicio da execucao do programa
	print("O Servidor Smart Home Devices foi iniciado")
	print()

	#Mostra a Lista de ambientes da casa
	print(f'Lista de ambientes da casa: {listaAmbiente}')
	print()

	#Mostra a Lista de dispositivos suportados
	print(f'Lista de dispositivos suportados: {listaDispositivo}')
	print()

	# Cria o socket do servidor
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	orig = (HOST, PORT) # Forma a tupla de host, porta
	tcp.bind(orig) # Solicita ao S.O. acesso exclusivo a porta
	tcp.listen(1) # Entra no modo de escuta


	while True:
		con, cliente = tcp.accept()

		#Ler: https://realpython.com/intro-to-python-threading/
		_thread.start_new_thread(conectado, tuple([con, cliente]))

		
	tcp.close()

main()
