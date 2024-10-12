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
            if node in visited:
                continue
            else:
                result.append(node)
            
            visited.add(node)
            stack = [n for n in node.children if n not in visited] + stack
            stack = [n for n in node.parents if n not in visited] + stack

        return result
    
    def regular_2(self):
        node_map = self.copy_map()
        reverse_map = {
            v: k
            for k, v in node_map.items()
        }

        for node in node_map.values():
            if len(node.parents) == 1 and len(next(iter(node.parents)).children) == 1:
                parent = next(iter(node.parents))
                chilren = node.children
                for child in chilren:
                    child.add_parent(parent)
                
                orig = reverse_map[node]
                node_map[orig] = parent
                node.remove(keep_self=True)
            
            elif len(node.children) == 1 and len(next(iter(node.children)).parents) == 1:
                child = next(iter(node.children))
                parents = node.parents
                for parent in parents:
                    parent.add_child(child)
                
                orig = reverse_map[node]
                node_map[orig] = child
                node.remove(keep_self=True)

        return Graph(node_map[self.root])
    
    def unique_indexes(self):
        global node_index

        for node in self.get_nodes():
            node.uuid = str(node_index)
            node_index += 1

    def copy_map(self, keep_connections=True, node_type=None):
        node_map = {node: (node_type if node_type else type(node))() for node in self.get_nodes()}
        for node, copy in node_map.items():
            for key, value in node.__dict__.items():
                if key in Node.__annotations__:
                    continue

                copy.__dict__[key] = value

            if keep_connections:
                for child in node.children:
                    twin = node_map[child]
                    copy.add_child(twin)

                for parent in node.parents:
                    twin = node_map[parent]
                    copy.add_parent(twin)
        
        return node_map

    def reverse_connections(self):
        roots = []
        node_map = self.copy_map(keep_connections=False)

        for node, rvrs in node_map.items():
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
        
        reversed = Graph(Node())
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


@dataclass
class NodeMapping:
    left: set[Node]
    right: set[Node]

    def __init__(self):
        self.left = set()
        self.right = set()
