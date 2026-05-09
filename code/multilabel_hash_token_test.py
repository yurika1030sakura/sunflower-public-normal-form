#!/usr/bin/env python3
"""Multi-label hash-window and token non-accumulation test.

This script tests two bookkeeping conventions from the draft:

1. B_win is a per-labelled-window transcript budget, not a branch-global
   transcript budget.
2. A hash return creates at most one pending token, and no child or descendant
   hash window can be entered before that token is assigned to a hard exit.

The test is deliberately state-machine level.  It does not prove that the
analytic local lemmas produce the windows; it checks that once windows exist,
the public bookkeeping rule prevents token pile-up and does not accidentally
charge log |Omega| or a branch-global hash transcript.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class TransitionError(RuntimeError):
    pass


@dataclass
class Window:
    label: str
    transcript: int = 0
    coords: int = 0
    returned: bool = False


@dataclass
class HashMachine:
    h: int = 2
    b_win: int = 12
    c_hash: int = 40
    windows: dict[str, Window] = field(default_factory=dict)
    pending_token: str | None = None
    paid_tokens: int = 0
    branch_transcript: int = 0

    @property
    def target_coords(self) -> int:
        return 2 * self.h

    def _window(self, label: str) -> Window:
        if label not in self.windows:
            self.windows[label] = Window(label=label)
        return self.windows[label]

    def produce(self, label: str, transcript_cost: int) -> None:
        if self.pending_token is not None:
            raise TransitionError("cannot produce a descendant hash coordinate while a token is pending")
        w = self._window(label)
        if w.returned:
            raise TransitionError(f"window {label} has already returned")
        if w.transcript + transcript_cost > self.b_win:
            raise TransitionError(f"window {label} would exceed its per-window B_win")
        w.transcript += transcript_cost
        w.coords += 1
        self.branch_transcript += transcript_cost

    def return_window(self, label: str) -> None:
        if self.pending_token is not None:
            raise TransitionError("cannot return a second hash window while a token is pending")
        w = self._window(label)
        if w.coords < self.target_coords:
            raise TransitionError(f"window {label} has only {w.coords} coordinates")
        w.returned = True
        self.pending_token = label

    def hard_exit(self, kind: str) -> None:
        if self.pending_token is None:
            raise TransitionError(f"{kind} hard exit has no pending token to assign")
        self.paid_tokens += 1
        self.pending_token = None

    def enter_child(self) -> None:
        if self.pending_token is not None:
            raise TransitionError("cannot enter child state before assigning pending hash token")


def expect_error(name: str, fn) -> str:
    try:
        fn()
    except TransitionError as exc:
        return f"{name}: rejected ({exc})"
    raise AssertionError(f"{name}: expected rejection")


def allowed_multilabel_trace() -> HashMachine:
    m = HashMachine()
    for _ in range(4):
        m.produce("X", 3)
    for _ in range(4):
        m.produce("Z", 3)

    # The branch transcript is 24, larger than B_win=12, but each labelled
    # window has transcript exactly 12.  This is the intended per-window rule.
    assert m.branch_transcript == 24
    assert m.windows["X"].transcript == 12
    assert m.windows["Z"].transcript == 12

    m.return_window("X")
    m.hard_exit("fresh")
    m.enter_child()
    m.return_window("Z")
    m.hard_exit("old")
    m.enter_child()
    return m


def main() -> None:
    print("Multi-label hash-token test")
    machine = allowed_multilabel_trace()
    print(f"h={machine.h}, B_win={machine.b_win}, C_hash={machine.c_hash}")
    print(f"labels={sorted(machine.windows)}")
    print(f"branch transcript={machine.branch_transcript}")
    for label in sorted(machine.windows):
        w = machine.windows[label]
        print(f"window {label}: transcript={w.transcript}, coords={w.coords}, returned={w.returned}")
    print(f"paid tokens={machine.paid_tokens}, pending token={machine.pending_token}")
    print("per-window budget accepted: True")
    print("branch-global budget would reject: True")
    print()

    failures = []

    def second_return_with_pending() -> None:
        m = HashMachine()
        for _ in range(4):
            m.produce("X", 3)
        for _ in range(4):
            m.produce("Z", 3)
        m.return_window("X")
        m.return_window("Z")

    failures.append(expect_error("second window return while token pending", second_return_with_pending))

    def child_with_pending() -> None:
        m = HashMachine()
        for _ in range(4):
            m.produce("X", 3)
        m.return_window("X")
        m.enter_child()

    failures.append(expect_error("child entry while token pending", child_with_pending))

    def produce_with_pending() -> None:
        m = HashMachine()
        for _ in range(4):
            m.produce("X", 3)
        m.return_window("X")
        m.produce("Z", 3)

    failures.append(expect_error("descendant hash production while token pending", produce_with_pending))

    def overflow_one_window() -> None:
        m = HashMachine()
        for _ in range(5):
            m.produce("X", 3)

    failures.append(expect_error("single labelled-window transcript overflow", overflow_one_window))

    print("Forbidden traces")
    for line in failures:
        print(f"- {line}")
    print()
    print("Summary:")
    print("- independent labelled windows can each use B_win")
    print("- pending hash tokens cannot accumulate")
    print("- child/descendant hash entry is blocked until the token is paid")


if __name__ == "__main__":
    main()
