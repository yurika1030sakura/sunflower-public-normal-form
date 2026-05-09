#!/usr/bin/env python3
"""Renyi conditioned-copy tax finite-distribution test.

For a random public key K with law p_k and m conditioned copies, the fixed-copy
lemma uses

    sum_k p_k^m nu_k^m(F_k) >= rho * sum_k p_k^m
                             = rho * exp(-(m-1) H_m(K))

provided every surviving key has nu_k^m(F_k) >= rho.  This script checks the
finite inequality on deterministic and pseudo-random distributions and includes
a negative control where the uniform per-key lower bound is violated.
"""

from __future__ import annotations

from math import isclose, log
from random import Random


def normalize(weights: list[float]) -> list[float]:
    total = sum(weights)
    return [w / total for w in weights]


def renyi_h(p: list[float], m: int) -> float:
    return log(sum(x**m for x in p)) / (1 - m)


def copy_mass(p: list[float], event_probs: list[float], m: int) -> float:
    return sum((x**m) * f for x, f in zip(p, event_probs))


def lower_bound(p: list[float], rho: float, m: int) -> float:
    return rho * sum(x**m for x in p)


def run_case(name: str, p: list[float], event_probs: list[float], rho: float, m: int) -> tuple[str, bool, float]:
    h_m = renyi_h(p, m)
    exp_form = rho * pow(2.718281828459045, -(m - 1) * h_m)
    direct = lower_bound(p, rho, m)
    mass = copy_mass(p, event_probs, m)
    if not isclose(exp_form, direct, rel_tol=1e-12, abs_tol=1e-15):
        raise AssertionError("Renyi expression and direct power sum disagree")
    return name, mass + 1e-15 >= direct, mass - direct


def main() -> None:
    rng = Random(1729)
    rho = 0.2
    m = 3
    cases: list[tuple[str, list[float], list[float]]] = [
        ("uniform-5", [0.2] * 5, [rho] * 5),
        ("spiky", normalize([100.0, 3.0, 2.0, 1.0]), [rho, 0.5, 0.8, 1.0]),
        ("geometric", normalize([0.5**i for i in range(8)]), [rho + 0.03 * (i % 4) for i in range(8)]),
    ]
    for n in (3, 6, 10, 20):
        weights = [rng.random() ** 3 + 0.001 for _ in range(n)]
        p = normalize(weights)
        events = [rho + (1 - rho) * rng.random() for _ in range(n)]
        cases.append((f"random-{n}", p, events))

    print("Renyi conditioned-copy tax test")
    print(f"m={m}, rho={rho}")
    all_ok = True
    worst_margin = 10**9
    for name, p, events in cases:
        _, ok, margin = run_case(name, p, events, rho, m)
        all_ok = all_ok and ok
        worst_margin = min(worst_margin, margin)
        print(f"- {name}: ok={ok}, margin={margin:.12g}, support={len(p)}")

    bad_p = normalize([100.0, 1.0, 1.0])
    bad_events = [0.0, 1.0, 1.0]
    _, bad_ok, bad_margin = run_case("bad-heavy-key", bad_p, bad_events, rho, m)
    print()
    print("Negative control")
    print(f"- bad-heavy-key: ok={bad_ok}, margin={bad_margin:.12g}")
    print()
    print("Summary:")
    print(f"- all surviving-key cases satisfy the Renyi lower bound: {all_ok}")
    print(f"- worst nonnegative margin={worst_margin:.12g}")
    print("- violating the per-key rho lower bound can break the inequality")


if __name__ == "__main__":
    main()
