#!/usr/bin/env python3
"""Constant-hierarchy dependency and inequality test.

This checks the bookkeeping-level claim that the constants can be chosen in an
acyclic order independent of k and the ambient alphabet size.  It also validates
a concrete toy assignment satisfying the displayed inequalities used by the
audit scripts.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


class DagError(RuntimeError):
    pass


GRAPH: dict[str, set[str]] = {
    "base_thresholds": set(),
    "sigma": {"base_thresholds"},
    "theta_rk": {"base_thresholds"},
    "q_fresh": {"base_thresholds"},
    "Q_revisit": {"base_thresholds"},
    "r_old": {"base_thresholds"},
    "h": {"base_thresholds"},
    "B_win": {"base_thresholds"},
    "C_hash": {"B_win", "h"},
    "C_fr": {"q_fresh", "C_hash"},
    "C_old": {"Q_revisit", "r_old"},
    "C_rk": {"theta_rk"},
    "B_s": {"sigma"},
    "B_rk": {"B_s", "C_rk", "C_hash", "theta_rk"},
    "omega_old": {"C_old", "B_rk", "B_s", "C_hash"},
    "B_o": {"Q_revisit", "omega_old"},
    "B_f": {"B_o", "C_fr", "C_hash", "B_rk", "B_s"},
    "m0": {"B_s", "C_hash", "sigma"},
    "C_star": {"C_hash", "C_fr", "C_old", "C_rk", "B_s", "B_rk", "B_o", "B_f"},
    "A": {"C_star"},
    "D0": {"m0"},
    "D": {"A", "D0"},
}


@dataclass(frozen=True)
class ToyConstants:
    sigma: Fraction = Fraction(1, 20)
    theta_rk: Fraction = Fraction(1, 4)
    Q_revisit: int = 3
    h: int = 3
    B_win: int = 20
    C_hash: int = 50
    C_fr: int = 4
    C_old: int = 5
    C_rk: int = 3
    B_s: int = 30
    B_rk: int = 80
    B_o: int = 600
    B_f: int = 800
    m0: int = 4
    D0: int = 1000
    A: int = 1000
    D: int = 10**9

    @property
    def omega_old(self) -> int:
        return self.C_old + self.B_rk + self.B_s + self.C_hash + 10


def topo_sort(graph: dict[str, set[str]]) -> list[str]:
    temporary: set[str] = set()
    permanent: set[str] = set()
    order: list[str] = []

    def visit(node: str) -> None:
        if node in permanent:
            return
        if node in temporary:
            raise DagError(f"cycle detected at {node}")
        temporary.add(node)
        for dep in graph.get(node, set()):
            if dep not in graph:
                raise DagError(f"unknown dependency {dep} of {node}")
            visit(dep)
        temporary.remove(node)
        permanent.add(node)
        order.append(node)

    for node in graph:
        visit(node)
    return order


def ancestors(graph: dict[str, set[str]], node: str) -> set[str]:
    out: set[str] = set()

    def go(n: str) -> None:
        for dep in graph[n]:
            if dep not in out:
                out.add(dep)
                go(dep)

    go(node)
    return out


def validate_inequalities(C: ToyConstants) -> list[str]:
    checks: list[tuple[str, bool, str]] = []
    checks.append(
        (
            "omega_old definition",
            C.omega_old == C.C_old + C.B_rk + C.B_s + C.C_hash + 10,
            f"{C.omega_old} == {C.C_old + C.B_rk + C.B_s + C.C_hash + 10}",
        )
    )
    checks.append(
        (
            "old margin",
            C.B_o > C.Q_revisit * C.omega_old + 20,
            f"{C.B_o} > {C.Q_revisit * C.omega_old + 20}",
        )
    )
    checks.append(
        (
            "fresh margin",
            C.B_f - C.B_o > C.C_fr + C.C_hash + C.B_rk + C.B_s + 10,
            f"{C.B_f - C.B_o} > {C.C_fr + C.C_hash + C.B_rk + C.B_s + 10}",
        )
    )
    lhs = C.B_rk * (1 - C.theta_rk)
    rhs = (C.B_s + C.C_rk + C.C_hash + 10) * C.theta_rk
    checks.append(("rank child margin", lhs > rhs, f"{lhs} > {rhs}"))
    scale_lhs = C.B_s * (1 - 4 * C.sigma) * C.m0
    scale_rhs = C.C_hash + 10
    checks.append(("scale cutoff margin", scale_lhs > scale_rhs, f"{scale_lhs} > {scale_rhs}"))
    checks.append(("base-case absorbed", C.D >= C.D0, f"{C.D} >= {C.D0}"))

    failures = [f"{name}: {detail}" for name, ok, detail in checks if not ok]
    if failures:
        raise AssertionError("; ".join(failures))
    return [f"{name}: {detail}" for name, _, detail in checks]


def negative_controls() -> list[str]:
    out: list[str] = []
    cyclic = {node: set(deps) for node, deps in GRAPH.items()}
    cyclic["C_hash"].add("B_f")
    try:
        topo_sort(cyclic)
    except DagError as exc:
        out.append(f"cycle injection rejected: {exc}")
    else:
        raise AssertionError("cycle injection was accepted")

    ambient_bad = {node: set(deps) for node, deps in GRAPH.items()}
    ambient_bad["ambient_alphabet"] = set()
    ambient_bad["C_hash"].add("ambient_alphabet")
    bad_ancestors = ancestors(ambient_bad, "D")
    if "ambient_alphabet" not in bad_ancestors:
        raise AssertionError("ambient alphabet dependency was not detected")
    out.append("ambient-alphabet dependency injection detected in ancestors(D)")
    return out


def main() -> None:
    order = topo_sort(GRAPH)
    d_ancestors = ancestors(GRAPH, "D")
    C = ToyConstants()
    inequality_lines = validate_inequalities(C)
    negatives = negative_controls()

    print("Constant hierarchy DAG test")
    print(f"nodes={len(GRAPH)}")
    print(f"topological order={' -> '.join(order)}")
    print(f"ambient alphabet in ancestors(D)={'ambient_alphabet' in d_ancestors}")
    print()
    print("toy inequalities:")
    for line in inequality_lines:
        print(f"- {line}")
    print()
    print("negative controls:")
    for line in negatives:
        print(f"- {line}")
    print()
    print("Summary:")
    print("- dependency graph is acyclic")
    print("- D depends on fixed hierarchy constants, not on k or ambient alphabet")
    print("- toy constants satisfy the ledger inequalities used in the audit scripts")


if __name__ == "__main__":
    main()
