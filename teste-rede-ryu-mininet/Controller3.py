from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, ether_types
from ryu.controller.dpset import EventDP
from ryu.topology import event
import networkx as nx
import os

class Controller(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    metodo = 'OSPF'
    topologia = nx.Graph()
    net = nx.DiGraph()
    switches = dict()
    hosts = dict()
    links = dict()
    blocks = dict()
    switch_map = {}
    mac_to_port = {}

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        # obtem o metodo de roteamento pela variavel de ambiente
        M = os.getenv('METODO')
        if M:
            self.metodo = M
        print('Metodo=', self.metodo)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # salva o datapath para uso futuro
        dpid = '{:0>16x}'.format(datapath.id)
        self.switch_map.update({dpid: datapath})
        
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        # Adiciona um novo fluxo
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id, priority=priority, match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignorar pacotes LLDP
            return
            
        dst = eth.dst
        src = eth.src

        dpid = '{:0>16x}'.format(datapath.id)
        
        self.mac_to_port.setdefault(dpid, {})

#        self.logger.info("dpid=%s src=%s dst=%s in_port=%s", dpid, src, dst, in_port)

        # Tratando o protocolo ARP
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            pkt_arp = pkt.get_protocol(arp.arp)
            # broadcast
            if dst == 'ff:ff:ff:ff:ff:ff':
                # evita as rotas bloqueadas (SPT)
                if self.bloqueado(dpid, in_port):
                    return
#            if pkt_arp.opcode != arp.ARP_REQUEST:
#                print('Reply:', src, dst, dpid, in_port)
            # salva a porta de saida para uso futuro
            self.mac_to_port[dpid][src] = in_port
            if dst in self.mac_to_port[dpid]:
                # se ja existe na tabela, usa a porta salva
                out_port = self.mac_to_port[dpid][dst]
            else:
                # nao existe, manda um flood
                out_port = ofproto.OFPP_FLOOD
            actions = [parser.OFPActionOutput(out_port)]
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)
            
        # Tratando os fluxos
        if not self.net.has_node(src):
            # se um host ainda nao foi adicionado a tabela, adicionar
            self.net.add_node(src)
            self.net.add_edge(src, dpid)
            self.net.add_edge(dpid, src, port = in_port)
        if self.net.has_node(dst):
            # procura o caminho usando o metodo escolhido
            path = self.find_route(src, dst)
            portas = nx.get_edge_attributes(self.net, 'port')
            # passa por cada item no caminho
            for cont in range(1, len(path) - 1):
                switch = path[cont]
                index = path.index(switch)+1
                proximo = path[index]
                out_port = portas[(switch, proximo)]
                actions = [parser.OFPActionOutput(int(out_port))]
                match = parser.OFPMatch(eth_dst=dst)
                dp = self.switch_map[switch]
                # implanta um fluxo para cada parte do caminho encontrado
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(dp, 1, match, actions, msg.buffer_id)
#                    return
                else:
                    self.add_flow(dp, 1, match, actions)
        else:
            return

    # retorna o melhor caminho de acordo com o método escolhido
    def find_route(self, switch_in, switch_out):
        path = []
        if self.metodo == 'OSPF':
            path = nx.shortest_path(self.net, switch_in, switch_out)
        elif self.metodo == 'ECMP':
            paths = [path for path in nx.all_shortest_paths(self.net, switch_in, switch_out)]
            path = self.get_route_ecmp(switch_in, switch_out, paths)
        return path

    def get_route_ecmp(self, switch_in, switch_out, paths):
        if paths:
            hash = 0
            for n in (switch_in + switch_out):
                hash += ord(n)
            choice = hash % len(paths)
            path = sorted(paths)[choice]
            return path
        else:
            return []

    @set_ev_cls(EventDP, CONFIG_DISPATCHER)
    def _event_switch_enter_handler(self, event):
        ports = event.ports  # obtem as portas do switch
        dpid = '{:0>16x}'.format(int(event.dp.id))
        # adiciona na dicionário de switch_name e datapah
        self.switch_map.setdefault(dpid, event.dp)

        if event.enter:  # verifica se é uma nova conexão de switch
            self.logger.info('switch %s conectado', dpid)
        else:  # se o switch desconectar
            del self.switch_map[dpid]  # remove do dict
            self.logger.info('switch %s desconectado', dpid)

    @set_ev_cls(event.EventSwitchEnter)
    def handler_switch_enter(self, ev):
