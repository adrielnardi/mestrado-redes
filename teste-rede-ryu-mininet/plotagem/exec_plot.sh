#! /bin/bash
for X in *.bwm; do
	TOPO=$(echo ${X}|cut -f1 -d\.)
	python2 plot_rate.py --rx --maxy 14000 --xlabel 'Time (seconds)' --ylabel  'Rate (Mbps)' -i 'total' -f "${TOPO}.bwm" -o "${TOPO}.png"
done
