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


# ATENÇÃO !!!
# FOI CRIADO PARA INFORMAR QUE NÃO É DISPOSITIVO SUPORTADO


import socket
from messages import *


HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

# Funcao de envio de da mensagem
def sendMsg (socket, msg):
	print ("Mensagem a ser enviada: ", msg)
	socket.send (msg)

# Main
def main():
	######### Inicio do programa
	# Cria o socket do cliente
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	dest = (HOST, PORT) # Forma a tupla de host, porta
	tcp.connect(dest) # Estabelece a conexao


	#---------------- inicio comunicação com o servidor  --------------
	msg_inicial = "4"  #Identificador do tipo 4 
	msg_inicial = msg_inicial.encode('UTF-8') 
	tcp.send (msg_inicial) 	
	msg = tcp.recv(1024)		
	msg = msg.decode('UTF-8')	
	print("Dispositivo não é suportado pelo servidor")

	#-------------------------------------------------------------------

	tcp.close()


main()
