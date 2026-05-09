# v0.1-audit Public Audit Draft

This release candidate contains:

- a conditional public-normal-form draft for entropy bookkeeping in sunflower
  bounds;
- the TeX source and compiled PDF;
- twelve executable audit scripts and two diagnostic scripts;
- proof notes for the tuple-level martingale shadow-mass interface and local
  selector-certificate expansion;
- expected output logs for reproducibility.

## Status

This is not an unconditional proof of the Erdos-Rado sunflower conjecture.  The
main result is presented as a conditional interface reduction.  The local
certificates in the transition system remain the main verification burden.

Before minting a DOI or marking this as a formal release, see `AUDIT.md`.

## Audit Scripts

Run from the repository root:

```bash
python3 code/alphabet_stretch_test.py
python3 code/worked_transition_example.py
python3 code/multilabel_hash_token_test.py
python3 code/cylinder_compatibility_test.py
python3 code/transition_exhaustiveness_checker.py
python3 code/constant_hierarchy_dag_test.py
python3 code/old_queue_refinement_test.py
python3 code/hash_prefix_budget_test.py
python3 code/renyi_copy_tax_test.py
python3 code/collision_split_bound_test.py
python3 code/high_revisit_exhaustiveness_test.py
python3 code/ledger_random_walk_fuzzer.py
python3 code/kl_route_diagnostic.py
python3 code/tuple_to_code_obstruction.py
```

The scripts are intended to make several possible failure modes easy to inspect:

- hidden dependence on the ambient alphabet size;
- accidental use of a branch-global rather than per-labelled-window hash budget;
- accumulation of unpaid hash-window tokens;
- terminal-cylinder potential rebound after deleting old pinned coordinates;
- non-exhaustive or overlapping public transition modes;
- cyclic or alphabet-dependent constant hierarchies;
- inconsistent old-pattern refinement under growth of old support;
- hash prefix budget overflow entering a fixed window instead of terminalizing;
- incorrect Renyi conditioned-copy tax arithmetic;
- collision-to-split estimates that secretly depend on ambient alphabet size;
- non-exhaustive high-revisit/collision one-coordinate routing;
- composed ledger traces that accumulate hash debt or exceed the old revisit cap.
- KL-blind product-routing steps that still require a larger interface proof.
- false black-box transfer from conditional tuple atoms to ambient code fibres.

Expected logs are included under `outputs/`.

The proof note
`notes/tuple_martingale_shadow_interface.md` records the valid replacement for
the false black-box tuple-to-code transfer: terminal tuple events are kept as
global martingale events until projected shadow counting.  It is an interface
proof, not a verification of every local transition.
