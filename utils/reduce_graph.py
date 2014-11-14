#!/usr/bin/env python

import json
import networkx as nx
import sys
import random
import copy
import matplotlib.pyplot as plt



if len(sys.argv) != 4:
    print "Usage: ./reduce_graph.py num_nodes (int) topo_file (json) show_topo (0/1)"
    sys.exit(1)

topo_file = sys.argv[2]
new_size = int(sys.argv[1])
show_topo = int(sys.argv[3])

def parse_olsr_topo(topo_file):
    graph = nx.MultiGraph()
    js = open(topo_file)
    data = json.load(js)
    for link in data["topology"]:
        graph.add_edge(link["lastHopIP"],
                       link["destinationIP"],
                       weight=link["tcEdgeCost"])
    return graph, data

def reduce_graph(new_size, graph):
    size_diff = len(graph) - new_size
    if size_diff <= 0:
        print "Your reduced graph is larger than the original:", len(graph)
        sys.exit(1)
    for i in range(1000):
        #Let's do 1000 attempts to find a random subgraph of 
        #the chosen size, else we give up
        test_graph = graph.copy()
        new_nodes = random.sample(graph.nodes(), new_size)
        new_graph = test_graph.subgraph(new_nodes)
        if nx.is_connected(new_graph):
            return new_graph
    return None




graph, data  = parse_olsr_topo(topo_file)
new_graph = reduce_graph(new_size, graph)

if new_graph == None:
    print "Could not find a connected graph of the size you requested!"
    sys.exit(1)

newjson = copy.deepcopy(data)
print "old graph len", len(data["topology"])
print new_graph.edges()
for link in data["topology"]:
    if (link["lastHopIP"], link["destinationIP"]) not in new_graph.edges():
        newjson["topology"].remove(link)

if show_topo:
    nx.draw(new_graph)
    plt.show()
print json.dumps(newjson, indent=1)

