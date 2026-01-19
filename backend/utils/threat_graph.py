import networkx as nx

class ThreatGraph:
    def __init__(self):
        self.graph = nx.Graph()

    def add_entities(self, entities):
        for i in range(len(entities) - 1):
            self.graph.add_edge(entities[i], entities[i + 1])

    def get_graph_data(self):
        return {
            "nodes": list(self.graph.nodes),
            "edges": list(self.graph.edges),
        }
