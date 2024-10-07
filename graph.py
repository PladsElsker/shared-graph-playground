from dataclasses import dataclass


@dataclass
class NodeRule:
    id: int
    children: list


node_index = 0


@dataclass
class Node:
    children: list
    parents: list
    uuid: str

    def __init__(self) -> None:
        global node_index

        self.children = []
        self.parents = []
        self.uuid = str(node_index)
        node_index += 1

    def __hash__(self) -> str:
        return hash(self.uuid)

    def __eq__(self, other) -> bool:
        return self.uuid == other.uuid

    def __repr__(self) -> str:
        return self.uuid

    def add_child(self, node) -> None:
        self.children.append(node)
        node.parents.append(self)
    
    def remove(self) -> None:
        for parent in self.parents:
            try:
                parent.children.remove(self)
            except ValueError:
                pass
        for child in self.children:
            try:
                child.parents.remove(self)
            except ValueError:
                pass


@dataclass
class Graph:
    root: Node

    def __eq__(self, other: 'Graph') -> bool:
        if not isinstance(other, Graph):
            return False

        return self._are_equal(self.root, other.root, set())

    def _are_equal(self, node1: Node, node2: Node, visited: set) -> bool:
        if not isinstance(node1, Node) or not isinstance(node2, Node):
            return False

        if len(node1.children) != len(node2.children):
            return False

        node1_id = id(node1)
        if node1_id in visited:
            return True

        visited.add(node1_id)
        for child1 in node1.children:
            if not any(self._are_equal(child1, child2, visited) for child2 in node2.children):
                return False

        return True

    def get_nodes(self) -> list:
        stack: list[Node] = [self.root]
        visited: set[Node] = set()
        result: list[Node] = []

        while stack:
            node = stack.pop()
            if node not in visited:
                result.append(node)
            
            visited.add(node)
            stack += [n for n in node.children if n not in visited]

        return result

    def unique_indexes(self) -> None:
        global node_index

        for node in self.get_nodes():
            node.uuid = str(node_index)
            node_index += 1

    @staticmethod
    def from_rules(rules: list):
        nodes = {}
        for rule in rules:
            node = Node()
            node.uuid = str(rule.id)
            nodes[str(rule.id)] = node

        valid_root_ids = list(nodes.keys())
        for rule, (k, node) in zip(rules, nodes.items()):
            for child_id in rule.children:
                node.add_child(nodes[f'{child_id}'])
                try:
                    valid_root_ids.remove(str(child_id))
                except (ValueError, AttributeError):
                    pass

        if valid_root_ids:
            return Graph(nodes[valid_root_ids[0]])

        return None
