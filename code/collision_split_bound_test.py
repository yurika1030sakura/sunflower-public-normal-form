#!/usr/bin/env python3
"""Collision-controls-split finite-distribution test.

For three iid samples from a one-coordinate law p, the split event is exactly
that two samples agree and the third differs.  The bound used in the draft is

    Pr[split] = 3 sum_a p_a^2 (1-p_a) <= 3 Coll(p).

This script verifies the formula on finite laws, including ambient-alphabet
stretching by unused symbols.
"""

from __future__ import annotations

from math import isclose, log2
from random import Random


def normalize(weights: list[float]) -> list[float]:
    total = sum(weights)
    return [w / total for w in weights]


def collision(p: list[float]) -> float:
    return sum(x * x for x in p)


def split_probability(p: list[float]) -> float:
    return 3.0 * sum(x * x * (1.0 - x) for x in p)


def pair_collision_union_bound(p: list[float]) -> float:
    # Probability that at least one pair agrees is at most this union bound.
    return 3.0 * collision(p)


def stretch(p: list[float], ambient_q: int) -> list[float]:
    if ambient_q < len(p):
        raise ValueError("ambient alphabet smaller than support")
    return p + [0.0] * (ambient_q - len(p))


def main() -> None:
    rng = Random(20260508)
    base_cases = [
        ("uniform-2", [0.5, 0.5]),
        ("uniform-20", [1.0 / 20] * 20),
        ("spiky", normalize([12.0, 3.0, 1.0, 1.0])),
        ("pair-witness-n128", [2.0 / 128] + [1.0 / 128] * 126),
    ]
    for n in (5, 11, 30):
        base_cases.append((f"random-{n}", normalize([rng.random() ** 2 + 0.001 for _ in range(n)])))

    print("Collision split-bound test")
    all_ok = True
    for name, p in base_cases:
        coll = collision(p)
        split = split_probability(p)
        bound = pair_collision_union_bound(p)
        ok = split <= bound + 1e-15
        all_ok = all_ok and ok
        print(f"- {name}: support={len(p)}, Coll={coll:.12g}, split={split:.12g}, 3Coll={bound:.12g}, ok={ok}")

    pair = [2.0 / 128] + [1.0 / 128] * 126
    stretched_rows = []
    for q in (127, 8128, 8128**2):
        s = stretch(pair, q)
        stretched_rows.append((q, collision(s), split_probability(s)))

    same_after_stretch = all(
        isclose(stretched_rows[0][1], row[1], rel_tol=0, abs_tol=1e-15)
        and isclose(stretched_rows[0][2], row[2], rel_tol=0, abs_tol=1e-15)
        for row in stretched_rows
    )

    print()
    print("Ambient alphabet stretch")
    for q, coll, split in stretched_rows:
        print(f"- Q={q} log2(Q)={log2(q):.2f}: Coll={coll:.12g}, split={split:.12g}")
    print()
    print("Summary:")
    print(f"- all finite laws satisfy split <= 3 Coll: {all_ok}")
    print(f"- adding unused alphabet symbols leaves Coll and split unchanged: {same_after_stretch}")


if __name__ == "__main__":
    main()
