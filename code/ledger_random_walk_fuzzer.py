#!/usr/bin/env python3
"""Random-walk fuzzer for the abstract potential ledger.

The worked transition example follows one hand-picked branch.  This fuzzer
generates many random abstract branches using the same toy constants and checks
the checkpoint invariant

    spent + Phi(state) <= Phi(initial)

at every token-free state.  A nonterminal hash return may create exactly one
pending token; while it is pending, only a hard exit may run, and that exit must
pay the token before the next checkpoint.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from random import Random


class LedgerError(RuntimeError):
    pass


@dataclass(frozen=True)
class Constants:
    c_hash: int = 50
    c_fr: int = 4
    c_old: int = 5
    c_rk: int = 3
    b_s: int = 30
    b_rk: int = 80
    q_revisit: int = 3
    b_o: int = 600
    b_f: int = 800

    @property
    def omega_old(self) -> int:
        return self.c_old + self.b_rk + self.b_s + self.c_hash + 10


@dataclass(frozen=True)
class State:
    K: int = 300
    U: int = 0
    old_inc: int = 0
    active_rank: int = 300
    active_scale: int = 0
    spent: int = 0
    pending_token: bool = False
    terminal: bool = False

    def phi(self, C: Constants) -> int:
        return (
            C.b_rk * self.active_rank
            + C.b_f * (self.K - self.U)
            + C.b_o * self.U
            - C.omega_old * self.old_inc
            + C.b_s * self.active_scale
        )


def checkpoint(state: State, C: Constants, initial_phi: int) -> None:
    if state.pending_token:
        return
    if state.spent + state.phi(C) > initial_phi:
        raise LedgerError(
            f"checkpoint failed: spent+Phi={state.spent + state.phi(C)} > {initial_phi}"
        )
    if state.old_inc > C.q_revisit * state.U:
        raise LedgerError("old revisit cap exceeded on nonterminal branch")


def activate(state: State, C: Constants) -> State:
    return replace(state, active_rank=50, active_scale=50, spent=state.spent + C.c_rk * 50)


def hash_return(state: State) -> State:
    if state.pending_token:
        raise LedgerError("hash token pile-up")
    return replace(state, pending_token=True)


def fresh_exit(state: State, C: Constants, rng: Random) -> State:
    fresh_left = state.K - state.U
    if fresh_left <= 0:
        return terminal_exit(state, C)
    f = rng.randint(1, min(5, fresh_left))
    child = rng.randint(0, f)
    token_cost = C.c_hash if state.pending_token else 0
    return replace(
        state,
        U=state.U + f,
        active_rank=child,
        active_scale=child,
        spent=state.spent + C.c_fr * f + token_cost + f,
        pending_token=False,
    )


def old_exit(state: State, C: Constants, rng: Random) -> State:
    room = C.q_revisit * state.U - state.old_inc
    if room <= 0:
        return terminal_exit(state, C)
    n = rng.randint(1, min(5, room))
    child = rng.randint(0, n)
    token_cost = C.c_hash if state.pending_token else 0
    return replace(
        state,
        old_inc=state.old_inc + n,
        active_rank=child,
        active_scale=child,
        spent=state.spent + C.c_old * n + token_cost + n,
        pending_token=False,
    )


def scale_exit(state: State, C: Constants) -> State:
    token_cost = C.c_hash if state.pending_token else 0
    child = max(0, state.active_scale // 2)
    return replace(
        state,
        active_rank=min(state.active_rank, child),
        active_scale=child,
        spent=state.spent + token_cost + 20,
        pending_token=False,
    )


def terminal_exit(state: State, C: Constants) -> State:
    token_cost = C.c_hash if state.pending_token else 0
    return replace(state, spent=state.spent + token_cost + 1, pending_token=False, terminal=True)


def run_one(seed: int, max_steps: int = 80) -> tuple[int, int, int]:
    rng = Random(seed)
    C = Constants()
    state = State()
    initial_phi = state.phi(C)
    state = activate(state, C)
    checkpoint(state, C, initial_phi)
    steps = 1
    pending_seen = 0
    max_lhs = state.spent + state.phi(C)

    while not state.terminal and steps < max_steps:
        if state.pending_token:
            pending_seen += 1
            action = rng.choice(("fresh", "old", "scale", "terminal"))
        else:
            action = rng.choice(("hash", "fresh", "old", "scale", "terminal"))

        if action == "hash":
            state = hash_return(state)
        elif action == "fresh":
            state = fresh_exit(state, C, rng)
        elif action == "old":
            state = old_exit(state, C, rng)
        elif action == "scale":
            state = scale_exit(state, C)
        else:
            state = terminal_exit(state, C)

        steps += 1
        checkpoint(state, C, initial_phi)
        if not state.pending_token:
            max_lhs = max(max_lhs, state.spent + state.phi(C))

    if state.pending_token:
        raise LedgerError("trace ended with unpaid pending token")
    return steps, pending_seen, max_lhs


def negative_control() -> str:
    state = State()
    state = hash_return(state)
    try:
        hash_return(state)
    except LedgerError as exc:
        return f"nested hash return rejected: {exc}"
    raise AssertionError("nested hash return was accepted")


def main() -> None:
    C = Constants()
    initial_phi = State().phi(C)
    traces = 1000
    max_steps_seen = 0
    total_pending = 0
    max_lhs_seen = 0
    for seed in range(traces):
        steps, pending_seen, max_lhs = run_one(seed)
        max_steps_seen = max(max_steps_seen, steps)
        total_pending += pending_seen
        max_lhs_seen = max(max_lhs_seen, max_lhs)

    print("Ledger random-walk fuzzer")
    print(f"traces={traces}")
    print(f"initial Phi={initial_phi}")
    print(f"max steps seen={max_steps_seen}")
    print(f"pending-token hard exits seen={total_pending}")
    print(f"max token-free spent+Phi seen={max_lhs_seen}")
    print(f"checkpoint margin={initial_phi - max_lhs_seen}")
    print()
    print("negative control:")
    print(f"- {negative_control()}")
    print()
    print("Summary:")
    print("- all random token-free checkpoints satisfy spent+Phi <= initial Phi")
    print("- every pending hash token is cleared by the next hard exit")
    print("- old incidences stay under the revisit cap on nonterminal branches")


if __name__ == "__main__":
    main()
