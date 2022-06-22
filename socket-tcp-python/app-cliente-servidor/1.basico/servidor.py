import socket
HOST = ''              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
# Cria o socket do servidor
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT) # Forma a tupla de host, porta
tcp.bind(orig)		# Solicita ao S.O. acesso exclusivo a porta
tcp.listen(1)		# Entra no modo de escuta
while True:
    con, cliente = tcp.accept() # Aceita conexao do cliente
    print ('Concetado por', cliente)
    while True:
        msg = con.recv(1024)		# Recebe mensagem
        msg = msg.decode('UTF-8')	# Decodifica a mensagem
        if not msg: break
        print (cliente, msg)
    print ('Finalizando conexao do cliente', cliente)
    con.close()		# fecha a conexao com o cliente