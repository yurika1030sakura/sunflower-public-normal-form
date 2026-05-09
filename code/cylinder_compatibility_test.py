#!/usr/bin/env python3
"""Terminal cylinder potential compatibility stress test.

The possible failure mode is that deleting old pinned coordinates also deletes
their old-incidence debits, causing Phi_old to increase.  The manuscript's
hierarchy uses

    B_o > Q * omega_old

so that deleting one old coordinate cannot increase the terminal cylinder
potential even if that coordinate carried the maximum Q old incidences.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Constants:
    b_f: int = 800
    b_o: int = 600
    q_revisit: int = 3
    c_old: int = 5
    b_rk: int = 80
    b_s: int = 30
    c_hash: int = 50

    @property
    def omega_old(self) -> int:
        return self.c_old + self.b_rk + self.b_s + self.c_hash + 10

    @property
    def old_margin(self) -> int:
        return self.b_o - self.q_revisit * self.omega_old


def projection_drop(constants: Constants, fresh_pins: int, old_pins: int, old_inc_deleted: int) -> int:
    """Return Phi_leaf - Phi_cylinder_child.

    Positive means the cylinder child has no larger potential than the terminal
    leaf after deleting the pinned coordinates.
    """

    return (
        constants.b_f * fresh_pins
        + constants.b_o * old_pins
        - constants.omega_old * old_inc_deleted
    )


def exhaustive_projection_check(constants: Constants, max_k: int = 25) -> tuple[int, int, int]:
    checked = 0
    failures = 0
    worst_drop = 10**18
    for k in range(max_k + 1):
        for old_size in range(k + 1):
            fresh_size = k - old_size
            for fresh_pins in range(fresh_size + 1):
                for old_pins in range(old_size + 1):
                    # Worst case for Phi rebound: every pinned old coordinate
                    # carries the maximum allowed old revisit count.
                    old_inc_deleted = constants.q_revisit * old_pins
                    drop = projection_drop(constants, fresh_pins, old_pins, old_inc_deleted)
                    checked += 1
                    worst_drop = min(worst_drop, drop)
                    if drop < 0:
                        failures += 1
    return checked, failures, worst_drop


def negative_control() -> tuple[Constants, int]:
    good = Constants()
    bad = Constants(b_o=good.q_revisit * good.omega_old - 1)
    drop = projection_drop(bad, fresh_pins=0, old_pins=1, old_inc_deleted=bad.q_revisit)
    return bad, drop


def main() -> None:
    constants = Constants()
    checked, failures, worst_drop = exhaustive_projection_check(constants)
    bad_constants, bad_drop = negative_control()

    print("Terminal cylinder compatibility test")
    print(
        f"B_f={constants.b_f}, B_o={constants.b_o}, Q={constants.q_revisit}, "
        f"omega_old={constants.omega_old}, old margin={constants.old_margin}"
    )
    print(f"checked projection cases={checked}")
    print(f"failures={failures}")
    print(f"worst nonnegative drop={worst_drop}")
    print()
    print("Negative control")
    print(
        f"with B_o={bad_constants.b_o} <= Q*omega_old={bad_constants.q_revisit * bad_constants.omega_old}, "
        f"one old pinned coordinate gives drop={bad_drop}"
    )
    print(f"negative control fails as expected: {bad_drop < 0}")
    print()
    print("Summary:")
    print("- deleting fresh pinned coordinates strictly lowers Phi_fresh")
    print("- deleting old pinned coordinates cannot increase Phi_old because B_o > Q*omega_old")
    print("- the test would fail immediately if the hierarchy allowed B_o <= Q*omega_old")


if __name__ == "__main__":
    main()