# {
#   'dpid': '0000000000000001',
#   'ports': [
#     {
#       'dpid': '0000000000000001',
#       'port_no': '00000001',
#       'hw_addr': 'b2:26:ca:2b:d3:84',
#       'name': 's1-eth1'
#     },
#     {
#       'dpid': '0000000000000001',
#       'port_no': '00000002',
#       'hw_addr': 'ba:0b:6c:2f:92:96',
#       'name': 's1-eth2'
#     }
#   ]
# }
        msg = ev.switch.to_dict()
        dpid = msg['dpid']
        ports = msg['ports']
        self.switches.update({dpid: { 'dpid': dpid, 'ports': ports, 'hosts': {}}})
        self.atualiza_topologia()

    def get_topology_data(self, ev):
        switch_list = get_switch(self.topology_api_app, None)
        switches =['{:0>16x}'.format(switch.dp.id) for switch in switch_list]
        links_list = get_link(self.topology_api_app, None)
        links=[('{:0>16x}'.format(link.src.dpid),'{:0>16x}'.format(link.dst.dpid),{'port':link.src.port_no}) for link in links_list]
        self.net.add_nodes_from(switches)
        self.net.add_edges_from(links)

    @set_ev_cls(event.EventSwitchLeave, [MAIN_DISPATCHER, CONFIG_DISPATCHER, DEAD_DISPATCHER])
    def handler_switch_leave(self, ev):
# {
#   'dpid': '0000000000000001',
#   'ports': []
# }
        msg = ev.switch.to_dict()
        dpid = msg['dpid']
        self.switches.pop(dpid)
        self.atualiza_topologia()

    @set_ev_cls(event.EventLinkAdd)
    def link_add_handler(self, ev):
# {
#   'src': {
#     'dpid': '000062aa5b76e648',
#     'port_no': '00000002',
#     'hw_addr': '2a:bf:3e:4e:29:a7',
#     'name': 's0-eth2'
#   },
#   'dst': {
#     'dpid': '0000000000000001',
#     'port_no': '00000002',
#     'hw_addr': 'ba:0b:6c:2f:92:96',
#     'name': 's1-eth2'
#    }
# }
        msg = ev.link.to_dict()
        indice, ordenado = self.cria_indice_ordenado(msg)
        self.links.update({ indice: ordenado })
        self.atualiza_topologia()

    @set_ev_cls(event.EventLinkDelete)
    def link_del_handler(self, ev):
# {
#   'src': {
#     'dpid': '000062aa5b76e648',
#     'port_no': '00000002',
#     'hw_addr': '2a:bf:3e:4e:29:a7',
#     'name': 's0-eth2'
#   },
#   'dst': {
#     'dpid': '0000000000000001',
#     'port_no': '00000002',
#     'hw_addr': 'ba:0b:6c:2f:92:96',
#     'name': 's1-eth2'
#   }
# }
        msg = ev.link.to_dict()
        indice = self.cria_indice(msg['src']['dpid'], msg['dst']['dpid'])
        if indice in self.links:
            self.links.pop(indice)
            self.atualiza_topologia()

    # cria um indice usando origem e destino em ordem alfanumerica
    def cria_indice(self, src, dst):
        if(src < dst):
            return(src + ':' + dst)
        else:
            return(dst + ':' + src)

    # organiza os dados de acordo com a ordem alfanumerica
    def cria_indice_ordenado(self, msg):
        src = msg['src']
        dst = msg['dst']
        if(src['dpid'] < dst['dpid']):
            return(src['dpid'] + ':' + dst['dpid'], { 'src': src, 'dst': dst })
        else:
            return(dst['dpid'] + ':' + src['dpid'], { 'src': dst, 'dst': src })

    # quando ocorrem mudancas na topologia essa rotina precisa ser acionada
    def atualiza_topologia(self):
        self.topologia.clear()
        self.net.clear()
        lista_links = dict()
        for switch in self.switches.values():
            self.topologia.add_node(switch['dpid'])
            self.net.add_node(switch['dpid'])
        for link in self.links.values():
            self.topologia.add_edge(link['src']['dpid'], link['dst']['dpid'], weight=1)
            indice = self.cria_indice(link['src']['dpid'], link['dst']['dpid'])
            lista_links.update({ indice: 0})
            self.net.add_edge(link['src']['dpid'], link['dst']['dpid'], weight=1, port=link['src']['port_no'])
            self.net.add_edge(link['dst']['dpid'], link['src']['dpid'], weight=1, port=link['dst']['port_no'])
        arvore_minima = nx.minimum_spanning_tree(self.topologia)
        # cria uma tabela com as rotas bloqueadas para ARP
        self.blocks = dict()
        for link in arvore_minima.edges():
            indice = self.cria_indice(link[0], link[1])
            if indice in lista_links:
                lista_links.pop(indice)
        # remove os outros itens deixando apenas os bloqueados
        for indice in lista_links.keys():
            dados = self.links[indice]
            src_dpid = dados['src']['dpid']
            src_in_port = str(int(dados['src']['port_no']))
            src_blk = src_dpid + ':' + src_in_port
            dst_dpid = dados['dst']['dpid']
            dst_in_port = str(int(dados['dst']['port_no']))
            dst_blk = dst_dpid + ':' + dst_in_port
            self.blocks.update({ src_blk: 0})
            self.blocks.update({ dst_blk: 0})

    # identifica se a rota esta bloqueada para ARP
    def bloqueado(self, dpid, in_port):
        indice =  dpid + ':' + str(in_port)
        if indice in self.blocks:
            return True
        else:
            return False
