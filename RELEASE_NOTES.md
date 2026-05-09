# v1.0 Initial Public Draft

This release candidate contains:

- a conditional public-normal-form draft for entropy bookkeeping in sunflower
  bounds;
- the TeX source and compiled PDF;
- two executable audit scripts;
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
```

The scripts are intended to make two possible failure modes easy to inspect:

- hidden dependence on the ambient alphabet size;
- accumulation of unpaid hash-window tokens.

Expected logs are included under `outputs/`.
