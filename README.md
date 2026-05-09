# A Public Normal-Form Framework for Entropy Bookkeeping in Sunflower Bounds

**Authors:** Yuli Li, Jingping Yang, Renhao Zhang

**Status:** Draft. This is a conditional framework, not an unconditional proof
of the Erdos-Rado sunflower conjecture. The main theorem is an interface
reduction: if the public transition-system certificates specified in the paper
are all verified, then the framework would imply a constant-base bound for
balanced two-collision codes, and hence for three-petal sunflower-free families
after the standard reduction.

## What This Is

This repository contains a public draft and small executable audit tests for a
proposed public-normal-form approach to entropy bookkeeping in sunflower bounds.
The draft packages the proof as a transition system with local certificates for
public tuple exits, fixed-window hash returns, residual repair, old-window
bookkeeping, and global potential accounting.

The intended conclusion is conditional on those local interfaces. The current
version is meant to make the framework inspectable and falsifiable, rather than
to ask the reader to accept an informal claim of a solved conjecture.

## What Is Novel

The proposed architectural change is to replace a codeword-level spread
invariant with a public per-coordinate transition system. Low-collision
coordinates are routed into fixed labelled hash windows; high-mass values are
terminalized as projected shadows. Near-sunflower outputs are then absorbed by
fresh, old, and scale potentials.

Individual ingredients such as entropy estimates, collision bounds, dependent
random choice, slice-rank reductions, and potential accounting are standard.
The candidate new mechanism is their organization into a fixed-window,
alphabet-free public ledger.

## What Is Not Claimed

This repository does not claim an unconditional proof of the sunflower
conjecture. In particular:

- The local certificates in the transition system remain the main verification
  burden.
- The executable tests below are falsification tests for specific bookkeeping
  and alphabet-stretch mechanisms, not a formal proof of all analytic lemmas.
- A complete independent review would need to verify the exhaustiveness of the
  public transition system and every local entropy certificate.

## Repository Layout

```text
sunflower-public-normal-form/
├── README.md
├── paper/
│   ├── sunflower_public_normal_form_v1.pdf
│   └── sunflower_public_normal_form_v1.tex
├── code/
│   ├── alphabet_stretch_test.py
│   ├── worked_transition_example.py
│   ├── multilabel_hash_token_test.py
│   ├── cylinder_compatibility_test.py
│   ├── transition_exhaustiveness_checker.py
│   ├── constant_hierarchy_dag_test.py
│   ├── old_queue_refinement_test.py
│   ├── hash_prefix_budget_test.py
│   ├── renyi_copy_tax_test.py
│   ├── collision_split_bound_test.py
│   ├── ledger_random_walk_fuzzer.py
│   ├── kl_route_diagnostic.py
│   ├── tuple_to_code_obstruction.py
│   └── requirements.txt
├── outputs/
│   ├── alphabet_stretch.log
│   ├── worked_transition.log
│   ├── multilabel_hash_token.log
│   ├── cylinder_compatibility.log
│   ├── transition_exhaustiveness.log
│   ├── constant_hierarchy_dag.log
│   ├── old_queue_refinement.log
│   ├── hash_prefix_budget.log
│   ├── renyi_copy_tax.log
│   ├── collision_split_bound.log
│   ├── ledger_random_walk_fuzzer.log
│   ├── kl_route_diagnostic.log
│   └── tuple_to_code_obstruction.log
├── CITATION.cff
├── LICENSE
└── .gitignore
```

## Reproducibility

The tests use only the Python standard library.

For the current verification status and open issues, see
[`AUDIT.md`](AUDIT.md).

### Test 1: Alphabet-Freeness Smoke Test

```bash
python3 code/alphabet_stretch_test.py
```

This builds concrete balanced two-collision toy codes and stretches the ambient
alphabet. The intended check is that the fixed hash-window cost and the relevant
collision quantities do not change when unused alphabet symbols are added.

Expected output is in [`outputs/alphabet_stretch.log`](outputs/alphabet_stretch.log).

### Test 2: Worked Transition Trace

```bash
python3 code/worked_transition_example.py
```

This runs a small-rank, large-alphabet ledger trace on a concrete balanced
two-collision code of size 25 and rank `K=300`, with ambient alphabet stretched
up to `K^10`. It traces representative public-normal-form transitions including
close-pair activation, labelled hash production, hash return, fresh promotion,
old-window registration, high revisit, deletion-trapped scale descent, and
bounded-leaf termination.

Expected output is in [`outputs/worked_transition.log`](outputs/worked_transition.log).

Summary of the alphabet replay:

| Q | log2(Q) | initial Phi | max checkpoint lhs | final lhs | ok |
|---:|---:|---:|---:|---:|:---:|
| 300 | 8.23 | 264000 | 245650 | 235754 | true |
| 90000 | 16.46 | 264000 | 245650 | 235754 | true |
| 2^82.29 | 82.29 | 264000 | 245650 | 235754 | true |

### Test 3: Multi-Label Hash-Token Test

```bash
python3 code/multilabel_hash_token_test.py
```

This checks that `B_win` is treated as a per-labelled-window budget and that
pending hash tokens cannot accumulate.  The positive trace allows two labels to
each use a full window budget, while the forbidden traces reject child entry,
descendant hash production, or a second hash return before the pending token is
paid.

