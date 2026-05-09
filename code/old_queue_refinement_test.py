#!/usr/bin/env python3
"""Old-window queue refinement and signature-flush test.

This targets the measure-theoretic bookkeeping issue that old-pattern atoms
must refine consistently when U grows, and that queued old-window data cannot
survive a change of sample-label signature unless it is first flushed.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class QueueError(RuntimeError):
    pass


@dataclass
class OldQueueState:
    support: set[int] = field(default_factory=set)
    pattern: dict[int, str] = field(default_factory=dict)
    signature: str = "XYZ"
    queued_blocks: list[tuple[int, ...]] = field(default_factory=list)
    registered: int = 0
    charged_flushes: int = 0

    def install_pattern(self, support: set[int], pattern: dict[int, str]) -> None:
        if set(pattern) != support:
            raise QueueError("pattern domain must equal support")
        self.support = set(support)
        self.pattern = dict(pattern)

    def enlarge_support(self, new_support: set[int], new_pattern: dict[int, str]) -> None:
        if not self.support <= new_support:
            raise QueueError("old support must be monotone")
        if set(new_pattern) != new_support:
            raise QueueError("new pattern domain must equal new support")
        for coord in self.support:
            if new_pattern[coord] != self.pattern[coord]:
                raise QueueError(f"pattern refinement changed old coordinate {coord}")
        self.support = set(new_support)
        self.pattern = dict(new_pattern)

    def enqueue(self, block: tuple[int, ...], signature: str) -> None:
        if signature != self.signature:
            raise QueueError("cannot enqueue a block with a different signature")
        if not set(block) <= self.support:
            raise QueueError("queued block must lie in old support")
        self.queued_blocks.append(block)

    def register_queue(self) -> None:
        self.registered += sum(len(block) for block in self.queued_blocks)
        self.queued_blocks.clear()

    def change_signature(self, signature: str, flush: bool) -> None:
        if signature == self.signature:
            return
        if self.queued_blocks and not flush:
            raise QueueError("signature changed with an unpaid old-window queue")
        if self.queued_blocks:
            self.charged_flushes += 1
            self.register_queue()
        self.signature = signature


def expect_error(name: str, fn) -> str:
    try:
        fn()
    except QueueError as exc:
        return f"{name}: rejected ({exc})"
    raise AssertionError(f"{name}: expected rejection")


def main() -> None:
    state = OldQueueState()
    state.install_pattern({1, 2}, {1: "eq", 2: "neq"})
    state.enqueue((1, 2), "XYZ")
    state.enlarge_support({1, 2, 3, 4}, {1: "eq", 2: "neq", 3: "eq", 4: "split"})
    state.enqueue((3, 4), "XYZ")
    state.change_signature("XZY", flush=True)
    state.enlarge_support(
        {1, 2, 3, 4, 5},
        {1: "eq", 2: "neq", 3: "eq", 4: "split", 5: "neq"},
    )

    failures = []

    def inconsistent_refinement() -> None:
        bad = OldQueueState()
        bad.install_pattern({1, 2}, {1: "eq", 2: "neq"})
        bad.enlarge_support({1, 2, 3}, {1: "neq", 2: "neq", 3: "eq"})

    failures.append(expect_error("inconsistent old-pattern refinement", inconsistent_refinement))

    def signature_change_without_flush() -> None:
        bad = OldQueueState()
        bad.install_pattern({1, 2}, {1: "eq", 2: "neq"})
        bad.enqueue((1, 2), "XYZ")
        bad.change_signature("XZY", flush=False)

    failures.append(expect_error("signature change without queue flush", signature_change_without_flush))

    def nonold_queue_entry() -> None:
        bad = OldQueueState()
        bad.install_pattern({1, 2}, {1: "eq", 2: "neq"})
        bad.enqueue((1, 3), "XYZ")

    failures.append(expect_error("queue entry outside old support", nonold_queue_entry))

    print("Old-window queue refinement test")
    print(f"support={sorted(state.support)}")
    print(f"pattern={state.pattern}")
    print(f"signature={state.signature}")
    print(f"registered incidences={state.registered}")
    print(f"charged flushes={state.charged_flushes}")
    print(f"queued blocks after signature change={state.queued_blocks}")
    print()
    print("negative controls:")
    for line in failures:
        print(f"- {line}")
    print()
    print("Summary:")
    print("- old support grows monotonically")
    print("- old-pattern atoms refine without changing old coordinates")
    print("- changing sample-label signature requires registering or charging the queue")


if __name__ == "__main__":
    main()
