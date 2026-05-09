#!/usr/bin/env python3
"""Diagnostic obstruction to black-box tuple-to-code fibre transfer.

The older notes identify a tempting but false shortcut:

    a heavy atom in a conditional tuple law should give a heavy atom in the
    ambient code law.

This script gives the smallest possible model showing why that transfer is not
valid without an additional shadow/mass interface.  Let one coordinate of a
codeword be uniform on an alphabet of size q, and condition two independent
samples on the event X_i = Y_i = a_0.  Inside that tuple node, the common value
is deterministic, but the ambient one-sample fibre mass is only 1/q.

Therefore a local tuple-level heavy value is not an alphabet-free code-level
heavy value.  It can only be used after paying the global event mass as a
projected shadow, or by staying in a tuple-level conditioned-copy framework.
"""

from __future__ import annotations

from math import log2


def row(q: int) -> dict[str, float | int | bool]:
    tuple_atom_mass = 1.0
    ambient_fibre_mass = 1.0 / q
    event_mass = 1.0 / (q * q)
    pinned_coordinates = 2
    cost_per_pinned_coordinate = -log2(event_mass) / pinned_coordinates
    rho = 0.05
    black_box_transfer_valid = ambient_fibre_mass >= rho
    return {
        "q": q,
        "tuple_atom_mass": tuple_atom_mass,
        "ambient_fibre_mass": ambient_fibre_mass,
        "event_mass": event_mass,
        "cost_per_pin_bits": cost_per_pinned_coordinate,
        "rho": rho,
        "black_box_transfer_valid": black_box_transfer_valid,
    }


def main() -> None:
    qs = [10, 100, 10_000, 10_000_000]
    print("Tuple-to-code obstruction diagnostic")
    print("conditioning event: X_i = Y_i = a0 for two independent samples")
    print("rho=0.05 is a representative constant heavy-atom threshold")
    print()
    print(
        "q | tuple atom | ambient fibre | event mass | bits per pinned coord | "
        "black-box heavy transfer?"
    )
    print("--:|-----------:|--------------:|-----------:|----------------------:|:--")
    for q in qs:
        data = row(q)
        print(
            f"{data['q']:>8} | "
            f"{data['tuple_atom_mass']:.3f} | "
            f"{data['ambient_fibre_mass']:.8f} | "
            f"{data['event_mass']:.3e} | "
            f"{data['cost_per_pin_bits']:.4f} | "
            f"{data['black_box_transfer_valid']}"
        )

    print()
    print("Summary:")
    print("- the conditional tuple atom has mass 1 for every q")
    print("- the ambient code-law fibre mass is 1/q and falls below any fixed rho")
    print("- the global shadow mass of the conditioning event is q^{-2}")
    print("- therefore black-box tuple-to-code heavy-fibre transfer is false")
    print("- a proof must keep tuple-level conditioning or pay global shadow mass")


if __name__ == "__main__":
    main()
