"""Ordenação topológica em camadas (Kahn). Python puro: decide a ordem, nunca a aplicabilidade."""

from collections.abc import Iterable


class DependencyCycleError(Exception):
    def __init__(self, nodes: list[str]) -> None:
        super().__init__(f"ciclo entre dependências envolvendo: {', '.join(nodes)}")
        self.nodes = nodes


def kahn_layers(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> list[list[str]]:
    """Aresta (a, b) significa "a antes de b". Cada camada vem ordenada por slug."""
    indegree = dict.fromkeys(nodes, 0)
    successors: dict[str, list[str]] = {node: [] for node in indegree}
    for before, after in edges:
        unknown = [node for node in (before, after) if node not in indegree]
        if unknown:
            raise ValueError(f"aresta {before!r} -> {after!r} com nó desconhecido: {unknown}")
        successors[before].append(after)
        indegree[after] += 1

    layer = sorted(node for node, degree in indegree.items() if degree == 0)
    layers: list[list[str]] = []
    ordered = 0
    while layer:
        layers.append(layer)
        ordered += len(layer)
        released: list[str] = []
        for node in layer:
            for successor in successors[node]:
                indegree[successor] -= 1
                if indegree[successor] == 0:
                    released.append(successor)
        layer = sorted(released)
    if ordered < len(indegree):
        raise DependencyCycleError(_cyclic_core(successors, indegree))
    return layers


def _cyclic_core(successors: dict[str, list[str]], indegree: dict[str, int]) -> list[str]:
    """Nós não ordenados que estão em ciclo: poda os que só alimentam o ciclo (a jusante)."""
    remaining = {node for node, degree in indegree.items() if degree > 0}
    outdegree = {node: sum(s in remaining for s in successors[node]) for node in remaining}
    predecessors: dict[str, list[str]] = {node: [] for node in remaining}
    for node in remaining:
        for successor in successors[node]:
            if successor in remaining:
                predecessors[successor].append(node)
    pending = [node for node, degree in outdegree.items() if degree == 0]
    while pending:
        node = pending.pop()
        remaining.discard(node)
        for predecessor in predecessors[node]:
            outdegree[predecessor] -= 1
            if outdegree[predecessor] == 0:
                pending.append(predecessor)
    return sorted(remaining)
