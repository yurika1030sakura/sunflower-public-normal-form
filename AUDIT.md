# Audit Status

This file records the current verification status of the public-normal-form
draft.  It is intentionally conservative: passing an item here means only that
the stated local check has been inspected or tested, not that the whole
conditional framework has been independently verified.

## Current Recommendation

Do not mint a Zenodo DOI or create a formal GitHub Release yet.

The repository is already public and timestamped by git commits and the
`v0.2-audit` tag.  A formal release should wait until the open interface checks
below are either verified or clearly separated into a smaller conditional
statement.

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

### 4. Multi-label hash-token test

Script:

```bash
python3 code/multilabel_hash_token_test.py
```

This state-machine test checks the ambiguity between a per-window and a
per-branch hash transcript budget.  It accepts a trace in which two different
sample labels each use the full `B_win` budget, so the branch transcript exceeds
`B_win` while every individual labelled window remains within budget.

It also rejects the following forbidden traces:

- returning a second hash window while a previous token is pending;
- entering a child state while a token is pending;
- producing a descendant hash coordinate while a token is pending;
- exceeding the transcript budget of one labelled window.

Interpretation: this is evidence that the intended per-labelled-window
semantics and token-free checkpoint convention are internally coherent.  It is
not a proof that all analytic branches produce such windows.

### 5. Terminal cylinder compatibility test

Script:

```bash
python3 code/cylinder_compatibility_test.py
```

This tests the old-coordinate rebound issue in terminal cylinder projections.
Deleting an old pinned coordinate also deletes its old-incidence debit, which
could increase `Phi_old`.  The sweep checks all toy projection cases up to rank
25 under the hierarchy condition

```text
B_o > Q * omega_old.
```

No failures occur.  The script also includes a negative control: replacing
`B_o` by `Q * omega_old - 1` fails immediately for one old pinned coordinate.

Interpretation: this supports the terminal-cylinder compatibility calculation
for the specific old-debit deletion failure mode.  It does not verify every
source of terminal shadows.

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
