#!/bin/bash
for TOPO in rede-100 rede-20000 hipercubo loop minima; do
	sudo python exercicio3.py -i ${TOPO}
	sudo mn -c
	mv ${TOPO}.bwm OSPF-${TOPO}.bwm
	sudo python exercicio3.py -e -i ${TOPO}
	sudo mn -c
	mv ${TOPO}.bwm ECPM-${TOPO}.bwm
done
