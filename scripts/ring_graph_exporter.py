import json
import os
from json import JSONEncoder
from typing import Dict, List, Union

import networkx as nx
import pandas as pd


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default

intTypeMap = {
        "IONIC"    : (0.0, 0.0, 1.0),
        "SSBOND"   : (1.0, 1.0, 0.0),
        "PIPISTACK": (1.0, 0.5, 0.0),
        "PICATION" : (1.0, 0.0, 0.0),
        "HBOND"    : (0.0, 1.0, 1.0),
        "VDW"      : (0.5050504803657532, 0.5050504803657532, 0.5050504803657532),
        "IAC"      : (1.0, 1.0, 1.0)
}


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


def get_freq(obj, interchain=False, intrachain=False) -> Dict[str, Dict[Edge, float]]:
    conn_freq = dict()
    for inter in intTypeMap.keys():
        conn_freq.setdefault(inter, dict())
        with open("/tmp/ring/md/{}.gfreq_{}".format(obj, inter), 'r') as f:
            for line in f:
                node1, _, node2, perc = line.split('\t')
                node1 = Node(node1)
                node2 = Node(node2)
                edge = Edge(node1, node2)

                if intrachain and node1.chain != node2.chain:
                    continue
                if interchain and node1.chain == node2.chain:
                    continue

                conn_freq[inter].setdefault(edge, float(perc))
    return conn_freq


def export_network_graph(model='input_file'):
    G = nx.MultiGraph()

    # Add the nodes to the graph
    is_md = "md" in os.listdir('.')

    file_pth = model + ".cif_ringNodes"
    df = pd.read_csv(file_pth, sep='\t')
    if len(df) == 0:
        return IndexError
    df = df.groupby('NodeId').mean()

    for (nodeId, _, degree, *_) in df.itertuples(index=True):
        node = Node(nodeId)
        G.add_node(node, degree=round(degree, 3), chain=node.chain, resi=node.resi, resn=node.resn)

    # Add the edges to the graph
    file_pth = model + ".cif_ringEdges"
    df = pd.read_csv(file_pth, sep='\t')

    distance_dict = dict()
    mean_distance = df.groupby(['NodeId1', 'NodeId2', 'Interaction']).mean()
    for (nodeId, distance, *_) in mean_distance.itertuples(index=True, name='Distance'):
        nodeId1, nodeId2, interaction = nodeId
        intType = interaction.split(":")[0]
        node1 = Node(nodeId1)
        node2 = Node(nodeId2)
        edge = Edge(node1, node2)
        distance_dict.setdefault(intType, dict()).setdefault(edge, distance)

    if is_md:
        conn_freq = get_freq(model)

    sawn = set()
    df = df.groupby(["NodeId1", "Interaction", "NodeId2"]).sum()
    for (ids, *_) in df.itertuples(index=True):
        nodeId1, interaction, nodeId2 = ids
        intType = interaction.split(":")[0]
        node1 = Node(nodeId1)
        node2 = Node(nodeId2)
        edge = Edge(node1, node2)
        key = (edge, intType)
        if key not in sawn:
            G.add_edge(node1, node2, interaction=intType, frequency=round(conn_freq[intType][edge], 3) if is_md else 1,
                       distance=round(distance_dict[intType][edge], 3))
            sawn.add(key)

    with open("{}.json".format(model), 'w+') as f:
        json.dump(nx.cytoscape_data(G), f)


if __name__ == '__main__':
    export_network_graph()
