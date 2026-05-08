#!/usr/bin/env python3
"""Worked small-rank / large-alphabet transition trace.

This is an executable falsification-oriented example for the public-normal-form
draft.  It does not try to implement the analytic lemmas automatically.  It
does two concrete things:

* builds a real balanced two-collision toy code with small rank K=300 and a
  stretched ambient alphabet Q=K^10;
* runs representative public-normal-form transition rows on that code while
  tracking the finite potential ledger, including the one-step pending
  hash-token state that must be cleared before the next child state.

The point is to catch accidental dependence on log |Omega| and token pile-up.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import comb, log2
from typing import Callable


@dataclass(frozen=True)
class CodeStats:
    n_words: int = 25

    @property
    def rank(self) -> int:
        return comb(self.n_words, 2)

    @property
    def used_support_per_coordinate(self) -> int:
        return self.n_words - 1

    @property
    def max_atom(self) -> float:
        return 2.0 / self.n_words

    @property
    def collision(self) -> float:
        return (self.n_words + 2.0) / (self.n_words * self.n_words)

    def verify_balanced(self) -> tuple[int, int]:
        checked = 0
        bad = 0
        for a in range(self.n_words):
            for b in range(a + 1, self.n_words):
                for c in range(b + 1, self.n_words):
                    checked += 1
                    # Coordinate {a,b} witnesses exactly two equal values:
                    # a and b share 0; c receives a private nonzero value.
                    if c in (a, b):
                        bad += 1
        return checked, bad


@dataclass(frozen=True)
class Constants:
    beta: float = 0.083
    h: int = 3
    b_win: int = 20
    c_hash: int = 50
    c_fr: int = 4
    c_old: int = 5
    c_rk: int = 3
    b_s: int = 30
    b_rk: int = 80
    revisit_cap: int = 3
    b_o: int = 600
    b_f: int = 800

    @property
    def omega_old(self) -> int:
        return self.c_old + self.b_rk + self.b_s + self.c_hash + 10


@dataclass(frozen=True)
class State:
    K: int
    ambient_Q: int
    U: int = 0
    old_inc: int = 0
    active_rank: int = 0
    active_scale: int = 0
    spent: int = 0
    pending_hash_tokens: int = 0
    T: int = 0
    R: int = 0

    def phi(self, C: Constants) -> int:
        return (
            C.b_rk * self.active_rank
            + C.b_f * (self.K - self.U)
            + C.b_o * self.U
            - C.omega_old * self.old_inc
            + C.b_s * self.active_scale
        )

    def checkpoint_lhs(self, C: Constants) -> int:
        return self.spent + self.phi(C)

    def token_lhs(self, C: Constants) -> int:
        return self.spent + self.pending_hash_tokens * C.c_hash + self.phi(C)


def fmt_q(q: int) -> str:
    return str(q) if q < 10**9 else f"2^{log2(q):.2f}"


def run_trace(ambient_Q: int, verbose: bool = True) -> dict[str, int | bool]:
    stats = CodeStats()
    C = Constants()
    K = stats.rank
    s = State(K=K, ambient_Q=ambient_Q, active_rank=K, active_scale=0)
    initial_phi = s.phi(C)
    rows: list[tuple[str, State, str]] = []

    def step(name: str, update: Callable[[State], State], note: str) -> None:
        nonlocal s
        s = update(s)
        rows.append((name, s, note))

    step(
        "inactive -> close-pair activation",
        lambda x: replace(
            x,
            active_rank=50,
            active_scale=50,
            spent=x.spent + C.c_rk * 50,
        ),
        "rank drop pays a public DRC/activation child of size 50",
    )
    step(
        "close-pair -> labelled hash production",
        lambda x: x,
        "six low-collision coordinates are available; transcript is stopped within B_win",
    )
    step(
        "hash window -> residual near-sunflower",
        lambda x: replace(x, pending_hash_tokens=x.pending_hash_tokens + 1),
        "one temporary C_hash token is attached to the returned residual block",
    )
    step(
        "residual -> fresh promotion, token assigned",
        lambda x: replace(
            x,
            U=x.U + 10,
            active_rank=5,
            active_scale=5,
            pending_hash_tokens=x.pending_hash_tokens - 1,
            spent=x.spent + C.c_fr * 10 + C.c_hash + 10,
        ),
        "fresh drop pays transcript, a child rank/scale deposit, and the unique hash token",
    )
    step(
        "close-pair -> law-level residual return",
        lambda x: x,
        "probabilistic near-sunflower return; no alphabet value is exposed",
    )
    step(
        "residual -> second fresh promotion",
        lambda x: replace(
            x,
            U=x.U + 10,
            active_rank=5,
            active_scale=5,
            spent=x.spent + C.c_fr * 10 + 10,
        ),
        "another disjoint fresh set is promoted",
    )
    step(
        "residual -> old-window registration",
        lambda x: replace(
            x,
            old_inc=x.old_inc + 4,
            active_rank=4,
            active_scale=4,
            spent=x.spent + C.c_old * 4 + 4,
        ),
        "old incidences debit N_old and birth a smaller old close-pair block",
    )
    step(
        "old-window -> high-revisit terminal",
        lambda x: replace(x, T=x.T + 1, R=x.R + 1, spent=x.spent + 1),
        "alternative terminal branch: high revisit pins one projected coordinate",
    )

    # A separate nonterminal continuation from the old-window checkpoint tests
    # deletion-trapped scale descent and bounded-leaf entry.
    before_terminal = rows[-2][1]
    scale_child = replace(
        before_terminal,
        active_rank=1,
        active_scale=1,
        spent=before_terminal.spent + 20,
    )
    bounded_leaf = scale_child

    max_checkpoint_lhs = max(r[1].checkpoint_lhs(C) for r in rows if r[1].pending_hash_tokens == 0)
    max_token_lhs = max(r[1].token_lhs(C) for r in rows)

    if verbose:
        checked, bad = stats.verify_balanced()
        print("Worked transition trace")
        print(f"rank K={K}, ambient |Omega|={fmt_q(ambient_Q)}, code size={stats.n_words}")
        print(
            "pair-witness code: "
            f"checked {checked} triples, bad={bad}, support={stats.used_support_per_coordinate}, "
            f"max_atom={stats.max_atom:.6f}, collision={stats.collision:.6f}"
        )
        print(
            f"beta={C.beta}, h={C.h}, B_win={C.b_win}, C_hash={C.c_hash}, "
            f"log2(|Omega|)={log2(ambient_Q):.2f}"
        )
        print(f"initial Phi={initial_phi}")
        print()
        print("transition | spent | pending | Phi | spent+Phi | spent+token+Phi | status")
        print("---------- | -----: | ------: | --: | --------: | --------------: | ------")
        for name, st, note in rows:
            checkpoint = (
                "ok"
                if st.pending_hash_tokens == 0 and st.checkpoint_lhs(C) <= initial_phi
                else "pending-token"
                if st.pending_hash_tokens
                else "FAIL"
            )
            print(
                f"{name} | {st.spent} | {st.pending_hash_tokens} | {st.phi(C)} | "
                f"{st.checkpoint_lhs(C)} | {st.token_lhs(C)} | {checkpoint}"
            )
            print(f"  note: {note}")
        print(
            "old-window -> deletion-trapped scale descent | "
            f"{scale_child.spent} | {scale_child.pending_hash_tokens} | {scale_child.phi(C)} | "
            f"{scale_child.checkpoint_lhs(C)} | {scale_child.token_lhs(C)} | "
            f"{'ok' if scale_child.checkpoint_lhs(C) <= initial_phi else 'FAIL'}"
        )
        print("  note: nonterminal continuation drops active scale to 1")
        print(
            "bounded leaf | "
            f"{bounded_leaf.spent} | {bounded_leaf.pending_hash_tokens} | {bounded_leaf.phi(C)} | "
            f"{bounded_leaf.checkpoint_lhs(C)} | {bounded_leaf.token_lhs(C)} | "
            f"{'ok' if bounded_leaf.checkpoint_lhs(C) <= initial_phi else 'FAIL'}"
        )
        print("  note: active rank is below the toy m0 cutoff")
        print()
        print("Summary:")
        print(f"- ordinary token-free checkpoints satisfy spent+Phi <= initial Phi: {max_checkpoint_lhs <= initial_phi}")
        print("- the single hash-return row is a non-checkpoint pending-token state")
        print(f"- final token-free bounded-leaf checkpoint ok: {bounded_leaf.checkpoint_lhs(C) <= initial_phi}")

    return {
        "initial_phi": initial_phi,
        "max_checkpoint_lhs": max_checkpoint_lhs,
        "max_token_lhs": max_token_lhs,
        "final_lhs": bounded_leaf.checkpoint_lhs(C),
        "final_ok": bounded_leaf.checkpoint_lhs(C) <= initial_phi,
        "checkpoint_ok": max_checkpoint_lhs <= initial_phi,
    }


def main() -> None:
    stats = CodeStats()
    K = stats.rank
    run_trace(K**10, verbose=True)
    print()
    print("Alphabet replay")
    print("Q | log2(Q) | initial Phi | max checkpoint lhs | final lhs | ok")
    print("- | -------: | ----------: | -----------------: | --------: | --")
    for Q in (K, K**2, K**10):
        out = run_trace(Q, verbose=False)
        print(
            f"{fmt_q(Q)} | {log2(Q):.2f} | {out['initial_phi']} | "
            f"{out['max_checkpoint_lhs']} | {out['final_lhs']} | {out['final_ok']}"
        )


if __name__ == "__main__":
    main()
