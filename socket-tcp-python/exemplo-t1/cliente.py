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
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	dest = (HOST, PORT)
	tcp.connect(dest)

	######### Envia uma mensagem
	print ('Para sair use CTRL+X\n')
	cmd = input("Digite qual mensagem você deseja enviar (1 ou 2): ")
	while cmd != '\x18':
		if int(cmd) == 1:
			######### Cria e envia uma mensagem do tipo 1
			login = "Cristina"
			senha = "123"
			msg1 = MessageType1()
			sendMsg(tcp, msg1.pack(login,senha))

		if int(cmd) == 2:
			######### Cria e envia uma mensagem do tipo 2
			statusCode = 1
			statusMsg = "Usuario autenticado"
			token = "njksbnkjsfbvfbl"
			msg2 = MessageType2()
			# Enviando mensagens duplicadas apenas 
			# para testar que o tratamento está
			#correto do lado servidor
			sendMsg(tcp, msg2.pack(statusCode, statusMsg, token))
			sendMsg(tcp, msg2.pack(statusCode+1, statusMsg, token))
			sendMsg(tcp, msg2.pack(statusCode+2, statusMsg, token))

		cmd = input("Digite qual mensagem você deseja enviar: ")

	tcp.close()

main()
