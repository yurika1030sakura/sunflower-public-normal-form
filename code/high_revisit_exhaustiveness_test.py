#!/usr/bin/env python3
"""Check that one-coordinate heavy-atom exits are exhaustive.

The old shorthand "heavy atom OR low collision" is not a proof-tree
partition: if a heavy atom exists, the complement may still have large mass and
must be routed.  The corrected route peels all atoms of mass >= rho*tau and
then either prunes a small complement or sends a large complement to a
low-collision hash coordinate.  This applies to high-revisit exits and to
cross/high-collision exits.
"""

from __future__ import annotations


def collision(p: list[float]) -> float:
    return sum(x * x for x in p)


def old_shorthand_gap(p: list[float], tau: float) -> tuple[bool, float]:
    heavy = [x for x in p if x >= tau]
    if not heavy:
        return (False, 0.0)
    # Terminalizing only one heavy atom leaves the rest of the branch uncovered.
    return (sum(p) - max(heavy) > 1e-12, sum(p) - max(heavy))


def corrected_route(p: list[float], rho: float, tau: float) -> dict[str, float | str]:
    threshold = rho * tau
    heavy_mass = sum(x for x in p if x >= threshold)
    light = [x for x in p if x < threshold]
    light_mass = sum(light)
    if light_mass < rho:
        route = "prune-light-complement"
        light_collision = 0.0
    else:
        q = [x / light_mass for x in light]
        light_collision = collision(q)
        route = "low-collision-hash"
        assert light_collision <= tau + 1e-12
    return {
        "threshold": threshold,
        "heavy_mass": heavy_mass,
        "light_mass": light_mass,
        "light_collision": light_collision,
        "route": route,
    }


def main() -> None:
    rho = 0.5
    tau = 0.2
    # One heavy atom, many tiny light atoms.  The old shorthand sees the heavy
    # atom, but terminalizing it alone leaves 70 percent of the branch.
    p = [0.30] + [0.70 / 100] * 100
    gap, uncovered = old_shorthand_gap(p, tau)
    route = corrected_route(p, rho, tau)
    print("One-coordinate exit exhaustiveness test")
    print(f"rho={rho}, tau={tau}, rho*tau={rho*tau}")
    print(f"old shorthand has uncovered complement? {gap}")
    print(f"old shorthand uncovered mass={uncovered:.6f}")
    print(f"corrected heavy mass={route['heavy_mass']:.6f}")
    print(f"corrected light mass={route['light_mass']:.6f}")
    print(f"corrected light collision={route['light_collision']:.6f}")
    print(f"corrected route={route['route']}")
    print("OK: heavy branches plus light complement form a partition")


if __name__ == "__main__":
    main()
