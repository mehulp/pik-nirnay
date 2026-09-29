"""C1 — Assessment / Farm Context domain model.

Authoritative source: docs/domain/c1-farm-context.md (V0.2, READY_TO_FREEZE).

This module defines the normalized input to A3/A4 evaluation. It performs
only the structural validation the reviewed document explicitly allows
(section 16) and must NOT perform any of the following (section 17):

- observed_depth_cm -> SoilDepthClass classification
- monsoon_delay_days -> MonsoonDelayStage classification
- weather observations -> SowingMoistureStatus derivation
- crop recommendation logic
- risk scoring

UNKNOWN is a legitimate first-class value throughout (section 15), never a
stand-in for an error, a district average, or "rain-fed".
"""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator

from app.modules.shared.enums import District, Season


class Taluka(str, Enum):
    """The eight Dharashiv talukas, plus UNKNOWN (section 6.2)."""

    DHARASHIV = "DHARASHIV"
    TULJAPUR = "TULJAPUR"
    OMERGA = "OMERGA"
    LOHARA = "LOHARA"
    KALLAM = "KALLAM"
    BHOOM = "BHOOM"
    PARANDA = "PARANDA"
    WASHI = "WASHI"
    UNKNOWN = "UNKNOWN"


class RainfallZone(str, Enum):
    """Rule-input abstraction derived from the Dharashiv contingency plan (section 6.4).

    Normally RULE_DERIVED via `location_resolver.resolve_rainfall_zone`,
    never hand-entered by the farmer.
    """

    LOWER_RAINFALL_BHOOM_PARANDA = "LOWER_RAINFALL_BHOOM_PARANDA"
    OTHER_DHARASHIV = "OTHER_DHARASHIV"
    UNKNOWN = "UNKNOWN"


class ContextSource(str, Enum):
    """Provenance for any derived/reported C1 fact (section 6.5)."""

    USER_REPORTED = "USER_REPORTED"
    RULE_DERIVED = "RULE_DERIVED"
    GIS_SUGGESTED = "GIS_SUGGESTED"
    FIELD_MEASURED = "FIELD_MEASURED"
    PROVIDER_DERIVED = "PROVIDER_DERIVED"
    UNKNOWN = "UNKNOWN"


class SoilDepthClass(str, Enum):
    """Frozen for V1; the numeric cm boundaries are deliberately NOT frozen
    and must not be hard-coded here (section 7.1)."""

    SHALLOW = "SHALLOW"
    MEDIUM_DEEP = "MEDIUM_DEEP"
    DEEP = "DEEP"
    UNKNOWN = "UNKNOWN"


class IrrigationAvailability(str, Enum):
    """Section 8."""

    RAINFED_ONLY = "RAINFED_ONLY"
    PROTECTIVE_IRRIGATION_AVAILABLE = "PROTECTIVE_IRRIGATION_AVAILABLE"
    RELIABLE_IRRIGATION = "RELIABLE_IRRIGATION"
    UNKNOWN = "UNKNOWN"


class DecisionType(str, Enum):
    """RESOWING is representable but unsupported by V1 rules; that policy
    check is intentionally left to the application layer, above this model
    (section 9.1)."""

    FIRST_SOWING = "FIRST_SOWING"
    RESOWING = "RESOWING"


class MonsoonDelayStage(str, Enum):
    """Normalized delay-onset state consumed by A4. No exact day boundaries
    are implied for "ABOUT_*" values (section 11)."""

    NORMAL_OR_LT_2_WEEKS = "NORMAL_OR_LT_2_WEEKS"
    ABOUT_2_WEEKS = "ABOUT_2_WEEKS"
    ABOUT_4_WEEKS = "ABOUT_4_WEEKS"
    ABOUT_6_WEEKS = "ABOUT_6_WEEKS"
    ABOUT_8_WEEKS = "ABOUT_8_WEEKS"
    UNKNOWN = "UNKNOWN"


class SowingMoistureStatus(str, Enum):
    """Section 12. Defaults to UNKNOWN until an approved derivation exists."""

    READY = "READY"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


class LocationContext(BaseModel):
    """Section 6."""

    model_config = ConfigDict(frozen=True)

    district: District
    taluka: Taluka
    village_name: str | None = None
    rainfall_zone: RainfallZone
    rainfall_zone_source: ContextSource

    @field_validator("district")
    @classmethod
    def _district_is_dharashiv(cls, value: District) -> District:
        if value != District.DHARASHIV:
            raise ValueError("V1 supports only District.DHARASHIV")
        return value


class SoilContext(BaseModel):
    """Section 7.

    `observed_depth_cm` and `depth_class` are independent fields; this model
    does not attempt to prove they are consistent with each other (section
    7.2) — the resolver/provider that produced them owns that consistency.
    """

    model_config = ConfigDict(frozen=True)

    depth_class: SoilDepthClass
    source: ContextSource
    observed_depth_cm: float | None = None

    @field_validator("observed_depth_cm")
    @classmethod
    def _observed_depth_positive(cls, value: float | None) -> float | None:
        if value is not None and value <= 0:
            raise ValueError("observed_depth_cm must be > 0 when provided")
        return value


class WaterContext(BaseModel):
    """Section 8."""

    model_config = ConfigDict(frozen=True)

    irrigation_availability: IrrigationAvailability
    source: ContextSource


class FarmContext(BaseModel):
    """Section 5. Stable field/farm facts only — no crop recommendations,
    no provider-specific schemas."""

    model_config = ConfigDict(frozen=True)

    location: LocationContext
    soil: SoilContext
    water: WaterContext


class SowingIntent(BaseModel):
    """Section 9. The farmer's proposed action — not a stable farm fact.

    The exact date is retained even outside A3 windows; A3 is responsible
    for returning OUTSIDE_V1_WINDOW, not this model.
    """

    model_config = ConfigDict(frozen=True)

    decision_type: DecisionType
    proposed_sowing_date: date


class SeasonContext(BaseModel):
    """Section 10. Time-varying season/weather-derived state, kept separate
    from `FarmContext` so the same farm can be evaluated against different
    season contexts (today, a different date, a historical replay)."""

    model_config = ConfigDict(frozen=True)

    monsoon_delay_stage: MonsoonDelayStage
    monsoon_delay_days: int | None = None
    monsoon_delay_source: ContextSource

    sowing_moisture_status: SowingMoistureStatus
    moisture_status_source: ContextSource

    as_of_date: date

    @field_validator("monsoon_delay_days")
    @classmethod
    def _delay_days_non_negative(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            raise ValueError("monsoon_delay_days must be >= 0 when provided")
        return value


class AssessmentContext(BaseModel):
    """Section 2. The complete normalized input to A3/A4 evaluation."""

    model_config = ConfigDict(frozen=True)

    assessment_date: date
    season: Season
    farm: FarmContext
    sowing_intent: SowingIntent
    season_context: SeasonContext

    @field_validator("season")
    @classmethod
    def _season_is_kharif(cls, value: Season) -> Season:
        if value != Season.KHARIF:
            raise ValueError("V1 supports only Season.KHARIF")
        return value
