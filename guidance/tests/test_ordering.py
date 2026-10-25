import pytest

from guidance.engine.ordering import DependencyCycleError, kahn_layers


def test_linear() -> None:
    assert kahn_layers(["c", "b", "a"], [("a", "b"), ("b", "c")]) == [["a"], ["b"], ["c"]]


def test_diamond() -> None:
    edges = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]
    assert kahn_layers("abcd", edges) == [["a"], ["b", "c"], ["d"]]


def test_independent_nodes_share_sorted_layer() -> None:
    assert kahn_layers(["z", "m", "a"], []) == [["a", "m", "z"]]


def test_empty() -> None:
    assert kahn_layers([], []) == []


def test_unknown_node_in_edge() -> None:
    with pytest.raises(ValueError, match="x"):
        kahn_layers(["a"], [("a", "x")])


def test_cycle_reports_unordered_nodes() -> None:
    edges = [("a", "b"), ("b", "c"), ("c", "a"), ("z", "a")]
    with pytest.raises(DependencyCycleError, match="a, b, c") as info:
        kahn_layers("abcdz", edges)
    assert info.value.nodes == ["a", "b", "c"]


def test_self_loop() -> None:
    with pytest.raises(DependencyCycleError) as info:
        kahn_layers(["a", "b"], [("a", "a")])
    assert info.value.nodes == ["a"]


def test_cycle_nodes_exclude_downstream() -> None:
    with pytest.raises(DependencyCycleError) as info:
        kahn_layers("abc", [("a", "b"), ("b", "a"), ("b", "c")])
    assert info.value.nodes == ["a", "b"]
