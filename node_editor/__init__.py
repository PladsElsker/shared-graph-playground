import sys
sys.path[0:0] = ['.']

import os
import json

from graph import Graph, NodeRule


graph = None
if os.path.exists('node_editor/tree_structure.json'):
    with open('node_editor/tree_structure.json', 'r') as graph_file:
        graph_data = json.load(graph_file)
        rules = []
        for i, node in graph_data.items():
            i = int(i)
            rules.append(NodeRule(
                id=i,
                children=node['children'],
            ))

        graph = Graph.from_rules(rules)
