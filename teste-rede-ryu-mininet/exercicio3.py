#!/usr/bin/python
import sys, getopt
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController
from mininet.cli import CLI
from multiprocessing import Process
from subprocess import Popen
from time import sleep
from os import system
from os.path import exists

class NovaTopologia(Topo):
    def build(self, topologia=[]):
        # Inicializa o dicionário que vai armazenar todos os switches
        switches = {}
        for item in topologia:
            # Cria um novo switch
            swname = 's' + item['host']
            switch = self.addSwitch(swname)
            # Inclui no dicionário
            switches.update( { swname: switch } )
            # Cria um novo host
            host = self.addHost('h' + item['host'])
            # Faz o link entre o host e o switch
            self.addLink(host, switch)
        # Faz uma segunda passagem pela topologia
        for item in topologia:
            # Obtem o objeto do switch
            sworig = 's' + item['host']
            switch_orig = switches[sworig]
            # Passa por todas as conexões do switch
            for conexao in item['conexoes']:
                swdest = 's' + conexao
                switch_dest = switches[swdest]
                # Faz o link entre os switches
                self.addLink(switch_orig, switch_dest)

def executarTopologia(topologia, metodo, filename):
    # Iniciar o controlador
    system('METODO=' + metodo + ' ryu-manager --observe-links Controller3.py &')
    # Cria a nova topologia
    topo = NovaTopologia(topologia)
    # Inicia o mininet
    net = Mininet(topo, controller=RemoteController, autoSetMacs=True)
    net.start()
    # Aguardar a conexao de todos os switches
    net.waitConnected()
    dumpNodeConnections(net.hosts)
    print('Testando a conectividade da rede')
    # Repete o teste de pingAll até que dê 100% de retorno. Demora por causa do STP
    while net.pingAll(timeout=0.1) > 0:
        print('Realizando um novo teste de conectividade')
    # Conseguiu conectar todos os hosts
    print('=====================================')
    print('Todos os nos da rede foram conectados')
    print('=====================================')
    
    # Modo interativo, pode ser desabilitado
    #CLI(net)
    
    # Inicia o processo de monitoramento
    monitor = Process(target=monitor_bwm_ng, args=(metodo + '-' + filename + '.bwm', 1.0))
    monitor.start()
    port = 5001
    data_size = 50000000
    for h in net.hosts:
        # Abre um servidor iperf em cada host
        h.cmd('iperf -s -p %s > /dev/null &' % port)
    for client in net.hosts:
        for server in net.hosts:
            if client != server:
                # abre um cliente iperf em cada host para conectar em todos os outros
                client.cmd('iperf -c %s -p %s -n %d -i 1 -yc > /dev/null &' % (server.IP(), 5001, data_size))
    print('Aguarde o termino do experimento...')
    for c in range(10):
        sleep(10)
        print('%s...' % str(10-c))
    # Fechando as aplicacoes abertas
    system('killall -9 iperf')
    system('killall -9 bwm-ng')
    monitor.terminate()
    # Finaliza o mininet
    net.stop()

def monitor_bwm_ng(fname, interval_sec):
    cmd = ("sleep 1; bwm-ng -t %s -o csv -u bits -T rate -C ',' > %s" % (interval_sec * 1000, fname))
    Popen(cmd, shell=True).wait()

def carregaTopologia(filename):
    topologia = []
    if not exists(filename):
        filename = filename + '.txt'
    if exists(filename):
        # Abre o arquivo em formato texto
        arq = open(filename, 'r')
        for line in arq:
            # Remove o fim de linha para que não entre na variável 
            line = line.replace('\n','')
            # Quebra a linha usando espaço como separador de campo
            valores = line.split(' ')
            # O primeiro valor é o número do host/switch e os outros são as conexões
            topologia.append( { 'host': valores[0], 'conexoes': valores[1:] } )
        return(topologia)
    else:
        print("Arquivo de topologia nao encontrado.")
        exit()

def help():
    print('exercicio3.py -i <arquivo_topologia> [ -o | -e ]')

def parametro(argv):
    # Validação dos parâmetros
    infile = ''
    metodo = 'OSPF'
    try:
        opts, args = getopt.getopt(argv,"hoei:",["file="])
    except:
        help()
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt == '--file' or opt == '-i':
            infile = arg
        elif opt == '-o':
            metodo = 'OSPF'
        elif opt == '-e':
            metodo = 'ECMP'
    if infile != '':
        print('Arquivo topologia: ', infile)
        return(infile, metodo)
    else:
        help()

if __name__ == '__main__':
    setLogLevel('info')
    # Avalia os parâmetros da linha de comando
    filename,metodo = parametro(sys.argv[1:])
    print('Carregando topologia')
    # Carrega o arquivo com a topolgia em um dicionario
    topologia = carregaTopologia(filename)
    print('Criar rede')
    # Cria a topologia carregada e faz o teste
    executarTopologia(topologia, metodo, filename)
