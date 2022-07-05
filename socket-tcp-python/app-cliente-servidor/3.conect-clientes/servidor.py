import socket
HOST = ''              # Endereco IP do Servidor e o endereco atual do computador
PORT = 5000            # Porta que o Servidor na maquina 
# Cria o socket do servidor
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT) # Forma a tupla de host, porta

tcp.bind(orig)		# Solicita ao S.O. acesso exclusivo a porta 5000
tcp.listen(10)		# Entra no modo de escuta

while True:
#------- Conectar o cliente 1 --------------
    con1, cliente1 = tcp.accept() # Aceita conexao do cliente
    print ('Concetado por', cliente1)

    msg = con1.recv(1024)		
    msg = msg.decode('UTF-8')	
    print (cliente1, msg)
 
    msg_inicial = "Bom dia!"
    msg_inicial = msg_inicial.encode('UTF-8')
    con1.send (msg_inicial)   
    
    
#------- Conectar o cliente 2 --------------
    con2, cliente2 = tcp.accept() # Aceita conexao do cliente
    print ('Concetado por', cliente2)

    msg = con2.recv(1024)		
    msg = msg.decode('UTF-8')	
    print (cliente2, msg)
 
    msg_inicial = "Bom dia!"
    msg_inicial = msg_inicial.encode('UTF-8')
    con2.send (msg_inicial)   
    

    while True:
        msg = con1.recv(1024)		# Recebe mensagem cliente 1        
        if not msg: break
        con2.send (msg)	    		# Envia a mensagem para o cliente 2
        
        msg = con2.recv(1024)		# Recebe mensagem cliente 2       
        if not msg: break
        con1.send (msg)	    		# Envia a mensagem para o cliente 1

#---------------- fim do protocolo --------------

    print ('Finalizando conexao do cliente', cliente1)
    con1.close()		# fecha a conexao com o cliente
    
    print ('Finalizando conexao do cliente', cliente2)
    con2.close()		# fecha a conexao com o cliente
