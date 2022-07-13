import sys, getopt
import networkx as nx

def str2int(str):
	try:
		i = int(str)
	except:
		i = 0
	return(i)

def help():
	print('Parâmetros:\n-n <nodes>\n-e <edges>\n-s <seed>')
	sys.exit()

def parametro(argv):
	nodes = 16
	edges = 32
	seed = 0
	try:
		opts, args = getopt.getopt(argv,"n:e:s:")
	except:
		help()
	for opt, arg in opts:
		if opt == '-h':
			help()
		elif opt == '-n':
			nodes = str2int(arg)
		elif opt == '-e':
			edges = str2int(arg)
		elif opt == '-s':
			seed = str2int(arg)
		else:
			help()
	return nodes, edges, seed

if __name__ == '__main__':
	if len(sys.argv) > 1:
		nodes, edges, seed = parametro(sys.argv[1:])
	else:
		nodes = 16
		edges = 32
		seed = 0

	# Use seed for reproducibility
	G = nx.gnm_random_graph(nodes, edges, seed=seed)

	for line in nx.generate_adjlist(G):
		print(line)
