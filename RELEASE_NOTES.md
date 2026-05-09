# v0.1-audit Public Audit Draft

This release candidate contains:

- a conditional public-normal-form draft for entropy bookkeeping in sunflower
  bounds;
- the TeX source and compiled PDF;
- six executable audit scripts;
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
```

The scripts are intended to make several possible failure modes easy to inspect:

- hidden dependence on the ambient alphabet size;
- accidental use of a branch-global rather than per-labelled-window hash budget;
- accumulation of unpaid hash-window tokens;
- terminal-cylinder potential rebound after deleting old pinned coordinates.
- non-exhaustive or overlapping public transition modes;
- cyclic or alphabet-dependent constant hierarchies.

Expected logs are included under `outputs/`.
