# Tuple-Level Martingale Shadow Interface

This note records the part of the tuple-to-code gap that can be proved cleanly.
It does not prove the full public-normal-form transition system.  Its purpose is
to replace the false black-box statement

```text
conditional tuple-law heavy fibre -> ambient code-law heavy fibre
```

by a valid martingale statement:

```text
conditional tuple-law branches remain tuple events until terminal projection;
the global probability of the resulting projected shadow is paid by the product
of the conditional probabilities along the stopped path.
```

## Theorem

Let `C` be a finite code with uniform law `mu`, and let
`X^1,...,X^r` be independent samples from `mu`.  Let `T` be a finite adaptive
proof tree on the product space `C^r`.  Every internal node `v` is an event
`E_v subset C^r`; its child selector `A_v` is measurable with respect to the
conditional law on `E_v`, and the child events partition `E_v`.

At each terminal leaf `ell`, suppose the terminal event `E_ell` is assigned a
nonempty multi-sample projected value-shadow

```text
theta(ell) = ((J_s, a_s))_{s in S(ell)}
```

such that

```text
E_ell subset intersection_{s in S(ell)} { X^s_{J_s} = a_s }.
```

Let `Theta` be the random projected shadow obtained from the terminal leaf, and
let

```text
T(Theta) = sum_s |J_s|,        R(Theta) = |S|.
```

Assume the local selectors have charges `c_v >= 0` satisfying

```text
H(A_v | E_v) <= E[c_v | E_v]
```

and that the total branch charge satisfies

```text
sum_{v reached} c_v <= lambda T(Theta) + c R(Theta) + B
```

on every retained terminal branch, for some nonnegative branch remainder `B`.
Then

```text
H(Theta) <= E[lambda T(Theta) + c R(Theta) + B].
```

Consequently, there is a projected shadow value `theta` such that

```text
-log Pr[Theta = theta] <= lambda T(theta) + c R(theta) + b
```

for at least one terminal branch with `Theta = theta` and branch remainder
`B = b`.

If the branch uses charged pruning, the same statement holds with the original
pre-pruning shadow mass after adding the accumulated pruning loss to `B`.

## Proof

Let `Gamma` be the full terminal leaf transcript before projection.  Since
`Theta` is a deterministic function of `Gamma`,

```text
H(Theta) <= H(Gamma).
```

Reveal the proof tree in a fixed topological order.  At an unreached node the
selector is a cemetery symbol; at a reached node `v` the selector has conditional
entropy `H(A_v | E_v)`.  The chain rule gives

```text
H(Gamma) = sum_v Pr(E_v) H(A_v | E_v).
```

Using the local charge inequality and summing,

```text
H(Theta) <= E sum_{v reached} c_v
          <= E[lambda T(Theta) + c R(Theta) + B].
```

Apply the same averaging argument to the random variable

```text
I(Theta) - lambda T(Theta) - c R(Theta) - B,
```

where `I(Theta) = -log Pr[Theta]`.  Its expectation is nonpositive, so at least
one retained terminal outcome has nonpositive value, which is the displayed
pointwise shadow-mass inequality.

For pruning, if a retained branch has pruning losses

```text
L_pr = sum_j -log q_j,
```

then the original unnormalized mass of a projected shadow atom is the normalized
shadow mass multiplied by the conditional expectation of `exp(-L_pr)` over that
atom.  Jensen gives

```text
-log Pr_orig[Theta = theta]
 <= -log Pr_retained[Theta = theta] + E[L_pr | Theta = theta].
```

Thus adding `L_pr` to the branch remainder gives the pre-pruning version.

## What This Proves

This proves that conditional tuple-level terminal pins are safe when they are
kept as tuple events until the final projected shadow.  For example, if a node
`E` branches to

```text
E' = E cap { X^s_i = a }
```

with conditional probability at least `rho`, then the global path mass is
multiplied by `rho`; the terminal event is compatible with the projected shadow
pin `(i,a)` for sample label `s`; and no ambient-code fibre mass assertion is
being made.

Likewise, a long paid tuple prefix is safe only if its selector entropy is
charged and the terminal projection records enough coordinate pins for the
bound `lambda T + c R + B`.

## What This Does Not Prove

The theorem is only a mass-accounting interface.  It does not prove that the
sunflower transition system satisfies its hypotheses.

The remaining mathematical burden is to verify, for every local transition,
that all selector entropy is one of the following:

1. charged to terminal projected coordinate pins counted by `T(Theta)` and
   `R(Theta)`;
2. charged to pruning loss;
3. charged to a potential drop or assigned hash token;
4. absent from the projected terminal transcript.

In particular, high-alphabet value exposure is still dangerous.  If a branch
selects `a` from a nearly uniform alphabet of size `q`, the entropy cost is
about `log q`; this cannot be paid by a constant multiple of one pinned
coordinate.  The public-normal-form route must therefore route such high-entropy
choices to a fixed hash window or to a long-prefix terminal shadow whose paid
prefix has amortized cost.  This is precisely the local-interface burden left
open by the diagnostic scripts.
