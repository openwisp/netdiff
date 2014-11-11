import json
import networkx as nx
import random



class OlsrGraphGen:
	def __init__(self, seed):
		self.parse_olsr_topo(seed)
	#olsr json to networkx
	def parse_olsr_topo(self, data):
		self.graph = nx.MultiGraph()
		if type(data) is not dict:
			data = json.loads(data)
		for link in data["topology"]:
			self.graph.add_edge(link["lastHopIP"],
						link["destinationIP"],
						weight=link["tcEdgeCost"])
		return self.graph

	def reduce_graph(self, new_size):
		size_diff = len(self.graph) - new_size
		if size_diff <= 0:
			print ("Your reduced graph is larger than the original:", len(self.graph))
			sys.exit(1)
		for i in range(1000):
			#Let's do 1000 attempts to find a random subgraph of
			#the chosen size, else we give up
			test_graph = self.graph.copy()
			new_nodes = random.sample(self.graph.nodes(), new_size)
			new_graph = test_graph.subgraph(new_nodes)
			if nx.is_connected(new_graph):
				return new_graph
		return None

	#networkx to olsr json
	def gen_olsr_topo(self, graph):
		data = {"topology": []}
		for n in graph.edges(data=True):
			data["topology"].append({"lastHopIP" : n[0], "destinationIP" : n[1], "tcEdgeCost" : n[2]['weight']})# to fix etx
		return json.dumps(data,indent=1)
