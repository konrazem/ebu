"""Candidate procedure identities: Layer M.

Each identity is the SHA-256 of an explicit, ordered preimage of source bytes
and declared configuration.  These are *candidate* identities for the isolated
v5 package; they neither overwrite nor interact with any ``e1a_v4`` identity.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Mapping, Sequence

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

#: Modules entering the analysis-procedure identity, in fixed order.
ANALYSIS_MODULES: tuple[str, ...] = (
    "__init__.py",
    "numerics.py",
    "units.py",
    "refusals.py",
    "packets.py",
    "branch_a.py",
    "reduction.py",
    "observation.py",
    "likelihood.py",
    "optimize.py",
    "gates.py",
    "diagnostics.py",
    "confidence.py",
    "realization.py",
    "verdict.py",
    "estimate.py",
)

#: Modules entering the synthetic-generator identity.
GENERATOR_MODULES: tuple[str, ...] = ("rng.py", "generate.py")

#: Modules entering the validation-procedure identity.
#:
#: ``validation/run.py`` is included deliberately and is the V3 repair of a
#: material defect: it carries the result-counting and release semantics, so
#: changing how a complete success is counted MUST change the validation
#: identity.  Under V2 it did not, and the counting logic could be altered
#: without any identity moving.
#:
#: ``verdict.py`` is likewise included: the authoritative success predicate
#: lives there, and the power runner now delegates to it.
VALIDATION_MODULES: tuple[str, ...] = (
    "seeds.py",
    "identity.py",
    "verdict.py",
    os.path.join("validation", "__init__.py"),
    os.path.join("validation", "plan.py"),
    os.path.join("validation", "cases.py"),
    os.path.join("validation", "harness.py"),
    os.path.join("validation", "run.py"),
)

#: Modules whose bytes define the frozen gate and diagnostic semantics.
GATE_MODULES: tuple[str, ...] = (
    "gates.py",
    "diagnostics.py",
    "confidence.py",
    "realization.py",
)


def _file_digest(relpath: str) -> tuple[str, str]:
    path = os.path.join(PACKAGE_DIR, relpath)
    with open(path, "rb") as fh:
        data = fh.read()
    return relpath, hashlib.sha256(data).hexdigest()


def module_digests(modules: Sequence[str]) -> list[tuple[str, str]]:
    return [_file_digest(m) for m in modules]


def identity_of(modules: Sequence[str], configuration: Mapping[str, object] | None = None) -> str:
    """SHA-256 over ``relpath || file-sha256`` in fixed order, then the configuration.

    The preimage is fully determined by the listed module bytes and the exact
    canonical JSON of the configuration; nothing ambient enters it.
    """
    h = hashlib.sha256()
    for rel, digest in module_digests(modules):
        h.update(rel.encode("utf-8"))
        h.update(b"\x00")
        h.update(digest.encode("ascii"))
        h.update(b"\x00")
    payload = json.dumps(configuration or {}, sort_keys=True, separators=(",", ":"))
    h.update(payload.encode("utf-8"))
    return h.hexdigest()


def hierarchical_identity(
    modules: Sequence[str],
    component_ids: Mapping[str, str],
    configuration: Mapping[str, object] | None = None,
) -> str:
    """Identity over module bytes PLUS named component identities.

    Hierarchical binding (V-stage brief section 25): the validation identity
    depends on the analysis, generator, seed-map and gate identities as well as
    on its own runner and harness bytes, so a change anywhere in the chain that
    can affect a validation outcome moves it.
    """
    h = hashlib.sha256()
    for rel, digest in module_digests(modules):
        h.update(rel.encode("utf-8"))
        h.update(b"\x00")
        h.update(digest.encode("ascii"))
        h.update(b"\x00")
    for name in sorted(component_ids):
        h.update(b"component:")
        h.update(name.encode("utf-8"))
        h.update(b"\x00")
        h.update(component_ids[name].encode("ascii"))
        h.update(b"\x00")
    payload = json.dumps(configuration or {}, sort_keys=True, separators=(",", ":"))
    h.update(payload.encode("utf-8"))
    return h.hexdigest()


@dataclass(frozen=True)
class Identities:
    analysis: str
    generator: str
    validation: str
    packet_schema: str
    seed_map: str
    gates: str

    def as_dict(self) -> dict[str, str]:
        return {
            "analysis_procedure": self.analysis,
            "synthetic_generator": self.generator,
            "validation_procedure": self.validation,
            "packet_schema": self.packet_schema,
            "seed_map": self.seed_map,
            "gate_semantics": self.gates,
        }


def validation_preimage() -> dict[str, object]:
    """The exact documented preimage of the validation-procedure identity."""
    return {
        "modules": list(VALIDATION_MODULES),
        "bound_component_identities": [
            "analysis_procedure",
            "synthetic_generator",
            "seed_map",
            "gate_semantics",
            "packet_schema",
        ],
        "rationale": {
            "validation/run.py": "result counting and release semantics",
            "verdict.py": "authoritative success predicate",
            "validation/harness.py": "record execution and gate evaluation",
            "validation/cases.py": "case generation and replicate counts",
            "validation/plan.py": "design point and smoke configuration",
            "seeds.py": "seed interpretation",
            "identity.py": "the identity rule itself",
        },
    }


def compute_identities(configuration: Mapping[str, object] | None = None) -> Identities:
    analysis = identity_of(ANALYSIS_MODULES, configuration)
    generator = identity_of(GENERATOR_MODULES, configuration)
    packet_schema = identity_of(("packets.py", "units.py", "refusals.py"), configuration)
    seed_map = identity_of(("seeds.py", "rng.py"), configuration)
    gates = identity_of(GATE_MODULES, configuration)
    validation = hierarchical_identity(
        VALIDATION_MODULES,
        {
            "analysis_procedure": analysis,
            "synthetic_generator": generator,
            "seed_map": seed_map,
            "gate_semantics": gates,
            "packet_schema": packet_schema,
        },
        configuration,
    )
    return Identities(
        analysis=analysis,
        generator=generator,
        validation=validation,
        packet_schema=packet_schema,
        seed_map=seed_map,
        gates=gates,
    )
