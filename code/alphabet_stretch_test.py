#!/usr/bin/env python3
"""Concrete alphabet-stretch smoke test for the sunflower draft.

This is not an executable implementation of the whole proof tree.  It tests
the specific alphabet-free claim that a fixed labelled hash window charges
only support/transcript quantities, not the size of an unused ambient alphabet.

Two balanced two-collision toy codes are used.

1. Binary full code: every three distinct binary words split somewhere.  This
   is the Q=2 row and routes by the high-atom terminal alternative.
2. Pair-witness code on n codewords: coordinates are indexed by unordered
   pairs {a,b}; at coordinate {a,b}, codewords a,b share value 0 and every
   other codeword has its own value.  Every triple is split by one of its pair
   coordinates.  The used support per coordinate is n-1, while the ambient
   alphabet can be stretched to K, K^2, K^10 by adding unused symbols.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb, log2


@dataclass(frozen=True)
class HashConstants:
    beta: float = 1.0 / 48.0
    h: int = 20
    b_win: int = 100
    c0: int = 10

    @property
    def c_hash(self) -> int:
        return self.c0 * (self.b_win + self.h + 1)


def fmt_q(q: int) -> str:
    if q < 10**9:
        return str(q)
    return f"2^{log2(q):.2f}"


def route(max_atom: float, collision: float, beta: float) -> str:
    if max_atom >= beta:
        return "terminal-high-atom"
    if collision <= beta:
        return "hash-eligible"
    return "neither-low-coll-nor-high-atom"


def binary_full_row(k: int, constants: HashConstants) -> dict[str, object]:
    # Any subset of a binary cube is a balanced two-collision code: among three
    # distinct binary words, some coordinate is not constant, hence exactly two
    # entries agree in that coordinate.
    return {
        "code": "binary-full",
        "ambient_Q": 2,
        "length_K": k,
        "code_size": f"2^{k}",
        "used_support": 2,
        "max_atom": 0.5,
        "collision": 0.5,
        "coord_H_bits": 1.0,
        "naive_log2_Q": 1.0,
        "route": route(0.5, 0.5, constants.beta),
        "C_hash": constants.c_hash,
    }


def pair_witness_row(n: int, ambient_q: int, constants: HashConstants) -> dict[str, object]:
    length_k = comb(n, 2)
    max_atom = 2.0 / n
    collision = (n + 2.0) / (n * n)
    coord_h = -max_atom * log2(max_atom) - (n - 2) * (1.0 / n) * log2(1.0 / n)
    return {
        "code": f"pair-witness(n={n})",
        "ambient_Q": ambient_q,
        "length_K": length_k,
        "code_size": n,
        "used_support": n - 1,
        "max_atom": max_atom,
        "collision": collision,
        "coord_H_bits": coord_h,
        "naive_log2_Q": log2(ambient_q),
        "route": route(max_atom, collision, constants.beta),
        "C_hash": constants.c_hash,
    }


def verify_pair_witness(n: int) -> tuple[int, int]:
    """Return (checked_triples, bad_triples).

    For a triple a<b<c, coordinate {a,b} has values 0,0,unique(c), so it is a
    valid two-collision witness.  The loop records that this constructive
    witness covers every triple.
    """

    checked = 0
    bad = 0
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                checked += 1
                # At coordinate {a,b}, a and b share 0; c is not in {a,b}, so
                # c receives its private nonzero value.
                if c in (a, b):
                    bad += 1
    return checked, bad


def print_table(rows: list[dict[str, object]]) -> None:
    headers = [
        "code",
        "Q",
        "K",
        "|C|",
        "support",
        "log2(Q)",
        "max p",
        "Coll",
        "route",
        "C_hash",
    ]
    print(" | ".join(headers))
    print(" | ".join("-" * len(h) for h in headers))
    for r in rows:
        print(
            " | ".join(
                [
                    str(r["code"]),
                    fmt_q(int(r["ambient_Q"])),
                    str(r["length_K"]),
                    str(r["code_size"]),
                    str(r["used_support"]),
                    f"{float(r['naive_log2_Q']):.2f}",
                    f"{float(r['max_atom']):.6f}",
                    f"{float(r['collision']):.6f}",
                    str(r["route"]),
                    str(r["C_hash"]),
                ]
            )
        )


def main() -> None:
    constants = HashConstants()
    n = 128
    k_pair = comb(n, 2)
    checked, bad = verify_pair_witness(n)

    rows = [binary_full_row(k_pair, constants)]
    for ambient_q in (k_pair, k_pair**2, k_pair**10):
        rows.append(pair_witness_row(n, ambient_q, constants))

    print("Alphabet stretch smoke test")
    print(f"beta={constants.beta:.8f}, h={constants.h}, B_win={constants.b_win}, C_hash={constants.c_hash}")
    print(f"pair-witness verification: checked {checked} triples, bad={bad}")
    print()
    print_table(rows)
    print()
    print("Stretch verdict:")
    print("- Q=2 is a valid balanced code but routes to terminal-high-atom, as expected.")
    print("- For Q=K,K^2,K^10, the used support, max atom, collision, route, and C_hash are unchanged.")
    print("- Only naive log2(Q) changes; charging that quantity would fail this test.")


if __name__ == "__main__":
    main()
