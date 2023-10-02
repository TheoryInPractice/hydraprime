import networkx as nx
from typing import TextIO

__all__ = ['read_pace_2023', 'load_pace_2023']


def read_pace_2023(input: TextIO) -> nx.Graph:
    G = None
    for line in input.readlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('c'):
            continue  # ignore comments

        if line.startswith('p'):
            _, _, nn, mm = line.split()
            n, m = int(nn), int(mm)
            G = nx.empty_graph(n)
        else:
            u, v = map(int, line.split())
            assert G is not None
            G.add_edge(u - 1, v - 1)

    assert G is not None
    assert m == G.number_of_edges(), 'inconsistent edges'
    return G


def load_pace_2023(path: str) -> nx.Graph:
    with open(path) as f:
        return read_pace_2023(f)
