# Demand-driven rehearsal artifact

**CLASS: REHEARSAL / NON-CONFIRMATORY. NOT SCIENTIFIC EVIDENCE.**

`DEMAND_DRIVEN_REHEARSAL.json.gz` is the output of `demand_driven_rehearsal.py`
for model `EBU-DEMAND-DRIVEN-ECONOMY-v1`. It exists to show that the machinery
runs end to end and replays exactly, and for nothing else.

No hypothesis is registered here, no comparison is preregistered, no seed is
selected, and no number in this artifact may be cited as a finding about
whether the demand-driven economy restores, is safe under a hostile actor, or
differs from its comparator. The model is not tuned to anything in it.

What it does establish, and all it establishes:

- 3,200 epochs across four policies and four replicates complete without
  refusal;
- the replay reproduces every scientific column exactly;
- the package code identity is unchanged between the run and the replay;
- accounting, conservation, nonnegativity, separability and capacity-source
  residuals are all exactly zero, with tolerance literally zero;
- the economic arrival sequence is identical under all four policies, as the
  stream-separation contract requires.

Registered artifacts live in `results/stage_a/`, `results/stage_b/` and
`results/homeostasis/`. This directory is not one of them.
