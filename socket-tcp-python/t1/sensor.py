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
from messages import *

import socket
from messages import *
from time import sleep


HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta


#lista de cada log inserido
infologs = []
#lista de logs
logs = []


# Funcao de envio de da mensagem
def sendMsg (socket, msg):
	print ("Mensagem a ser enviada: ", msg)
	socket.send (msg)

# Main
def main():
	#id da lista logs
	contador = 1
	######### Inicio do programa
	# Cria o socket do cliente
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	dest = (HOST, PORT) # Forma a tupla de host, porta
	tcp.connect(dest) # Estabelece a conexao


	#---------------- inicio comunicação com o servidor  --------------
	msg_inicial = "3"  #Identificador do tipo 3 
	msg_inicial = msg_inicial.encode('UTF-8') 
	tcp.send (msg_inicial) 	

	#Recebe a lista de ambientes cadastrados do servidor
	print()
	msg = tcp.recv(1024)		
	msg = msg.decode('UTF-8')	
	print (dest, msg)
	print()

	#-------------------------------------------------------------------

	######### MENU INICIAL CLIENTE SENSOR
	print()
	print ('Para sair use CTRL+X\n')
	print()

	print("####MENU INICIAL##### \n")
	print("Digite: \n")
	print("1 - Listar ambientes e Visualizar banco de dados no servidor")
	print("2 - Detecção do sensor de presença")
	print("3 - Lista de LOgs")


	cmd = input("Digite qual mensagem você deseja enviar (1, 2 ou 3):")
	while cmd != '\x18':
		if int(cmd) == 1:
			######### Mostra lista ambientes retornada
			print (dest, msg)
			######### Cria e envia uma mensagem para banco
			banco = 1
			msg1 = MessageType1()
			sendMsg(tcp, msg1.pack(banco))


			idlog = f"V{str(contador)}"
			infologs.append(idlog)
			infologs.append("View BD")
			logs.append(infologs[:])
			infologs.clear()
			contador = contador + 1

		if int(cmd) == 2:
			######### Cria e envia uma mensagem do tipo 2
			print("Escolha o ambiente que o sensor detectou presença ")
			dispositivo = 2 #por causa do indice da lista 
			ambiente = input("ID: ")
			ambiente = int(ambiente)
			valor = "1"
			
			msg2 = MessageType2()
			sendMsg(tcp, msg2.pack(dispositivo,ambiente,valor))



			idlog = f"S{str(contador)}"
			infologs.append(idlog)
			infologs.append("Send Data Lamp")
			logs.append(infologs[:])
			infologs.clear()
			contador = contador + 1


		if int(cmd) == 3:
			######### Mostra o registro de logs do clientee	
			print("===========LISTA DE LOGS=============")
			for i in logs:
				print(f'ID: {i[0]}||{i[1]}')

			idlog = f"R{str(contador)}"
			infologs.append(idlog)
			infologs.append("List Log")
			logs.append(infologs[:])
			infologs.clear()
			contador = contador + 1


		cmd = input("Digite qual mensagem você deseja enviar: ")

	tcp.close()

main()
