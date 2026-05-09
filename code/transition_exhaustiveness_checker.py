#!/usr/bin/env python3
"""Executable transition-system partition checker.

This is an interface-level checker.  It does not prove the analytic local
lemmas; instead it checks the public normal-form claim that, once the local
lemma signals are supplied, deterministic entry conditions and priority rules
make the transition system a genuine state machine:

* every retained node is in exactly one public mode;
* raw overlapping exit signals are resolved by fixed priority;
* a mode with no available exit signal is detected as an interface failure.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product


class PartitionError(RuntimeError):
    pass


@dataclass(frozen=True)
class NodeSignature:
    terminal: bool = False
    bounded_leaf: bool = False
    close_pair: bool = False
    hash_window: bool = False
    residual: bool = False
    old_window: bool = False
    pending_hash_token: bool = False


MODE_FLAGS = ("close_pair", "hash_window", "residual", "old_window")
MODES = (
    "inactive",
    "close-pair",
    "hash-window",
    "residual",
    "old-window",
    "terminal",
    "bounded-leaf",
)


def classify_mode(sig: NodeSignature) -> str:
    if sig.terminal and sig.bounded_leaf:
        raise PartitionError("terminal and bounded-leaf flags overlap")
    if sig.terminal:
        if any(getattr(sig, f) for f in MODE_FLAGS) or sig.pending_hash_token:
            raise PartitionError("terminal node carries nonterminal data")
        return "terminal"
    if sig.bounded_leaf:
        if any(getattr(sig, f) for f in MODE_FLAGS) or sig.pending_hash_token:
            raise PartitionError("bounded leaf carries nonterminal data")
        return "bounded-leaf"

    active = [flag for flag in MODE_FLAGS if getattr(sig, flag)]
    if len(active) == 0:
        if sig.pending_hash_token:
            raise PartitionError("pending hash token without returned residual block")
        return "inactive"
    if len(active) > 1:
        raise PartitionError(f"multiple active modes: {active}")
    if sig.pending_hash_token and active[0] != "residual":
        raise PartitionError("pending hash token is allowed only on returned residual state")
    return active[0].replace("_", "-")


EXIT_PRIORITIES: dict[str, tuple[str, ...]] = {
    "inactive": (
        "terminal-atom",
        "root-near-sunflower",
        "close-pair-activation",
    ),
    "close-pair": (
        "low-entropy-terminal",
        "atom-terminal",
        "product-kl-hash-or-pin",
        "high-collision-pin",
        "law-near-sunflower",
    ),
    "hash-window": (
        "terminal-value-pin",
        "bounded-support-fresh",
        "bounded-support-old",
        "public-hash-return",
    ),
    "residual": (
        "fresh-promotion",
        "fresh-close-pair-birth",
        "old-incidence",
        "scale-descent",
        "old-close-pair-birth",
        "bounded-leaf",
    ),
    "old-window": (
        "terminal-low-symbol",
        "high-revisit-pin-or-hash",
        "low-revisit-continuation",
    ),
}


def select_exit(mode: str, raw_signals: dict[str, bool]) -> str:
    for signal in EXIT_PRIORITIES[mode]:
        if raw_signals.get(signal, False):
            return signal
    raise PartitionError(f"{mode} has no exit signal")


def enumerate_mode_signatures() -> tuple[int, int, dict[str, int]]:
    valid = 0
    invalid = 0
    counts = {mode: 0 for mode in MODES}
    fields = NodeSignature.__dataclass_fields__.keys()
    for values in product((False, True), repeat=len(tuple(fields))):
        sig = NodeSignature(**dict(zip(fields, values)))
        try:
            mode = classify_mode(sig)
        except PartitionError:
            invalid += 1
        else:
            valid += 1
            counts[mode] += 1
    return valid, invalid, counts


def enumerate_exit_table() -> tuple[int, int, int, dict[str, int]]:
    checked_nonempty = 0
    overlap_raw = 0
    no_signal_failures = 0
    selected_counts: dict[str, int] = {}
    for mode, priority in EXIT_PRIORITIES.items():
        for values in product((False, True), repeat=len(priority)):
            raw = dict(zip(priority, values))
            active_count = sum(values)
            if active_count == 0:
                try:
                    select_exit(mode, raw)
                except PartitionError:
                    no_signal_failures += 1
                continue
            checked_nonempty += 1
            if active_count > 1:
                overlap_raw += 1
            selected = select_exit(mode, raw)
            selected_counts[selected] = selected_counts.get(selected, 0) + 1
    return checked_nonempty, overlap_raw, no_signal_failures, selected_counts


def negative_controls() -> list[str]:
    examples = []
    bad_sigs = [
        NodeSignature(hash_window=True, residual=True),
        NodeSignature(terminal=True, close_pair=True),
        NodeSignature(pending_hash_token=True),
        NodeSignature(old_window=True, pending_hash_token=True),
    ]
    for sig in bad_sigs:
        try:
            classify_mode(sig)
        except PartitionError as exc:
            examples.append(f"rejected bad signature {sig}: {exc}")
        else:
            raise AssertionError(f"bad signature was accepted: {sig}")

    try:
        select_exit("hash-window", {name: False for name in EXIT_PRIORITIES["hash-window"]})
    except PartitionError as exc:
        examples.append(f"rejected uncovered hash-window exit table: {exc}")
    else:
        raise AssertionError("uncovered hash-window exit table was accepted")
    return examples


def main() -> None:
    valid, invalid, counts = enumerate_mode_signatures()
    checked_nonempty, overlap_raw, no_signal_failures, selected_counts = enumerate_exit_table()
    examples = negative_controls()

    print("Transition exhaustiveness checker")
    print(f"mode signatures checked={valid + invalid}")
    print(f"valid signatures={valid}, invalid signatures={invalid}")
    print("valid mode counts:")
    for mode in MODES:
        print(f"- {mode}: {counts[mode]}")
    print()
    print("exit table:")
    print(f"- nonempty raw signal rows checked={checked_nonempty}")
    print(f"- raw overlapping rows resolved by priority={overlap_raw}")
    print(f"- no-signal rows rejected={no_signal_failures}")
    print(f"- selected exit alternatives={len(selected_counts)}")
    print()
    print("negative controls:")
    for line in examples:
        print(f"- {line}")
    print()
    print("Summary:")
    print("- legal public nodes classify into exactly one mode")
    print("- raw exit overlaps are deterministic after priority")
    print("- missing local-interface coverage is detected rather than silently accepted")


if __name__ == "__main__":
    main()
