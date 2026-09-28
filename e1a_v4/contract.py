"""Fail-closed loading and authority binding of the adopted E1a v4 design contract.

The implementation binds itself to `docs/e1a/e1a_v4_design_contract.json`. Every
adopted constant is READ from there. Nothing in this package types a competing
value, and nothing falls back to a historical v3 default: a mismatch is a
Refusal, not a warning.

CLASSIFICATION
    load_contract, ContractBinding ... EXACT (byte-level hash comparison)
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any

from . import DESIGN_CONTRACT, DESIGN_DOCUMENT, FROZEN_FOUNDATION, WORKING_BASELINE
from .numerics import Refusal

SUPPORTED_CONTRACT_IDS = ("e1a_v4_prospective_design",)
SUPPORTED_MAJOR_MINOR = ("1.0", "1.1")
#: 1.1 adds the synthetic-validation release criteria (dispositions G1/G2) and a numeric
#: sigma_psi (disposition G3). It changes NO analysis decision rule; the coherence checks
#: below are unchanged and still enforced.

#: Keys whose absence makes the contract unusable. Fail closed, never default.
REQUIRED_TOP_LEVEL = (
    "contract_id", "contract_version", "authority", "scientific_target",
    "information_separation", "fields", "endpoints", "entropy_semantics",
    "mode_resolution", "complete_pipeline", "refusal_semantics",
    "forbidden_mechanisms", "authorization_boundaries",
)
REQUIRED_ENDPOINTS = ("P1_geometry", "P2_cross_field", "P3_absolute", "P4_entropy")


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


@dataclass(frozen=True)
class ContractBinding:
    """A validated contract plus the document identities it was bound against."""

    path: str
    sha256: str
    data: dict[str, Any]
    foundation_sha256: str
    baseline_sha256: str
    design_sha256: str

    # ---- adopted rules, read from the contract, never typed here -------------
    @property
    def delta_cross(self) -> float:
        return float(self.data["endpoints"]["P2_cross_field"]["delta_cross"])

    @property
    def z_cross(self) -> float:
        return float(self.data["endpoints"]["P2_cross_field"]["z_cross"])

    @property
    def delta_abs(self) -> float:
        return float(self.data["endpoints"]["P3_absolute"]["delta_abs"])

    @property
    def z_abs(self) -> float:
        return float(self.data["endpoints"]["P3_absolute"]["z_abs"])

    @property
    def alpha_geom(self) -> float:
        return float(self.data["endpoints"]["P1_geometry"]["alpha_geom"])

    @property
    def alpha_1(self) -> float:
        return float(self.data["endpoints"]["P1_geometry"]["alpha_1"])

    @property
    def alpha_2(self) -> float:
        return float(self.data["endpoints"]["P1_geometry"]["alpha_2"])

    @property
    def theta_cap_deg(self) -> float:
        return float(self.data["mode_resolution"]["theta_cap_deg"])

    @property
    def rank_tol(self) -> float:
        return float(self.data["refusal_semantics"]["rank_tol"])

    @property
    def pipeline_target(self) -> float:
        return float(self.data["complete_pipeline"]["target_true_bridge_success"])

    @property
    def fields(self) -> list[dict[str, Any]]:
        return list(self.data["fields"])

    @property
    def reference_field_id(self) -> str:
        refs = [f["id"] for f in self.fields if f.get("reference")]
        if len(refs) != 1:
            raise Refusal(f"contract must declare exactly one reference field, found {refs}")
        return refs[0]

    @property
    def forbidden_branch_a_routes(self) -> tuple[str, ...]:
        return tuple(self.data["information_separation"]["forbidden_branch_A_routes"])

    @property
    def authorised_branch_a_routes(self) -> tuple[str, ...]:
        return tuple(self.data["information_separation"]["authorised_branch_A_routes"])


def load_contract(
    root: str = ".",
    *,
    require_document_identities: bool = True,
) -> ContractBinding:
    """Load, validate and bind the contract. Refuses on any mismatch."""
    path = os.path.join(root, DESIGN_CONTRACT)
    if not os.path.exists(path):
        raise Refusal(f"design contract absent: {path}")
    digest = sha256_file(path)
    with open(path, encoding="utf-8") as handle:
        try:
            data = json.load(handle)
        except json.JSONDecodeError as exc:
            raise Refusal(f"design contract is not valid JSON: {exc}") from exc

    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            raise Refusal(f"contract missing required section {key!r}")
    if data["contract_id"] not in SUPPORTED_CONTRACT_IDS:
        raise Refusal(f"unsupported contract_id {data['contract_id']!r}")
    major_minor = ".".join(str(data["contract_version"]).split(".")[:2])
    if major_minor not in SUPPORTED_MAJOR_MINOR:
        raise Refusal(f"unsupported contract_version {data['contract_version']!r}")
    for name in REQUIRED_ENDPOINTS:
        if name not in data["endpoints"]:
            raise Refusal(f"contract missing endpoint {name!r}")

    binds = data["authority"]["binds"]
    identities: dict[str, str] = {}
    for key, declared_path in (
        ("frozen_foundation", FROZEN_FOUNDATION),
        ("working_baseline", WORKING_BASELINE),
        ("design_document", DESIGN_DOCUMENT),
    ):
        expected = binds[key]["sha256"]
        target = os.path.join(root, declared_path)
        if not os.path.exists(target):
            raise Refusal(f"bound document absent: {declared_path}")
        actual = sha256_file(target)
        if require_document_identities and actual != expected:
            raise Refusal(
                f"AUTHORITY IDENTITY MISMATCH for {declared_path}: "
                f"contract expects {expected}, file is {actual}. "
                "Refusing to continue with defaults."
            )
        identities[key] = actual

    binding = ContractBinding(
        path=path, sha256=digest, data=data,
        foundation_sha256=identities["frozen_foundation"],
        baseline_sha256=identities["working_baseline"],
        design_sha256=identities["design_document"],
    )

    # structural coherence of the adopted rules themselves
    if abs(binding.alpha_1 + binding.alpha_2 - binding.alpha_geom) > 1e-15:
        raise Refusal("contract incoherent: alpha_1 + alpha_2 != alpha_geom")
    if not 0.0 < binding.delta_cross < 1.0 or not 0.0 < binding.delta_abs < 1.0:
        raise Refusal("contract incoherent: margins must lie in (0, 1)")
    p2_mult = str(binding.data["endpoints"]["P2_cross_field"]["multiplicity_correction"])
    if not p2_mult.upper().startswith("NONE"):
        raise Refusal(
            f"contract incoherent: P2 must carry no multiplicity correction (IUT), got {p2_mult!r}"
        )
    if binding.data["endpoints"]["P3_absolute"]["applies_to"] != "EVERY tested field":
        raise Refusal("contract incoherent: P3 must apply to every tested field")
    if binding.data["endpoints"]["P4_entropy"]["classification"] != \
            "DETERMINISTIC PHYSICAL/THEORETICAL CONSISTENCY CHECK":
        raise Refusal("contract incoherent: P4 classification changed")
    binding.reference_field_id  # raises unless exactly one reference field
    return binding
