import sys
sys.path[0:0] = ['.']

import json

from graph import Graph, NodeRule


def load_graph_json(path):
    with open(path, 'r') as graph_file:
        graph_data = json.load(graph_file)
        rules = []
        for i, node in graph_data.items():
            i = int(i)
            rules.append(NodeRule(
                id=i,
                children=node['children'],
            ))

        return Graph.from_rules(rules)
