"""The central typed case dispatcher.

Every validation case maps through exactly one path::

    case_id -> ValidationCaseV4 -> CaseInstantiation -> generated world

There is no nominal fallback.  A case ID the dispatcher does not recognise is
an invalid plan, not a nominal run, and a declared configuration field that no
handler consumes raises rather than being ignored.  Under V3 the dispatcher
was an ``if`` chain over case IDs inside the runner, and three cases
(``POWER-CONDLIM``, ``POWER-NOISEHI`` and several field-specific controls)
declared a world nothing read, so they generated nominal records under a
non-nominal name.

:meth:`CaseInstantiation.digest` records what was actually built, including
measured properties of the generated world, so a validation result carries
evidence that it ran the world it claims.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from .. import numerics as nm
from ..generate import GeneratorSpec
from ..numerics import NumericalFailure
from ..observation import bandwidth_product, localization_ratio
from .cases import CASES_BY_ID, CaseConfig, ExpectedEvent, ValidationCaseV4
from . import plan


class InvalidValidationPlan(Exception):
    """A case is unknown, or declares a world no handler consumes."""


#: Driver families the dispatcher can actually execute.
DRIVER_SINGLE_RECORD = "single_record"
DRIVER_COMPLETE = "complete_experiment"
DRIVER_DETERMINISTIC = "deterministic"
DRIVER_CALIBRATION = "finite_n_calibration"
DRIVER_CONTRAST = "multi_record_contrast"
DRIVER_GATE_BOUNDARY = "gate_boundary"

#: Drivers that exist in this build.  A case routed to any other driver is
#: reported NOT RUN; it is never silently executed as a nominal case.
IMPLEMENTED_DRIVERS = frozenset(
    {DRIVER_SINGLE_RECORD, DRIVER_COMPLETE, DRIVER_DETERMINISTIC}
)


@dataclass(frozen=True)
class CaseInstantiation:
    """The concrete world one case asks for."""

    case_id: str
    driver: str
    #: Keyword arguments for :func:`~e1a_v5.validation.harness.design_specs`.
    spec_kwargs: Mapping[str, Any] = field(default_factory=dict)
    #: True absolute log beta imposed on the single-record driver.
    b_true: float | None = None
    #: Hidden Branch-A scale applied to the locked H.
    blind_scale: float | None = None
    #: Geometry perturbation applied to the locked H / true H.
    geometry: str | None = None
    #: Post-generation selection applied to the observed record.
    selection: str | None = None
    #: Declared calibration standard uncertainty for the absolute endpoint.
    sigma_cal: float | None = None
    #: Deterministic battery key, when the case is exact.
    deterministic_key: str | None = None
    #: Generate from the full 3D hidden-memory world.
    axial_memory: bool = False
    #: Analyse with a C_phi that omits the shared thermometry dependency.
    omit_eta_t_covariance: bool = False
    #: Which declared config fields this instantiation consumed.
    consumed: tuple[str, ...] = ()
    #: Why a recognised case is not executable in this build.
    not_run_reason: str = ""

    @property
    def runnable(self) -> bool:
        return self.driver in IMPLEMENTED_DRIVERS and not self.not_run_reason

    def digest(self, specs: Sequence[tuple[GeneratorSpec, Any]] | None = None) -> dict:
        """A compact record of the world that was actually instantiated.

        Measured, not declared: the achieved localisation ratio, bandwidth
        product and exposure fraction are read back off the generated spec, so
        a case that declared a world and built a nominal one is visible in its
        own result.
        """
        out: dict[str, Any] = {
            "case_id": self.case_id,
            "driver": self.driver,
            "consumed": list(self.consumed),
            "declared": dict(self.spec_kwargs),
            "b_true": self.b_true,
            "blind_scale": self.blind_scale,
            "geometry": self.geometry,
            "selection": self.selection,
            "sigma_cal": self.sigma_cal,
            "axial_memory": self.axial_memory,
            "omit_eta_t_covariance": self.omit_eta_t_covariance,
        }
        if specs:
            spec, h_locked = specs[0]
            sigma = nm.spd_inverse(spec.h_true)
            out["measured"] = {
                "localization_ratio": localization_ratio(
                    sigma, spec.r_obs, spec.p_matrix),
                "exposure_over_dt": spec.t_exp / spec.dt if spec.dt else None,
                "condition_h_true": nm.cond2_spd(spec.h_true),
                "omega_true": spec.omega_true,
                "noise_model": spec.noise_model,
                "drift_rate": list(spec.drift_rate),
                "generate_t_exp": spec.generate_t_exp,
                "n_frames": spec.n_frames,
                "beta_true_by_field": [s.beta_true for s, _ in specs[:4]],
            }
        return out


def _route(cfg: CaseConfig, event: ExpectedEvent) -> tuple[str, dict, dict, list[str]]:
    """Map a typed config to (driver, spec kwargs, extras, consumed names)."""
    spec: dict[str, Any] = {}
    extra: dict[str, Any] = {}
    consumed: list[str] = []

    def take(name: str, into: dict | None = None, key: str | None = None,
             transform: Callable[[Any], Any] | None = None) -> Any:
        v = getattr(cfg, name)
        if v is None:
            return None
        consumed.append(name)
        if into is not None:
            into[key or name] = transform(v) if transform else v
        return v

    take("noise_ratio", spec, "localization_ratio_target")
    take("exposure_fraction", spec, "exposure_fraction")
    take("condition", spec, "condition_target")
    take("r_irr_target", spec, "r_irr_target")
    take("axial_coupling", spec, "coupling")
    take("noise_model", spec, "noise_model")
    take("blur_mismatch", spec, "blur_mismatch")
    take("drift_rate", spec, "drift_rate", lambda v: tuple(v))

    betas = take("betas")
    common = take("beta_common")
    if betas is not None and common is not None:
        raise InvalidValidationPlan("a case may declare betas or beta_common, not both")
    if betas is not None:
        spec["beta_by_field"] = tuple(betas)
    elif common is not None:
        spec["beta_by_field"] = (common,) * 4

    take("blind_scale", extra)
    take("geometry", extra)
    take("selection", extra)
    take("sigma_cal", extra)
    take("b_true", extra)

    # Gate-boundary size cases place the TRUE value of a gate statistic on its
    # tolerance.  Only the current gate has a constructor for that in this
    # build; the geometry and centre boundaries need the gate-boundary driver.
    r_true = take("r_irr_true")
    if r_true is not None:
        spec["r_irr_target"] = r_true

    take("axial_memory", extra)
    take("omit_eta_t_covariance", extra)

    driver = DRIVER_COMPLETE
    if event is ExpectedEvent.DETERMINISTIC or event is ExpectedEvent.REALIZATION_STATUS:
        # The case's declared event decides the driver, so a case exercised by
        # the exact battery can never also be routed to a stochastic driver.
        consumed.extend(
            n for n in ("realization", "optimiser_failure")
            if getattr(cfg, n) is not None
        )
        extra["deterministic_key"] = (
            cfg.realization or cfg.optimiser_failure or "exact"
        )
        driver = DRIVER_DETERMINISTIC
    elif cfg.realization is not None or cfg.optimiser_failure is not None:
        consumed.extend(
            n for n in ("realization", "optimiser_failure")
            if getattr(cfg, n) is not None
        )
        extra["deterministic_key"] = cfg.realization or cfg.optimiser_failure
        driver = DRIVER_DETERMINISTIC
    elif cfg.statistic is not None:
        consumed.append("statistic")
        driver = DRIVER_CALIBRATION
    elif cfg.contrast_true is not None:
        consumed.append("contrast_true")
        driver = DRIVER_CONTRAST
    elif cfg.g_true is not None or cfg.m_true is not None:
        consumed.extend(n for n in ("g_true", "m_true") if getattr(cfg, n) is not None)
        driver = DRIVER_GATE_BOUNDARY
    elif cfg.b_true is not None:
        driver = DRIVER_SINGLE_RECORD
    return driver, spec, extra, consumed


NOT_RUN_REASONS = {
    DRIVER_CONTRAST: "requires the multi-record contrast driver",
    DRIVER_GATE_BOUNDARY: "requires the geometry/centre gate-boundary driver",
    DRIVER_CALIBRATION: "finite-N critical-value calibration is not run in V4",
}


def instantiate(case_id: str) -> CaseInstantiation:
    """Resolve a case ID to its concrete world. Unknown IDs are a hard error."""
    if case_id not in CASES_BY_ID:
        raise InvalidValidationPlan(
            f"unknown validation case {case_id!r}; an unrecognised case is an "
            "invalid plan, never a nominal run"
        )
    case = CASES_BY_ID[case_id]
    driver, spec, extra, consumed = _route(case.config, case.expected_event)
    declared = set(case.config.declared_fields())
    missed = sorted(declared - set(consumed))
    if missed:
        raise InvalidValidationPlan(
            f"{case_id} declares {missed} but no handler consumes them; a "
            "declared world must be instantiated, not ignored"
        )
    return CaseInstantiation(
        case_id=case_id,
        driver=driver,
        spec_kwargs=spec,
        b_true=extra.get("b_true"),
        blind_scale=extra.get("blind_scale"),
        geometry=extra.get("geometry"),
        selection=extra.get("selection"),
        sigma_cal=extra.get("sigma_cal"),
        deterministic_key=extra.get("deterministic_key"),
        axial_memory=bool(extra.get("axial_memory")),
        omit_eta_t_covariance=bool(extra.get("omit_eta_t_covariance")),
        consumed=tuple(sorted(consumed)),
        not_run_reason=NOT_RUN_REASONS.get(driver, ""),
    )


def apply_geometry(
    kind: str, spec: GeneratorSpec, h_locked
) -> tuple[GeneratorSpec, Any]:
    """Apply a declared geometry perturbation to one record.

    ``trace_preserving`` stretches one locked eigenvalue and shrinks the other
    by the same factor, so a scalar beta remains plausible and only the T4
    shape statistic can see it.  ``rotation`` keeps the true eigenvalues and
    rotates the true axes away from the locked ones.
    """
    if kind == "trace_preserving":
        vals, q = nm.eigh(h_locked)
        new = nm.symmetrise(nm.matmul(nm.matmul(
            q, [[vals[0] * 1.6, 0.0], [0.0, vals[1] / 1.6]]), nm.transpose(q)))
        return spec, new
    if kind == "rotation":
        theta = math.pi / 5.0
        r = nm.mat([[math.cos(theta), -math.sin(theta)],
                    [math.sin(theta), math.cos(theta)]])
        base = nm.mat([[spec.h_true[0][0] * 1.5, 0.0],
                       [0.0, spec.h_true[1][1] / 1.5]])
        rotated = nm.symmetrise(nm.matmul(nm.matmul(r, base), nm.transpose(r)))
        return type(spec)(**{**spec.__dict__, "h_true": rotated}), base
    raise InvalidValidationPlan(f"unknown geometry perturbation {kind!r}")


#: Selection control: frames whose whitened radius exceeds this are dropped,
#: which is exactly the tracking failure the control exists to detect.
SELECTION_RADIUS = 1.5


def apply_selection(kind: str, y, spec: GeneratorSpec):
    """Apply a declared observation selection to a generated record."""
    if kind != "clipping":
        raise InvalidValidationPlan(f"unknown selection {kind!r}")
    sigma = nm.spd_inverse(spec.h_true)
    w = nm.inv_sqrtm_spd(sigma)
    kept = []
    for row in y:
        d = [row[i] - spec.b_det[i] for i in range(2)]
        z = nm.matvec(w, d)
        if math.sqrt(z[0] * z[0] + z[1] * z[1]) <= SELECTION_RADIUS:
            kept.append(row)
    if len(kept) < 64:
        raise NumericalFailure("selection control removed essentially every frame")
    return kept