Expected output is in
[`outputs/multilabel_hash_token.log`](outputs/multilabel_hash_token.log).

### Test 4: Terminal Cylinder Compatibility Test

```bash
python3 code/cylinder_compatibility_test.py
```

This checks the old-coordinate deletion issue in terminal cylinder projections.
The exhaustive toy sweep verifies that deleting pinned old coordinates cannot
increase the terminal cylinder potential under `B_o > Q omega_old`, and includes
a negative control showing immediate failure when that inequality is violated.

Expected output is in
[`outputs/cylinder_compatibility.log`](outputs/cylinder_compatibility.log).

### Test 5: Transition Exhaustiveness Checker

```bash
python3 code/transition_exhaustiveness_checker.py
```

This interface-level checker enumerates public mode signatures and abstract
exit-signal tables.  It verifies that legal public nodes classify into exactly
one mode, overlapping exit signals are resolved by deterministic priority, and
missing local-interface coverage is rejected rather than silently accepted.

Expected output is in
[`outputs/transition_exhaustiveness.log`](outputs/transition_exhaustiveness.log).

### Test 6: Constant-Hierarchy DAG Test

```bash
python3 code/constant_hierarchy_dag_test.py
```

This checks that the constant dependency graph is acyclic and that the final
constant `D` does not depend on `k` or the ambient alphabet.  It also validates
a concrete toy assignment satisfying the inequalities used by the audit scripts
and includes negative controls for an injected cycle and an injected ambient
alphabet dependency.

Expected output is in
[`outputs/constant_hierarchy_dag.log`](outputs/constant_hierarchy_dag.log).

### Test 7: Old-Queue Refinement Test

```bash
python3 code/old_queue_refinement_test.py
```

This checks that old-pattern atoms refine consistently when the old support
`U` grows, and that a queued old-window block cannot survive a sample-label
signature change unless it is first registered or charged.

Expected output is in
[`outputs/old_queue_refinement.log`](outputs/old_queue_refinement.log).

### Test 8: Hash Prefix Budget Test

```bash
python3 code/hash_prefix_budget_test.py
```

This checks the stopped transcript rule for coordinate-production prefixes.  A
window that reaches `2h` coordinates can return one hash token; a prefix whose
next description would exceed `B_win` terminalizes before adding the coordinate;
and failed accumulation exits through bounded support without creating a token.

Expected output is in
[`outputs/hash_prefix_budget.log`](outputs/hash_prefix_budget.log).

### Test 9: Renyi Copy-Tax Test

```bash
python3 code/renyi_copy_tax_test.py
```

This checks the finite-distribution inequality behind the conditioned-copy
tax.  If every surviving public key has conditional event probability at least
`rho`, the test verifies the lower bound involving `exp(-(m-1) H_m(K))`.  A
negative control shows that the inequality can fail when the per-key `rho`
condition is removed.

Expected output is in
[`outputs/renyi_copy_tax.log`](outputs/renyi_copy_tax.log).

### Test 10: Collision Split-Bound Test

```bash
python3 code/collision_split_bound_test.py
```

This checks the one-coordinate inequality
`Pr[split] = 3 sum_a p_a^2 (1-p_a) <= 3 Coll(p)` on deterministic and
pseudo-random finite laws.  It also stretches the ambient alphabet with unused
symbols and verifies that collision and split probabilities are unchanged.

Expected output is in
[`outputs/collision_split_bound.log`](outputs/collision_split_bound.log).

### Test 11: Ledger Random-Walk Fuzzer

```bash
python3 code/ledger_random_walk_fuzzer.py
```

This generates random abstract branches using the same toy constants as the
worked trace.  It checks the token-free checkpoint inequality, immediate
clearing of pending hash tokens by hard exits, and the old-incidence revisit
cap across many composed fresh/old/scale/hash/terminal sequences.

Expected output is in
[`outputs/ledger_random_walk_fuzzer.log`](outputs/ledger_random_walk_fuzzer.log).

### Diagnostic: KL Route

```bash
python3 code/kl_route_diagnostic.py
```

This diagnostic records a remaining burden rather than a passed proof check.
It shows that the elementary one-coordinate atom/collision dichotomy is
KL-blind, and that a first-crossing trigger depends only on `P`-prefix masses
once those masses are fixed.  Thus any product-KL progress must be justified by
the larger routing/conditioning/ledger interface, not by that dichotomy alone.

Expected output is in
[`outputs/kl_route_diagnostic.log`](outputs/kl_route_diagnostic.log).

### Diagnostic: Tuple-to-Code Obstruction

```bash
python3 code/tuple_to_code_obstruction.py
```

This diagnostic records the obstruction identified in the older project notes:
a heavy atom in a conditional tuple law need not be a heavy atom in the ambient
code law.  In the toy model, conditioning on `X_i = Y_i = a0` makes the tuple
node deterministic at that coordinate, while the ambient one-sample fibre mass
is only `1/q`.  Thus black-box tuple-to-code heavy-fibre transfer is false; a
proof must either keep tuple-level conditioning or pay the global projected
shadow mass.

Expected output is in
[`outputs/tuple_to_code_obstruction.log`](outputs/tuple_to_code_obstruction.log).

## Suggested Citation

Use the metadata in [`CITATION.cff`](CITATION.cff). If a Zenodo DOI is minted
for a GitHub release, cite that DOI together with the release tag.
