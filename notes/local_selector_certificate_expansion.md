# Local Selector Certificate Expansion

This note expands the local selector rows used by the public-normal-form
ledger.  It is meant as a proof skeleton for replacing a table entry by
explicit entropy inequalities.

Throughout, all laws are conditional laws at the reached public node.  Public
tie-breaks have zero conditional entropy.  Only the first non-public selector is
charged.

## Lemma 1: Constant-heavy atom selectors

Let `p` be a finite probability law and fix `theta > 0`.  Let

```text
H_theta = {a : p(a) >= theta}.
```

If a branch selector chooses either one atom `a in H_theta` or the complement,
then the selector entropy is at most

```text
log(1 + floor(1/theta)).
```

If a retained atom branch fixes `A=a`, then its conditional mass is at least
`theta`, and the branch can be terminalized as a projected tuple pin with fixed
local cost `log(1/theta)`.

### Proof

The set `H_theta` has at most `1/theta` elements.  The selector alphabet
therefore has at most `1 + floor(1/theta)` outcomes.  On an atom branch,
`-log p(a) <= log(1/theta)`.

## Lemma 2: Heavy-or-light hash selector

Let `p` be a finite probability law and fix `0 < rho, tau <= 1`.  Put

```text
H = {a : p(a) >= rho*tau},       L = H^c.
```

Then every atom branch in `H` is a constant-mass terminal pin.  On `L`, either
`p(L) < rho`, in which case discarding `L` has pruning loss `-log(1-p(L))`,
or `p(L) >= rho`, in which case the conditional law `p(. | L)` has collision
at most `tau`.

### Proof

The first sentence is Lemma 1 with `theta = rho*tau`.  If `p(L) < rho`, the
retained complement has mass at least `1-rho`, so the pruning-normalization loss
is

```text
-log(1-p(L)) <= 2 rho
```

for `rho <= 1/2`.  If `p(L) >= rho`, then every atom in `L` has mass
`< rho*tau`, and

```text
Coll(p(. | L))
 = sum_{a in L} (p(a)/p(L))^2
 <= max_{a in L} p(a) / p(L)
 <= tau.
```

Thus the light retained branch is a genuine low-collision coordinate for the
actual conditional law of the selected sample coordinate.

## Lemma 3: Amortized prefix selectors

Let a stopped prefix selector output finite words `u` with lengths `l(u)` under
a law `P`.  If every retained output satisfies

```text
-log P[U = u] <= lambda l(u) + b,
```

then

```text
H(U) <= lambda E l(U) + b.
```

If the word consists of tuple-coordinate values and each entropy-bearing value
is projected to one sample-label coordinate pin, then the prefix selector is
paid by `lambda T(Theta) + b`, where deterministic repeats are discarded before
counting `T`.

### Proof

Average the displayed pointwise bound:

```text
H(U) = E[-log P(U)] <= lambda E l(U) + b.
```

For tuple prefixes, the terminal event is contained in the intersection of the
chosen sample-label coordinate cylinders.  Exact repeats either have zero
conditional entropy or zero branch mass.  Therefore the number of
entropy-bearing prefix variables is at most the projected coordinate count.

## Lemma 4: Public set-event increments inside a hash transcript

Suppose a public coordinate has already been selected and a public set event
`A in S` is appended to a labelled hash-window transcript.  If the retained
conditional mass is at least `rho`, then the added transcript entropy is at most
`log(1/rho)`.  If appending the set event would exceed the remaining window
budget, the event is not appended and the branch terminalizes on the already
paid value prefix.

### Proof

Conditioning on a retained public set of mass at least `rho` costs at most
`log(1/rho)` in the leaf transcript.  The stopped-window rule is deterministic:
overflow is checked before appending the set event, so the continuing hash
branch never has a transcript exceeding `B_win`.

## Lemma 5: DRC and role selectors

At fixed density `delta`, a DRC block of size `s` can be selected publicly with
conditioning cost

```text
O_delta(s).
```

If the only private refinement is a three-role vector on the selected block,
the role selector costs at most `s log 3`; taking a majority role produces a
subblock of size at least `s/3`.

### Proof

The public tie-break chooses the first valid DRC block in the fixed order, so
the block identity is a deterministic function of the current public law.  The
conditioning atom has mass at least `exp(-O_delta(s))` by the one-row DRC
estimate, which is the stated cost.  The role vector has at most `3^s`
possible values, and one role occupies at least one third of the coordinates.

## Lemma 6: Fixed-window Renyi copy charge

Let `K` be the public key/transcript of one labelled hash window and suppose
`H(K) <= B_win`.  Let `G` be the good-key event with conditional probability at
least `1/2`.  Then

```text
H_3(K | G) <= H(K | G) <= 2 B_win + O(1).
```

For three conditioned copies, the key-sharing cost is therefore

```text
2 H_3(K | G) + O(1) = O(B_win).
```

The split exposure on a fixed block of size `h` has cost at most

```text
log sum_{r <= 6 beta h} binom(h,r) <= h log 2.
```

Thus one completed labelled hash window has total local charge

```text
C_hash = O(B_win + h + 1).
```

### Proof

Renyi entropy decreases with order, so `H_3 <= H`.  Conditioning on an event of
probability at least `1/2` gives

```text
H(K | G) <= H(K)/Pr(G) + log 2 <= 2 B_win + O(1).
```

The random-transcript conditioned-copy lemma with `m=3` contributes
`(m-1)H_m = 2H_3`.  The remaining split exposure is a subset choice inside a
fixed `h`-set.

## Lemma 7: Old-window non-value selectors

Fix the revisit cap `Q`, reservoir size `r_*`, scale class, and sample-label
signature.  If high-symbol old values are not exposed on continuing branches,
then the remaining old-window selectors have a finite per-incidence alphabet.
Consequently there is a constant `C_old(Q,r_*)` such that a branch registering
`n` old incidences has non-value old selector entropy at most

```text
C_old(Q,r_*) n.
```

### Proof

The allowed continuing data are finite: sample-label signature, five-state
equality pattern, three-role refinement, scale class, bounded reservoir labels,
and queue-flush markers.  The old-symbol value vector itself is either
terminal-local in the low-symbol case or is not exposed in the continuing
high-symbol case.  Since every continuing block registers at least one old
incidence and no coordinate is registered more than `Q` times before
high-revisit exit, the finite selector cost is linear in the incidence count.

## Lemma 8: Local row verification

Every local selector row in the current transition system is paid by one of
the preceding lemmas:

```text
terminal value pin             -> Lemma 1 or Lemma 3
collision/high-revisit exit    -> Lemma 2, not the non-exhaustive shorthand
positive-KL heavy/tail branch  -> Lemmas 2, 3, 4
first-crossing branch          -> Lemmas 2, 3, 4
hash survival heavy atom       -> retained atom + constant pruning loss
hash return                    -> Lemma 6
fresh bounded residual         -> finite q-pattern + fresh potential
old residual/window            -> Lemma 7
DRC/split/scale                -> Lemma 5 + scale/rank certificate
low-symbol old terminal        -> terminal shadow entropy by its low-symbol cap
copy/reservoir labels          -> fixed reservoir plus Lemma 6 when copied
```

Therefore the only remaining non-formal step is not an entropy inequality, but
the transition-system coverage assertion: every possible nonterminal state must
enter exactly one of these rows and every child carrying recurrence potential
must have a valid rank/scale/fresh/old/hash-token certificate.
