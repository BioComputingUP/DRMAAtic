import json
import os
from json import JSONEncoder
from typing import List, Union

import networkx as nx
import pandas as pd


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default


class Node:
    def __init__(self, *args):
        if len(args) == 1:
            self.init_string(*args)
        else:
            self.init_args(*args)
        self.atom = None

    def init_string(self, string_id: str):
        if ':' in string_id:
            ids = string_id.strip().split(':')
        else:
            ids = string_id.strip().split('/')

        self.chain: str = ids[0]
        self.resi: int = int(ids[1])
        self.ins = None
        self.resn = None

        if len(ids) > 2:
            if len(ids[2]) == 3:
                self.resn: str = ids[2]
            else:
                self.ins: str = ids[2]
            if len(ids) > 3:
                self.resn: str = ids[3]

        if self.ins == '_':
            self.ins = None

    def init_args(self, chain: str, resi: Union[int, str], resn: str = None, ins: str = None):
        self.chain: str = chain
        self.resi: int = int(resi)
        self.ins: str = ins
        self.resn: str = resn

    def __lt__(self, other):
        if self.ins:
            return self.chain < other.chain or \
                   self.chain == other.chain and self.resi < other.resi or \
                   self.chain == other.chain and self.resi == other.resi and self.ins < other.ins
        return self.chain < other.chain or self.chain == other.chain and self.resi < other.resi

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return self == other or other < self

    def __eq__(self, other):
        if not other:
            return False
        base = self.chain == other.chain and self.resi == other.resi and self.ins == other.ins
        if self.resn and other.resn:
            base = base and self.resn == other.resn
        return base

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        if self.resn:
            if self.ins:
                return "{}/{}/{}/{}".format(self.chain, self.resi, self.ins, self.resn)
            else:
                return "{}/{}/{}".format(self.chain, self.resi, self.resn)
        elif self.ins:
            return "{}/{}/{}".format(self.chain, self.resi, self.ins)
        return "{}/{}".format(self.chain, self.resi)

    def __hash__(self):
        if self.ins is not None:
            return hash((self.chain, self.resi, self.ins))
        return hash((self.chain, self.resi))

    def id_repr(self):
        return "{}/{}".format(self.chain, self.resi)

    def id_tuple(self):
        return self.chain, self.resi

    def to_json(self):
        return self.__repr__()


class Edge:
    def __init__(self, *args):
        self.node1 = None
        self.node2 = None
        if len(args) == 2:
            self.init_nodes(*args)
        else:
            self.init_list(*args)

    def init_nodes(self, node1: Node, node2: Node):
        self.node1: Node = node1
        self.node2: Node = node2

    def init_list(self, sorted_node_list: List[Node]):
        if len(sorted_node_list) != 2:
            raise ValueError("Cannot create an Edge with more than two nodes")
        self.node1: Node = sorted_node_list[0]
        self.node2: Node = sorted_node_list[1]

    def __lt__(self, other):
        return self.node1 < other.node1 or (self.node1 == other.node1 and self.node2 < other.node2)

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return self == other or other < self

    def __eq__(self, other):
        if not other:
            return False
        return (self.node1 == other.node1 and self.node2 == other.node2) or (
                self.node1 == other.node2 and self.node2 == other.node1)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "{} - {}".format(self.node1, self.node2)

    def __hash__(self):
        return hash((self.node1, self.node2))


def produce_graph(model='input_file'):
    G = nx.MultiGraph()

    # Add the nodes to the graph
    if "input_file.cif_ringNodes" in os.listdir("."):
        ext = "cif"
    else:
        ext = "pdb"

    # Add nodes to the graph
    file_pth = model + ".{}_ringNodes".format(ext)
    df = pd.read_csv(file_pth, sep='\t')
    if len(df) == 0:
        return IndexError
    df = df.groupby('NodeId').mean()

    for (nodeId, _, degree, *_) in df.itertuples(index=True):
        node = Node(nodeId)
        G.add_node(node, degree=round(degree, 3), chain=node.chain, resi=node.resi, resn=node.resn)

    # Now edges
    file_pth = model + ".{}_ringEdges".format(ext)
    df = pd.read_csv(file_pth, sep='\t')

    max_model = df["Model"].max()
    # Remove useless interaction informations
    df["Interaction"] = df["Interaction"].map(lambda x: x.split(':')[0])
    # Remove coordinates from atom columns
    df = df.replace({'Atom1': r'[^A-Z]*', 'Atom2': r'[^A-Z]*'}, {'Atom1': '', 'Atom2': ''}, regex=True)
    group = df.groupby(['NodeId1', 'NodeId2', 'Interaction', 'Atom1', 'Atom2']).mean()
    # Get the frequency for that contact
    group["Model"] = group["Model"] / max_model

    for (ids, distance, _, energy, _, frequency) in group.itertuples(index=True):
        nodeId1, nodeId2, interaction, atom1, atom2 = ids
        node1 = Node(nodeId1)
        node2 = Node(nodeId2)
        G.add_edge(node1, node2, interaction=interaction, frequency=round(frequency, 3),
                   distance=round(distance, 3), atom1=atom1, atom2=atom2)

    with open("{}.json".format(model), 'w+') as f:
        json.dump(nx.cytoscape_data(G), f)


if __name__ == '__main__':
    produce_graph(model='input_file')
