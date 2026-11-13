# First implementation requirements

## Mathematical core

Implement cell state/design records, field and slope evaluation, exact finite contributions, identified joint changes, neutral split and equal-slope composition. Use an explicit numerical representation with a fixed exact denomination.

Keep complete joint value and individual attribution separate. Keep valuation separate from actor selection and physical feasibility.

## Existing EBU

Represent holdings and zero-sum transfers separately from physical contribution history. Any account constraints must be named assumptions. Do not add debt-based issuance or silently combine the after-action ideal with historical acceptance posting.

## Application constraints

Represent whole resource units and declared energy/capability bounds explicitly. Do not choose a final handling law, source dynamics, actor policy or admission/removal rule in this preparation stage.

## Initial mathematical checks

- Exact finite value agrees with accumulated current contributions for a declared path.
- Identified complete parallel contributions close once, including finite cross effects.
- Existing-unit transfers preserve their total.
- Neutral subdivision preserves stock, reference, inverse stiffness and field.
- Split/merge reversal restores K and x*.
- Unequal aggregation retains the residual field.
- A complete closed restored-state sequence has zero signed contribution.
- Whole-unit signs match the half-unit threshold and feasible domains.
- No source, capacity or power budget is copied by subdivision.
- Bounded allocation agrees with the conditional continuous and whole-unit results in EBU Real Limits.

These checks verify implementation of stated equations. Experimental growth, recovery, efficiency and actor behaviour require a separately specified study.
