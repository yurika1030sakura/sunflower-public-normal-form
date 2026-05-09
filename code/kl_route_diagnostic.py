#!/usr/bin/env python3
"""Diagnostic for the KL-blind part of product-KL routing.

This is intentionally not a "proof passed" test.  It records a structural
warning: the elementary one-coordinate dichotomy

    max_a p(a) >= tau  OR  Coll(p) < tau

is true for every one-coordinate law p and does not use KL(P||Q).  Therefore a
product-KL transfer lemma must obtain its real progress from the surrounding
prefix/conditioning/ledger interface, not from this dichotomy alone.
"""

from __future__ import annotations

from math import log


def normalize(weights: list[float]) -> list[float]:
    total = sum(weights)
    return [w / total for w in weights]


def kl(p: list[float], q: list[float]) -> float:
    out = 0.0
    for x, y in zip(p, q):
        if x == 0:
            continue
        if y == 0:
            return float("inf")
        out += x * log(x / y)
    return out


def coll(p: list[float]) -> float:
    return sum(x * x for x in p)


def dichotomy_route(p: list[float], tau: float) -> str:
    if max(p) >= tau:
        return "value-pin"
    if coll(p) < tau:
        return "low-collision-hash"
    raise AssertionError("elementary dichotomy failed")


def first_crossing(prefix_probs: list[float], lam: float) -> int | None:
    mass = 1.0
    for i, prob in enumerate(prefix_probs, start=1):
        mass *= prob
        if -log(mass) > lam * i:
            return i
    return None


def main() -> None:
    tau = 0.2
    cases = [
        ("uniform", [0.01] * 100),
        ("spiky", normalize([60.0, 20.0, 10.0, 10.0])),
        ("medium", normalize([18.0, 17.0, 16.0, 15.0, 14.0, 20.0])),
    ]
    q_uniforms = {
        "same": None,
        "uniform": None,
    }

    print("KL route diagnostic")
    print(f"tau={tau}")
    for name, p in cases:
        q_same = p
        q_uniform = [1.0 / len(p)] * len(p)
        route_same = dichotomy_route(p, tau)
        route_uniform = dichotomy_route(p, tau)
        print(
            f"- {name}: max={max(p):.6f}, Coll={coll(p):.6f}, "
            f"KL(P||P)={kl(p, q_same):.6f}, route={route_same}"
        )
        print(
            f"  against uniform Q: KL={kl(p, q_uniform):.6f}, route={route_uniform}"
        )

    prefix_probs = [0.8, 0.1, 0.5, 0.5]
    lam = 0.7
    crossing = first_crossing(prefix_probs, lam)
    print()
    print("Prefix crossing diagnostic")
    print(f"prefix probabilities={prefix_probs}, lambda={lam}, first crossing={crossing}")
    print("The crossing calculation depends only on P-prefix masses, not on Q.")
    print()
    print("Summary:")
    print("- the atom/collision route is KL-blind")
    print("- the first-crossing trigger is also KL-blind once P-prefix masses are fixed")
    print("- product-KL progress must therefore be justified by the larger interface")


if __name__ == "__main__":
    main()
