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
│   └── requirements.txt
├── outputs/
│   ├── alphabet_stretch.log
│   └── worked_transition.log
├── CITATION.cff
├── LICENSE
└── .gitignore
```

## Reproducibility

The tests use only the Python standard library.

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

## Suggested Citation

Use the metadata in [`CITATION.cff`](CITATION.cff). If a Zenodo DOI is minted
for a GitHub release, cite that DOI together with the release tag.
