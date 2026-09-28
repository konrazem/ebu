# E1a v4 pre-execution correction candidate

> **ADOPTED — see `docs/e1a/E1A_V4_PREEXEC_CORRECTION_ADOPTION_REPORT.md`.**
> Every critical claim below was independently reproduced before adoption. The text is
> preserved verbatim as the auditor wrote it; only this banner was added. Two figures in
> it are superseded by the adoption report: the `696` local check total omitted the
> bounded-implementation suite and counted the correction gate's three *groups* as
> checks, and the correction gate now reports **37** numbered checks rather than three
> groups. `execution_authorised` remains `false` and the campaign driver is still not
> implemented, exactly as the candidate says.

**Status: local correction candidate; not adopted or frozen; no execution permission.**
*(superseded by the banner above: adopted at the commit named in the adoption report)*

Starting commit: `c1f2ca13693c6f23e31c9828e063876c500012bf`.

The independent clearance audit found a rotated-OU defect that could change the
scientific answer. The former generator applied unequal modal relaxation factors
to laboratory coordinates. For a rotated anisotropic field, this does not
preserve the declared covariance. The candidate generator now evolves independent
eigenmodes of `H_true` and rotates them back. It also pairs each relaxation time
with the ascending eigenvalue order. A pure algebraic regression checks
`A Sigma A^T + Q = Sigma` and demonstrates that the former recurrence violates it.
No trajectory was generated to validate this correction.

Other candidate corrections:

- C2 and C7 cannot pass with missing field/alternative rows; G2's direct helper
  also refuses an incomplete alternative map.
- The calibration lock refuses an absent or mismatched separately supplied
  realised condition. The future driver must still show that this condition
  was constructed from its own Branch-A measurement; a caller passing a copied
  artifact condition is not an independent physical provenance proof.
- Seed scopes are limited to each case's frozen `fields_affected` list. The
  experiment-shared scope is limited to the Branch-A measurement family. C6
  uses its one declared synthetic-field descriptor as its field-scope token and
  cannot borrow a theta0 stream. The resulting authorised stream inventory is
  **166,600 expected / 166,600 unique / zero collisions** under static per-case
  enumeration. The older 204,000 count was a broader Cartesian product that
  included fields C6 does not declare and experiment scopes in other families.
- The human-readable output schema now says `/2`, like the existing JSON and
  implementation, and includes subcondition and scope in the reproduction recipe.
- Calibration request construction refuses a relaxation-time ordering that
  cannot pair with the measured `H_A` eigenmodes under the declared isotropic
  Stokes-drag rule.

The JSON plan, contract, seed map and analysis-layer source are untouched.
`execution_authorised` remains `false`. The official runner still has no campaign
driver. A passing static preflight is **not** an execution clearance. Before any
campaign, independently review these corrections and C6's literal scope token,
complete and audit the driver, version/reseal the package with its new code and
documentation hashes, and separately authorize execution. Do not change frozen
scientific thresholds or use observed outcomes to choose a correction.

Local validation: eight static/pure checks reported 696 passes and zero failures;
the new correction gate consists of three groups. The original JSON plan SHA-256
remains `db4ba663c21945413d94de02062e21263e42a9ea4d0432ac9bb749a1bf9d165d`;
the seed-map SHA-256 remains
`95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce`.
The candidate code changes the computed validation execution identity; it has
not been adopted as the frozen one. RNG objects, random draws, trajectories and
campaign jobs executed in this correction stage: **zero**. No commit or push.
