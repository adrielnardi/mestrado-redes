import socket
HOST = '127.0.0.1'     # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
# Cria o socket do cliente
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT) # Forma a tupla de host, porta
tcp.connect(dest)	# Estabelece a conexao

print ('Para sair use CTRL+X\n')
msg = input()
while msg != '\x18':
    msg = msg.encode('UTF-8') 	# Codifica a mensagem para UTF-8
    tcp.send (msg) 				# Codifica a mensagem para UTF-8
    msg = input()
tcp.close()	# fecha a conexao com o servidor