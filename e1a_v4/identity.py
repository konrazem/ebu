"""Deterministic procedure identity.

The configuration hash alone is NOT a procedure freeze: v3 hashed its config and
then changed the generator and the decision rules afterwards. The procedure
identity below binds the scientifically relevant implementation state.

CANONICALISATION RECIPE, exactly:
    1. build a mapping with these keys and no others:
         "implementation_identity"  -> e1a_v4.IMPLEMENTATION_IDENTITY
         "contract_sha256"          -> sha256 of the design contract file
         "design_sha256"            -> sha256 of the prospective design document
         "foundation_sha256"        -> sha256 of the frozen foundation
         "baseline_sha256"          -> sha256 of the working theory baseline
         "code"                     -> {relative path: sha256} for every module
                                       in SCIENTIFIC_MODULES, sorted by path
         "analysis_rules"           -> the adopted rule values read from the
                                       contract, sorted by key
         "configuration"            -> the caller's configuration mapping
         "seed_map_schema"          -> the declared future seed-family schema
    2. serialise with json.dumps(..., sort_keys=True, separators=(",", ":"),
       ensure_ascii=True)
    3. sha256 of the UTF-8 encoding of that string

No seed VALUES enter the identity at this stage; only the schema does, because
seeds are set in the authorised stochastic-validation stage.

CLASSIFICATION
    procedure_identity ... EXACT (deterministic function of declared inputs)
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Mapping

from . import IMPLEMENTATION_IDENTITY
from .contract import ContractBinding, sha256_file
from .seeds import SEED_MAP_SCHEMA

#: Modules whose content can change a scientific result. Ordered set, sorted on use.
SCIENTIFIC_MODULES = (
    "e1a_v4/__init__.py",
    "e1a_v4/branch_a.py",
    "e1a_v4/calibration.py",
    "e1a_v4/contract.py",
    "e1a_v4/effective_size.py",
    "e1a_v4/endpoints.py",
    "e1a_v4/geometry.py",
    "e1a_v4/identity.py",
    "e1a_v4/numerics.py",
    "e1a_v4/seeds.py",
    "e1a_v4/status.py",
    "e1a_v4/world.py",
)


def adopted_rules(binding: ContractBinding) -> dict[str, Any]:
    """The adopted decision-rule values, read from the contract."""
    return {
        "alpha_1": binding.alpha_1,
        "alpha_2": binding.alpha_2,
        "alpha_geom": binding.alpha_geom,
        "delta_abs": binding.delta_abs,
        "delta_cross": binding.delta_cross,
        "field_ids": [f["id"] for f in binding.fields],
        "pipeline_target": binding.pipeline_target,
        "rank_tol": binding.rank_tol,
        "reference_field": binding.reference_field_id,
        "theta_cap_deg": binding.theta_cap_deg,
        "z_abs": binding.z_abs,
        "z_cross": binding.z_cross,
    }


def procedure_preimage(
    binding: ContractBinding,
    configuration: Mapping[str, Any] | None = None,
    root: str = ".",
) -> str:
    code = {path: sha256_file(os.path.join(root, path)) for path in sorted(SCIENTIFIC_MODULES)}
    payload = {
        "implementation_identity": IMPLEMENTATION_IDENTITY,
        "contract_sha256": binding.sha256,
        "design_sha256": binding.design_sha256,
        "foundation_sha256": binding.foundation_sha256,
        "baseline_sha256": binding.baseline_sha256,
        "code": code,
        "analysis_rules": adopted_rules(binding),
        "configuration": dict(configuration or {}),
        "seed_map_schema": SEED_MAP_SCHEMA,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def procedure_identity(
    binding: ContractBinding,
    configuration: Mapping[str, Any] | None = None,
    root: str = ".",
) -> str:
    return hashlib.sha256(procedure_preimage(binding, configuration, root).encode("utf-8")).hexdigest()
