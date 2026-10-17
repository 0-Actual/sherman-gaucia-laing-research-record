<!-- Proposed review derivative; not installed or submitted. Original OpenAI source: lean/docs/342.md. Apache-2.0. -->

> The scope description below is adapted from OpenAI. This review has not independently executed the formal proof. Links are expanded for this standalone copy; the diff retains upstream-relative paths.

# Donaldson's tamed-to-compatible conjecture

The following describes the scope of the Lean formalization related to the following accompanying paper(s):

- [Taming implies compatibility on four-manifolds, revised edition](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/Taming-implies-compatibility-on-four-manifolds-October-6-2026/paper.pdf)
- [Previously cited September 23 edition](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/Taming-implies-compatibility-on-four-manifolds-September-23-2026/paper.pdf)

## Scope

Donaldson's tamed-to-compatible conjecture asks whether an almost-complex structure tamed by a symplectic form also admits a compatible symplectic form. The formalized result establishes this for every closed connected smooth four-manifold, keeping the almost-complex structure fixed. No integrability assumption or prescribed cohomology class for the compatible form is required.

## Version scope

The October 6 edition corrects the discussion of compatible and tamed cones. The formalized result described above concerns the existence of a compatible symplectic form. This scope note does not certify every secondary cone identity in either manuscript edition. The previous edition remains linked for the revision record.

## Comparator links

| Result | Comparator statement |
| --- | --- |
| Taming implies compatibility | [TamingCompatibility.lean](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/ComparatorChallenges/TamingCompatibility.lean) |
