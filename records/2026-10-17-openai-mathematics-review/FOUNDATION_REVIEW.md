# Foundation review: finite capacity and the ideal-density coefficient

## Purpose and limits

The reviewed manuscript is OpenAI's *The first lattice correction to Bloch's law*,
October 5, 2026, in family 271. Its central claim concerns an interacting,
infinite-volume quantum system at fixed positive half-integer spin. The present
completed checks concern a finite-dimensional lemma and a coefficient in the
ideal comparison model. The random-environment estimates linking them to the
interacting system remain unverified here.

## Definitions and invariant

Let U be a nonnegative matrix whose row sums and column sums are at most one,
with zero rows and columns at the killing coordinates K. Transitions act on
column distributions. Set A=I-U. For real z define e(z)=z^T A z.
The row/column bounds imply ||U||_2<=1, so e(z)>=0. Equivalently its symmetric
energy matrix is G=I-(U+U^T)/2, which is positive semidefinite.

Fix a target i outside K. Let f_j be the probability of ever hitting i before
killing, starting at j, and take f_i=1. Let q be the probability of returning to i
after at least one step. Coordinates in a disjoint recurrent class have hitting
probability zero. Almost-sure killing is not assumed.

For a trial h with h_i=1 and h_K=0, a scalar c, and the target unit vector eta,
define mu_plus=Uh-h+c*eta and mu_minus=U^T h-h+c*eta. Set y=f-h.

## Algebra checked

The first-step hitting equations give A^T f=(1-q)*eta. Subtracting the adjoint
trial equation yields A^T y=(1-q-c)*eta+mu_minus. Because y_i=0,

    e(y) = y^T mu_minus.

Also 1-q=(A^T f)^T h=f^T Ah=c-f^T mu_plus, hence

    q-(1-c) = h^T mu_plus + y^T mu_plus.

These identities use the adjoint in the hitting equation. Replacing it with the
forward operator is generally invalid for a non-symmetric U. The independent
checks include four scenarios that detect that incorrect substitution.

Let M>=||h||_infinity. Assume X,epsilon>=0 and, for each residual,
|mu^T z|<=X*sqrt(e(z))+epsilon for every z with z_K=0 and
||z||_infinity<=1+M. Since 0<=f<=1, y=f-h belongs to this test class.
The first identity gives sqrt(e(y))<=X+sqrt(epsilon). Substitution
in the second yields the paper's bound

    |q-(1-c)| <= |h^T mu_plus| + 2*X^2 + 2*epsilon.

No symmetry or invertibility of A was introduced. This is a direct algebraic
review of the stated finite lemma, not a claim about all later estimates.

## Independent exact checks

The evaluator uses rational arithmetic and solves first-step equations only on
states that can reach the target. It covers immediate killing, a self loop,
non-symmetric transitions, leakage, a closed cycle, a disjoint recurrent class,
explicit killed coordinates, and an absorbing target. There are eight transition
scenarios, each with nine trial/scalar combinations: 72 parameter cases, not
72 separate theorems or independent discoveries.

All 72 satisfy the checked identities. In 60, solving G*x=mu supplies a zero-slack
energy-dual certificate and the stability bound also passes. The remaining 12
have no certificate under that particular zero-slack construction; their
`stability_bound_checked=false` fields mean unperformed subchecks, not failures
of the identities or counterexamples to the lemma. Hand-derived hitting values
and the wrong-adjoint negative control check the evaluator's orientation.

## Ideal-density coefficient

For t=beta*S and nearest-neighbor dispersion, the one-coordinate return kernel is

    I(t)=(1/(2*pi))*integral[-pi,pi] exp(-2*t*(1-cos k)) dk.

After u=sqrt(t)*k, the exponent is -u^2+u^4/(12*t)+O(u^6/t^2).
The Gaussian fourth-moment ratio is 3/4, giving the relative coefficient 1/16.
Cubing the three coordinate factors multiplies this coefficient by three:

    I(t)^3=(4*pi*t)^(-3/2)*(1+3/(16*t)+O(t^(-2))).

The controlled Gaussian tail and Taylor remainder support the estimate uniformly
for t>=1. Summing it at n*t over n>=1 produces the ideal density

    zeta(3/2)/(8*pi^(3/2))*t^(-3/2)
      +3*zeta(5/2)/(128*pi^(3/2))*t^(-5/2) + O(t^(-7/2)).

The remainder is summable because sum n^(-7/2) converges. The rational coefficient
calculation agrees with the manuscript. This does not prove that the interacting
magnetization deficit differs from the ideal density by o(beta^(-5/2)); that is
the difficult comparison still to be reviewed.

## What remains

Review the conditional probability laws for pins and exposed cycles, the geometric
and heat-kernel estimates, signed cancellation, both energy residuals, and their
uniformity in volume and permitted pin sets. Then connect them to the pressure
argument, preserving volume limit first, right field derivative second, and low
temperature last. A finite zero-field symmetric system or a small quantum
simulation alone cannot certify spontaneous magnetization in that limit order.

The source review so far includes the complete finite-capacity section, profile
section, introduction and pressure section, plus partial scalar-estimate reading.
These readings and the checks are not a completed review of the full paper or its
companion dependencies. The formal proof execution remains separate work.

## Pinned source locations

- [main.tex](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/The-first-lattice-correction-to-Blochs-law-October-5-2026/build/main.tex)
- [sections/01-introduction.tex](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/The-first-lattice-correction-to-Blochs-law-October-5-2026/build/sections/01-introduction.tex)
- [sections/04-capacity.tex](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/The-first-lattice-correction-to-Blochs-law-October-5-2026/build/sections/04-capacity.tex)
- [sections/04-profiles.tex](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/The-first-lattice-correction-to-Blochs-law-October-5-2026/build/sections/04-profiles.tex)
- [sections/06-scalar.tex](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/The-first-lattice-correction-to-Blochs-law-October-5-2026/build/sections/06-scalar.tex)
- [sections/08-pressure.tex](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/The-first-lattice-correction-to-Blochs-law-October-5-2026/build/sections/08-pressure.tex)
