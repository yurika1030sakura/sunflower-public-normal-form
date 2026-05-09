#!/usr/bin/env python3
"""Hash prefix budget stopping test.

This targets the ambiguity around coordinate-production prefixes.  A labelled
hash window may append prefix/tail/production transcript only while its own
stopped budget remains available.  If the next prefix would exceed the budget,
the branch terminalizes on the projected prefix and no hash token is created.
"""

from __future__ import annotations

from dataclasses import dataclass


class PrefixError(RuntimeError):
    pass


@dataclass
class PrefixWindow:
    label: str = "X"
    h: int = 2
    b_win: int = 10
    transcript: int = 0
    coords: int = 0
    terminalized: bool = False
    bounded_support_exit: bool = False
    token_created: bool = False
    terminal_T: int = 0

    @property
    def target_coords(self) -> int:
        return 2 * self.h

    def produce(self, prefix_cost: int, pinned_coordinates: int) -> None:
        if self.terminalized or self.bounded_support_exit or self.token_created:
            raise PrefixError("closed window cannot accept more coordinates")
        if self.transcript + prefix_cost > self.b_win:
            self.terminalized = True
            self.terminal_T += pinned_coordinates
            return
        self.transcript += prefix_cost
        self.coords += 1

    def ambient_stops(self) -> None:
        if self.terminalized or self.token_created:
            raise PrefixError("window already closed")
        if self.coords >= self.target_coords:
            raise PrefixError("full window should return, not bounded-support exit")
        if self.coords == 0:
            raise PrefixError("empty stopped decision did not open a hash window")
        self.bounded_support_exit = True

    def return_hash(self) -> None:
        if self.terminalized or self.bounded_support_exit:
            raise PrefixError("closed window cannot return hash")
        if self.coords < self.target_coords:
            raise PrefixError("cannot return before 2h coordinates")
        self.token_created = True


def expect_error(name: str, fn) -> str:
    try:
        fn()
    except PrefixError as exc:
        return f"{name}: rejected ({exc})"
    raise AssertionError(f"{name}: expected rejection")


def main() -> None:
    full = PrefixWindow()
    for cost in (3, 3, 2, 2):
        full.produce(cost, pinned_coordinates=1)
    full.return_hash()

    terminal = PrefixWindow()
    terminal.produce(3, pinned_coordinates=1)
    terminal.produce(3, pinned_coordinates=1)
    terminal.produce(5, pinned_coordinates=4)

    bounded = PrefixWindow()
    bounded.produce(3, pinned_coordinates=1)
    bounded.produce(3, pinned_coordinates=1)
    bounded.ambient_stops()

    failures = []

    def return_too_early() -> None:
        bad = PrefixWindow()
        bad.produce(3, pinned_coordinates=1)
        bad.return_hash()

    failures.append(expect_error("hash return before 2h coordinates", return_too_early))

    def append_after_terminal() -> None:
        bad = PrefixWindow()
        bad.produce(9, pinned_coordinates=1)
        bad.produce(2, pinned_coordinates=3)
        bad.produce(1, pinned_coordinates=1)

    failures.append(expect_error("append after prefix terminalization", append_after_terminal))

    def bounded_after_full() -> None:
        bad = PrefixWindow()
        for _ in range(4):
            bad.produce(2, pinned_coordinates=1)
        bad.ambient_stops()

    failures.append(expect_error("bounded-support exit after full window", bounded_after_full))

    print("Hash prefix budget stopping test")
    print(
        f"full window: transcript={full.transcript}, coords={full.coords}, "
        f"token_created={full.token_created}"
    )
    print(
        f"terminalized window: transcript={terminal.transcript}, coords={terminal.coords}, "
        f"terminalized={terminal.terminalized}, terminal_T={terminal.terminal_T}, "
        f"token_created={terminal.token_created}"
    )
    print(
        f"bounded-support window: transcript={bounded.transcript}, coords={bounded.coords}, "
        f"bounded_support_exit={bounded.bounded_support_exit}, token_created={bounded.token_created}"
    )
    print()
    print("negative controls:")
    for line in failures:
        print(f"- {line}")
    print()
    print("Summary:")
    print("- a full labelled window can return one hash token")
    print("- a prefix that would exceed B_win terminalizes before adding a coordinate")
    print("- failed accumulation exits through bounded support without creating a token")


if __name__ == "__main__":
    main()
