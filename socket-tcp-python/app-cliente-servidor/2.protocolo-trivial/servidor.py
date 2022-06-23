import socket
HOST = ''              # Endereco IP do Servidor e o endereco atual do computador
PORT = 5000            # Porta que o Servidor na maquina 
# Cria o socket do servidor
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT) # Forma a tupla de host, porta

tcp.bind(orig)		# Solicita ao S.O. acesso exclusivo a porta 5000
tcp.listen(10)		# Entra no modo de escuta

while True:
    con, cliente = tcp.accept() # Aceita conexao do cliente
    print ('Concetado por', cliente)

#------- inicio do protocolo --------------
    msg = con.recv(1024)		
    msg = msg.decode('UTF-8')	
    print (cliente, msg)
 
    msg_inicial = "Bom dia Cliente!"
    msg_inicial = msg_inicial.encode('UTF-8')
    con.send (msg_inicial)   
    

    while True:
        msg = con.recv(1024)		# Recebe mensagem
        msg = msg.decode('UTF-8')	# Decodifica a mensagem
        if not msg: break
        print (cliente, msg)

#---------------- fim do protocolo --------------

    print ('Finalizando conexao do cliente', cliente)
    con.close()		# fecha a conexao com o cliente
