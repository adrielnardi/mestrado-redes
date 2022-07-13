#!/usr/bin/python
import sys, getopt
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSSwitch
from mininet.cli import CLI

class NovaTopologia(Topo):
    def build(self, topologia=[]):
        switches = {}
        for item in topologia:
            swname = 's' + item['host']
            switch = self.addSwitch(swname)
            switches.update( { swname: switch } )
            host = self.addHost('h' + item['host'])
            self.addLink(host, switch)
        for item in topologia:
            sworig = 's' + item['host']
            switch_orig = switches[sworig]
            for conexao in item['conexoes']:
                swdest = 's' + conexao
                switch_dest = switches[swdest]
                self.addLink(switch_orig, switch_dest)


def criarTopologia(topologia):
    topo = NovaTopologia(topologia)
    net = Mininet(topo, switch=OVSSwitch)
    net.start()
    net.waitConnected()
    print( "Dumping host connections" )
    dumpNodeConnections(net.hosts)
    print( "Testing network connectivity" )
    #CLI (net)
    while net.pingAll() > 0:
        print('Try new network connectivity test')
    print('===========================')
    print('All Network Nodes Connected')
    print('===========================')
    net.stop()

def carregaTopologia(infile):
    topologia = []
    arq = open(infile, 'r')
    for line in arq:
        line = line.replace('\n','')
        valores = line.split(' ')
        topologia.append( { 'host': valores[0], 'conexoes': valores[1:] } )
    return(topologia)

def help():
    print('exercicio2.py --file <arquivo_topologia>')

def parametro(argv):
    infile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:",["file="])
    except:
        help()
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt == '--file':
            infile = arg
    if infile != '':
        print('Arquivo topologia: ', infile)
        return(infile)
    else:
        help()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    infile = parametro(sys.argv[1:])
    print('Carregando topologia')
    topologia = carregaTopologia(infile)
    print('Criar rede')
    criarTopologia(topologia)
