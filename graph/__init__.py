from dataclasses import dataclass
import json


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

        self.children = set()
        self.parents = set()
        self.uuid = str(node_index)
        node_index += 1

    def __hash__(self) -> str:
        return hash(self.uuid)

    def __eq__(self, other) -> bool:
        return self.uuid == other.uuid

    def __repr__(self) -> str:
        return self.uuid
    
    def serialize(self) -> str:
        return json.dumps({
            'uuid': self.uuid,
            'children': [n.uuid for n in self.children],
            'parents': [n.uuid for n in self.parents],
        })

    def add_child(self, node) -> None:
        node.parents.add(self)
        self.children.add(node)

    def add_parent(self, node) -> None:
        node.children.add(self)
        self.parents.add(node)

    def remove_child(self, node) -> None:
        node.parents.remove(self)
        self.children.remove(node)

    def remove_parent(self, node) -> None:
        node.children.remove(self)
        self.parents.remove(node)
    
    def remove(self, keep_self=False) -> None:
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
        if not keep_self:
            self.parents = []
            self.children = []


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

    def serialize(self):
        nodes = self.get_nodes()
        return json.dumps([
            json.loads(node.serialize())
            for node in nodes
        ])

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
    
    def reverse_connections(self) -> None:
        roots = []
        NodeType = None
        node_map = {node: type(node)() for node in self.get_nodes()}
        for node, rvrs in node_map.items():
            for key, value in node.__dict__.items():
                if key in Node.__annotations__:
                    continue

                rvrs.__dict__[key] = value

        for node, rvrs in node_map.items():
            if NodeType is None:
                NodeType = type(node)
            
            for child in node.children:
                try:
                    rvrs.add_parent(node_map[child])
                except:
                    pass
            for parent in node.parents:
                try:
                    rvrs.add_child(node_map[parent])
                except:
                    pass
            
            if not rvrs.parents:
                roots.append(rvrs)
        
        if len(roots) == 1:
            return Graph(roots[0])
        
        reversed = Graph(NodeType())
        for root in roots:
            reversed.root.add_child(root)

        return reversed

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
