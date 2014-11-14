import json
import networkx
import random



class Olsr1Parser(object):
    def __init__(self, old, new):
        self.old_graph = networkx.MultiGraph()
        self.new_graph = networkx.MultiGraph()
        if old:
            self.parse(graph=self.old_graph, data=old)
            self.old_data = old
        if new:
            self.parse(graph=self.new_graph, data=new)
            self.new_data = new
    
    def parse(self, graph, data):
        if type(data) is not dict:
            data = json.loads(data)
        for link in data["topology"]:
            graph.add_edge(link["lastHopIP"],
                           link["destinationIP"],
                           weight=link["tcEdgeCost"])
        return graph

    def reduce_graph(self, new_size, data = None):
        if data == None:
            data = self.new_data
        g = networkx.MultiGraph()
        graph = self.parse(g, data)
        size_diff = len(g) - new_size
        if size_diff <= 0:
            print "Your reduced graph is larger than the original"
            sys.exit(1)
        for i in range(1000):
            #Let's do 1000 attempts to find a random subgraph of 
            #the chosen size, else we give up
            test_graph = graph.copy()
            new_graph = random.sample(graph.nodes(), size_diff)








    def diff(self):
        return {
            "added": networkx.difference(self.new_graph, self.old_graph),
            "removed": networkx.difference(self.old_graph, self.new_graph)
        }
