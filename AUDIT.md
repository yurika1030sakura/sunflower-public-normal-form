# Audit Status

This file records the current verification status of the public-normal-form
draft.  It is intentionally conservative: passing an item here means only that
the stated local check has been inspected or tested, not that the whole
conditional framework has been independently verified.

## Current Recommendation

Do not mint a Zenodo DOI or create a formal GitHub Release yet.

The repository is already public and timestamped by git commits and the `v1.0`
tag.  A formal release should wait until the open interface checks below are
either verified or clearly separated into a smaller conditional statement.

If a release is needed before that point, label it as a pre-release audit draft
and keep the title modest, for example:

```text
v0.1 public audit draft
```

## Checks Passed So Far

### 1. Public package check

The public repository contains:

- the draft PDF and TeX source;
- executable Python audit scripts;
- expected output logs;
- citation metadata;
- a conservative README that does not claim an unconditional proof.

### 2. Alphabet-stretch smoke test

Script:

```bash
python3 code/alphabet_stretch_test.py
```

This test uses concrete balanced two-collision toy codes and stretches the
ambient alphabet.  In the tested low-collision rows, the used support,
maximum atom, collision, route, and fixed hash-window cost remain unchanged
when the ambient alphabet is stretched from `K` to `K^2` to `K^10`.

Interpretation: this is evidence that the tested hash-window quantities are
support/transcript dependent rather than ambient-alphabet dependent.  It is
not a proof of the full transition system.

### 3. Worked transition ledger trace

Script:

```bash
python3 code/worked_transition_example.py
```

This test runs a representative small-rank, large-alphabet ledger trace through
the following transition types:

- inactive to close-pair activation;
- labelled hash production;
- fixed-window hash return;
- residual fresh promotion with hash-token assignment;
- law-level residual return;
- second fresh promotion;
- old-window registration;
- high-revisit terminal branch;
- deletion-trapped scale descent;
- bounded-leaf termination.

The token-free checkpoints satisfy the toy ledger inequality, and the result is
unchanged as `log2(|Omega|)` increases from `8.23` to `82.29`.

Interpretation: this checks that the written token-free checkpoint semantics
are coherent on a concrete trace.  It does not prove exhaustiveness of all
possible branches.

## Open Verification Burdens

### A. Local interface verification

The main theorem is conditional on local public-transition interfaces.  Each
interface must be checked directly from its hypotheses, including:

- positive-KL/product-KL routing into terminal pins or hash coordinates;
- fixed-window hash return with stopped per-labelled-window transcript;
- residual decision order;
- old-supported residual routing;
- old-window/high-revisit routing;
- terminal cylinder potential compatibility.

### B. Exhaustiveness of the transition system

The public modes must form an actual partition after deterministic tie-breaks:

- inactive code-law mode;
- close-pair mode;
- hash-window mode;
- residual mode;
- old-window mode;
- terminal and bounded-leaf modes.

The paper currently states this as an interface proposition.  A more convincing
version would list entry and exit conditions in a mechanically checkable table.

### C. Hash-token non-accumulation

The current manuscript imposes token-free checkpoints: a hash return may create
one pending token attached to the returned residual block, but that token must
be assigned before a child state or descendant hash window is entered.

This needs continued stress testing, especially in multi-label and nested
scale scenarios.

### D. Constant hierarchy

The constants appear acyclic in the current draft, and the toy traces do not
show hidden alphabet dependence.  A final version should still give a fully
expanded dependency DAG and state which constants are fixed before `k` and the
ambient alphabet are chosen.

## Release Criteria

A formal release or DOI would be more credible after at least one of the
following is available:

1. a complete interface-by-interface audit table with explicit inequalities;
2. a Lean or other formal harness proving the abstract ledger/token invariants;
3. an executable transition checker for a wider class of toy states;
4. an external reader's report confirming that the local interfaces are
   correctly stated.

Until then, the repository is best described as a public audit draft.
