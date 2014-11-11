import json
import networkx


class Olsr1Parser:
    def __init__(self, old, new):
        self.old_graph = networkx.MultiGraph()
        self.new_graph = networkx.MultiGraph()
        if old:
            self.parse(graph=self.old_graph, data=old)
        if new:
            self.parse(graph=self.new_graph, data=new)

    def parse(self, graph, data):
        if type(data) is not dict:
            data = json.loads(data)
        for link in data["topology"]:
            graph.add_edge(link["lastHopIP"],
                           link["destinationIP"],
                           weight=link["tcEdgeCost"])
        return graph

    def diff(self):
        def difference(old, new):
            diff = old.copy()
            diff.remove_edges_from(n for n in old.edges() if n in new.edges())
            return diff


        return {
            "added": difference(old = self.new_graph,
                                new = self.old_graph),
            "removed": difference(old = self.old_graph,
                                new = self.new_graph)
        }
