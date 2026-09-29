"""C3 — DecisionRule domain model.

Authoritative source: docs/domain/c3-decision-rule.md (V0.2, READY_TO_FREEZE).

This module implements the rule *schema* and catalog-level referential
validation only. It deliberately contains NO rule evaluator, no matching
loop, no precedence/specificity resolution and no risk/priority scoring
(section 21 of the task instructions; section 23-24 of the C3 doc).

`RULE_CATALOG_V1` below is the production V1 rule catalog and intentionally
holds zero rules — the A3/A4 contingency matrix has not been approved into
production rules yet. Worked examples from the reviewed C3 doc exist only
as test fixtures (backend/tests/domain/fixtures.py), never here.

Implementation note on typed condition values (see completion report for
full rationale): `EnumCondition`/`EnumSetCondition` store `value`/`values`
as validated `str`, not as a raw `Union[Taluka, RainfallZone, ...]`. A raw
union was tried and rejected: several of these enums share the literal
member `"UNKNOWN"`, and Pydantic's union resolution silently collapses an
ambiguous match to whichever enum type is listed first in the union,
regardless of which one the condition's `fact` actually names. A validated
string, cross-checked against the specific enum implied by `fact`, is safer
than that silent mis-typing while still not being `Any`.
"""

from __future__ import annotations

import calendar
from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.agronomy_rules.crops import (
    CROP_CATALOG_V1,
    CropCatalog,
    CropId,
    CropOptionId,
    ExternalOptionReference,
    ensure_valid_source_ids,
)
from app.modules.field_profile.context import (
    DecisionType,
    IrrigationAvailability,
    MonsoonDelayStage,
    RainfallZone,
    SoilDepthClass,
    SowingMoistureStatus,
    Taluka,
)
from app.modules.shared.enums import District, Season

# ---------------------------------------------------------------------------
# Rule identity, family, status, scope (sections 3-7)
# ---------------------------------------------------------------------------


class RuleFamily(str, Enum):
    SOWING_WINDOW_RULE = "SOWING_WINDOW_RULE"
    PRE_SOWING_CANDIDATE_RULE = "PRE_SOWING_CANDIDATE_RULE"
    SCENARIO_ADVISORY = "SCENARIO_ADVISORY"


class RuleStatus(str, Enum):
    ACTIVE_PROTOTYPE = "ACTIVE_PROTOTYPE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    DEFERRED = "DEFERRED"
    RETIRED = "RETIRED"


class RuleScope(BaseModel):
    """Section 6. Facts that describe *where/what the rule applies to* —
    district, season, decision_types, crop_option_ids. These must never
    also appear as `RuleCondition` facts (section 7); that is enforced
    structurally here by `ConditionFact` simply not defining those facts.
    """

    model_config = ConfigDict(frozen=True)

    district: District
    season: Season
    decision_types: tuple[DecisionType, ...]
    crop_option_ids: tuple[CropOptionId, ...]


# ---------------------------------------------------------------------------
# Conditions (sections 8-12)
# ---------------------------------------------------------------------------


class ConditionFact(str, Enum):
    """V1 pre-sowing condition facts (section 8).

    Deliberately excludes SOWING_WINDOW_STATUS (would make candidate rules
    depend on another rule family's output — not introduced in V1 without
    explicit later evidence) and CLIMATE_SCENARIO (reserved for deferred
    ScenarioAdvisory rules, not active pre-sowing conditions).
    """

    TALUKA = "TALUKA"
    RAINFALL_ZONE = "RAINFALL_ZONE"
    SOIL_DEPTH_CLASS = "SOIL_DEPTH_CLASS"
    IRRIGATION_AVAILABILITY = "IRRIGATION_AVAILABILITY"
    PROPOSED_SOWING_DATE = "PROPOSED_SOWING_DATE"
    MONSOON_DELAY_STAGE = "MONSOON_DELAY_STAGE"
    SOWING_MOISTURE_STATUS = "SOWING_MOISTURE_STATUS"


class ConditionOperator(str, Enum):
    EQUALS = "EQUALS"
    IN = "IN"
    NOT_EQUALS = "NOT_EQUALS"
    DATE_ON_OR_AFTER = "DATE_ON_OR_AFTER"
    DATE_ON_OR_BEFORE = "DATE_ON_OR_BEFORE"
    DATE_BETWEEN_INCLUSIVE = "DATE_BETWEEN_INCLUSIVE"


# Facts backed by an enum type (as opposed to the recurring-date fact below).
_ENUM_FACT_TYPES: dict[ConditionFact, type[Enum]] = {
    ConditionFact.TALUKA: Taluka,
    ConditionFact.RAINFALL_ZONE: RainfallZone,
    ConditionFact.SOIL_DEPTH_CLASS: SoilDepthClass,
    ConditionFact.IRRIGATION_AVAILABILITY: IrrigationAvailability,
    ConditionFact.MONSOON_DELAY_STAGE: MonsoonDelayStage,
    ConditionFact.SOWING_MOISTURE_STATUS: SowingMoistureStatus,
}

EnumFact = Literal[
    ConditionFact.TALUKA,
    ConditionFact.RAINFALL_ZONE,
    ConditionFact.SOIL_DEPTH_CLASS,
    ConditionFact.IRRIGATION_AVAILABILITY,
    ConditionFact.MONSOON_DELAY_STAGE,
    ConditionFact.SOWING_MOISTURE_STATUS,
]


def _validate_enum_value(fact: ConditionFact, value: str) -> str:
    enum_type = _ENUM_FACT_TYPES[fact]
    try:
        enum_type(value)
    except ValueError as exc:
        raise ValueError(f"{value!r} is not a valid value for fact {fact}") from exc
    return value


class MonthDay(BaseModel):
    """Section 12. A recurring Kharif calendar date with no embedded year."""

    model_config = ConfigDict(frozen=True)

    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)

    @model_validator(mode="after")
    def _validate_day_in_month(self) -> "MonthDay":
        # 2024 is used only as a permissive leap-year reference so 29 Feb
        # remains representable; MonthDay itself carries no year.
        max_day = calendar.monthrange(2024, self.month)[1]
        if self.day > max_day:
            raise ValueError(f"day {self.day} is not valid for month {self.month}")
        return self


class EnumCondition(BaseModel):
    """`fact OPERATOR value`, operator in {EQUALS, NOT_EQUALS}."""

    model_config = ConfigDict(frozen=True)

    kind: Literal["ENUM"] = "ENUM"
    fact: EnumFact
    operator: Literal[ConditionOperator.EQUALS, ConditionOperator.NOT_EQUALS]
    value: str

    @model_validator(mode="after")
    def _validate_value(self) -> "EnumCondition":
        _validate_enum_value(self.fact, self.value)
        return self


class EnumSetCondition(BaseModel):
    """`fact IN values`."""

    model_config = ConfigDict(frozen=True)

    kind: Literal["ENUM_SET"] = "ENUM_SET"
    fact: EnumFact
    operator: Literal[ConditionOperator.IN] = ConditionOperator.IN
    values: tuple[str, ...]

    @model_validator(mode="after")
    def _validate_values(self) -> "EnumSetCondition":
        if not self.values:
            raise ValueError("EnumSetCondition requires at least one value")
        for value in self.values:
            _validate_enum_value(self.fact, value)
        return self


class MonthDayCondition(BaseModel):
    """`PROPOSED_SOWING_DATE` on-or-after/on-or-before a recurring MonthDay."""

    model_config = ConfigDict(frozen=True)

    kind: Literal["MONTH_DAY"] = "MONTH_DAY"
    fact: Literal[ConditionFact.PROPOSED_SOWING_DATE] = ConditionFact.PROPOSED_SOWING_DATE
    operator: Literal[ConditionOperator.DATE_ON_OR_AFTER, ConditionOperator.DATE_ON_OR_BEFORE]
    value: MonthDay


class MonthDayRangeCondition(BaseModel):
    """`PROPOSED_SOWING_DATE` inclusively between two recurring MonthDay values."""

    model_config = ConfigDict(frozen=True)

    kind: Literal["MONTH_DAY_RANGE"] = "MONTH_DAY_RANGE"
    fact: Literal[ConditionFact.PROPOSED_SOWING_DATE] = ConditionFact.PROPOSED_SOWING_DATE
    operator: Literal[ConditionOperator.DATE_BETWEEN_INCLUSIVE] = ConditionOperator.DATE_BETWEEN_INCLUSIVE
    start: MonthDay
    end: MonthDay


RuleCondition = Annotated[
    Union[EnumCondition, EnumSetCondition, MonthDayCondition, MonthDayRangeCondition],
    Field(discriminator="kind"),
]


# ---------------------------------------------------------------------------
# Effects (sections 13-18)
# ---------------------------------------------------------------------------


class SowingWindowStatus(str, Enum):
    NORMAL_WINDOW = "NORMAL_WINDOW"
    DELAYED_WINDOW = "DELAYED_WINDOW"
    CONTINGENCY_WINDOW = "CONTINGENCY_WINDOW"
    CONDITIONAL_REVIEW = "CONDITIONAL_REVIEW"
    OUTSIDE_V1_WINDOW = "OUTSIDE_V1_WINDOW"


class VarietyDurationRequirement(str, Enum):
    ANY_APPROVED = "ANY_APPROVED"
    EARLY_OR_SHORT_DURATION_REQUIRED = "EARLY_OR_SHORT_DURATION_REQUIRED"
    CROP_SPECIFIC_APPROVED_VARIETY_REQUIRED = "CROP_SPECIFIC_APPROVED_VARIETY_REQUIRED"
    UNKNOWN = "UNKNOWN"


class ComponentVarietyRequirement(BaseModel):
    """Section 17. Attached to one component crop, never to "the system"
    as a whole — e.g. an early-Pigeonpea requirement inside
    PEARL_MILLET_PIGEONPEA_INTERCROP applies to Pigeonpea only."""

    model_config = ConfigDict(frozen=True)

    crop_id: CropId
    requirement: VarietyDurationRequirement


class SowingWindowEffect(BaseModel):
    """Section 14. Used only by SOWING_WINDOW_RULE. Cannot substitute or
    exclude a crop option — it has no such fields."""

    model_config = ConfigDict(frozen=True)

    kind: Literal["SOWING_WINDOW"] = "SOWING_WINDOW"
    status: SowingWindowStatus
    component_variety_requirements: tuple[ComponentVarietyRequirement, ...] = ()
    warning_keys: tuple[str, ...] = ()


class CandidateAction(str, Enum):
    """Section 15. All actions are local to the evaluated crop option —
    e.g. EXCLUDE_NO_SUPPORTED_REPLACEMENT means this option is excluded and
    its source-backed replacements are outside the active V1 catalog; it
    does NOT mean the assessment has no viable Kharif crop at all."""

    KEEP_CANDIDATE = "KEEP_CANDIDATE"
    KEEP_WITH_CONDITIONS = "KEEP_WITH_CONDITIONS"
    COMPARE_ALTERNATIVE = "COMPARE_ALTERNATIVE"
    SUBSTITUTE_TO_SUPPORTED_OPTION = "SUBSTITUTE_TO_SUPPORTED_OPTION"
    EXCLUDE_AND_OFFER_RABI_PLANNING = "EXCLUDE_AND_OFFER_RABI_PLANNING"
    EXCLUDE_NO_SUPPORTED_REPLACEMENT = "EXCLUDE_NO_SUPPORTED_REPLACEMENT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


_ACTIONS_WITH_TARGETS = frozenset(
    {CandidateAction.SUBSTITUTE_TO_SUPPORTED_OPTION, CandidateAction.COMPARE_ALTERNATIVE}
)


class CandidateEffect(BaseModel):
    """Section 16."""

    model_config = ConfigDict(frozen=True)

    kind: Literal["CANDIDATE"] = "CANDIDATE"
    action: CandidateAction
    target_option_ids: tuple[CropOptionId, ...] = ()
    source_alternatives: tuple[ExternalOptionReference, ...] = ()
    component_variety_requirements: tuple[ComponentVarietyRequirement, ...] = ()
    requirement_keys: tuple[str, ...] = ()
    warning_keys: tuple[str, ...] = ()
    mitigation_keys: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _validate_target_counts(self) -> "CandidateEffect":
        if self.action == CandidateAction.SUBSTITUTE_TO_SUPPORTED_OPTION:
            if len(self.target_option_ids) != 1:
                raise ValueError(
                    "SUBSTITUTE_TO_SUPPORTED_OPTION requires exactly one target_option_id"
                )
        elif self.action == CandidateAction.COMPARE_ALTERNATIVE:
            if len(self.target_option_ids) < 1:
                raise ValueError("COMPARE_ALTERNATIVE requires at least one target_option_id")
        elif self.target_option_ids:
            raise ValueError(
                f"{self.action} does not support target_option_ids "
                f"(only SUBSTITUTE_TO_SUPPORTED_OPTION/COMPARE_ALTERNATIVE do)"
            )
        return self


class ScenarioAdvisoryEffect(BaseModel):
    """Section 18. Advisory-only: no action field exists on this model, so
    it cannot substitute or exclude a crop option, change candidate
    eligibility, or carry a risk-score delta — structurally, not just by
    convention."""

    model_config = ConfigDict(frozen=True)

    kind: Literal["SCENARIO_ADVISORY"] = "SCENARIO_ADVISORY"
    warning_keys: tuple[str, ...] = ()
    mitigation_keys: tuple[str, ...] = ()


RuleEffect = Annotated[
    Union[SowingWindowEffect, CandidateEffect, ScenarioAdvisoryEffect],
    Field(discriminator="kind"),
]

_FAMILY_EFFECT_TYPES: dict[RuleFamily, type[BaseModel]] = {
    RuleFamily.SOWING_WINDOW_RULE: SowingWindowEffect,
    RuleFamily.PRE_SOWING_CANDIDATE_RULE: CandidateEffect,
    RuleFamily.SCENARIO_ADVISORY: ScenarioAdvisoryEffect,
}


# ---------------------------------------------------------------------------
# Evidence (sections 19-20)
# ---------------------------------------------------------------------------


class RuleSupportType(str, Enum):
    DIRECT = "DIRECT"
    CORROBORATED = "CORROBORATED"
    CONFLICTING = "CONFLICTING"
    PRODUCT_DERIVED = "PRODUCT_DERIVED"


class RuleEvidence(BaseModel):
    """Section 19-20. References canonical SRC-* ids only; source
    age/currentness/publication metadata stays in the Evidence Register."""

    model_config = ConfigDict(frozen=True)

    source_ids: tuple[str, ...]
    support_type: RuleSupportType

    @field_validator("source_ids")
    @classmethod
    def _validate_source_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return ensure_valid_source_ids(value)


# ---------------------------------------------------------------------------
# DecisionRule and RuleCatalog (sections 4-5, 26-27, 35)
# ---------------------------------------------------------------------------


class DecisionRule(BaseModel):
    model_config = ConfigDict(frozen=True)

    rule_id: str
    version: str
    family: RuleFamily
    status: RuleStatus
    scope: RuleScope
    conditions: tuple[RuleCondition, ...]
    effect: RuleEffect
    evidence: RuleEvidence
    explanation_key: str
    developer_notes: str | None = None

    @model_validator(mode="after")
    def _validate_family_effect_match(self) -> "DecisionRule":
        expected_type = _FAMILY_EFFECT_TYPES[self.family]
        if not isinstance(self.effect, expected_type):
            raise ValueError(
                f"{self.rule_id}: family {self.family} requires a {expected_type.__name__}, "
                f"got {type(self.effect).__name__}"
            )
        return self

    @model_validator(mode="after")
    def _validate_evidence_required_when_decisive(self) -> "DecisionRule":
        if self.status in (RuleStatus.ACTIVE_PROTOTYPE, RuleStatus.REVIEW_REQUIRED):
            if not self.evidence.source_ids:
                raise ValueError(
                    f"{self.rule_id}: ACTIVE_PROTOTYPE/REVIEW_REQUIRED rules require evidence"
                )
        return self


class RuleCatalog(BaseModel):
    """Section 26. Immutable for a version; declares which C2 catalog
    version it is compatible with (checked against an actual `CropCatalog`
    by `validate_rule_catalog_against_crop_catalog`, not by this model
    alone — a `RuleCatalog` has no reference to a live `CropCatalog`
    object, only to its id/version, so cross-catalog checks are a separate
    startup-validation step)."""

    model_config = ConfigDict(frozen=True)

    catalog_id: str
    version: str
    district_scope: District
    season_scope: Season
    compatible_crop_catalog_id: str
    compatible_crop_catalog_version: str
    rules: tuple[DecisionRule, ...]

    @model_validator(mode="after")
    def _validate_unique_rule_ids(self) -> "RuleCatalog":
        seen: set[str] = set()
        duplicates: set[str] = set()
        for rule in self.rules:
            if rule.rule_id in seen:
                duplicates.add(rule.rule_id)
            seen.add(rule.rule_id)
        if duplicates:
            raise ValueError(f"duplicate rule_id(s): {sorted(duplicates)}")
        return self

    @model_validator(mode="after")
    def _validate_rule_scope_matches_catalog(self) -> "RuleCatalog":
        for rule in self.rules:
            if rule.scope.district != self.district_scope:
                raise ValueError(
                    f"{rule.rule_id}: scope.district does not match catalog district_scope"
                )
            if rule.scope.season != self.season_scope:
                raise ValueError(
                    f"{rule.rule_id}: scope.season does not match catalog season_scope"
                )
        return self

    @model_validator(mode="after")
    def _validate_scenario_advisory_deferred(self) -> "RuleCatalog":
        for rule in self.rules:
            if rule.family == RuleFamily.SCENARIO_ADVISORY and rule.status != RuleStatus.DEFERRED:
                raise ValueError(
                    f"{rule.rule_id}: SCENARIO_ADVISORY rules must be DEFERRED in the V1 "
                    f"pre-sowing rule catalog (schema supports other statuses for later phases)"
                )
        return self


def validate_rule_catalog_against_crop_catalog(
    rule_catalog: RuleCatalog, crop_catalog: CropCatalog
) -> None:
    """Startup catalog validation (C3 doc, section 35, items 4-5 and 16-17).

    This is referential/schema validation between two static catalogs, not
    a rule evaluator: it never inspects an `AssessmentContext` and never
    decides which rule "fires".
    """
    if rule_catalog.compatible_crop_catalog_id != crop_catalog.catalog_id:
        raise ValueError(
            f"rule catalog {rule_catalog.catalog_id} declares compatible_crop_catalog_id="
            f"{rule_catalog.compatible_crop_catalog_id!r}, but was validated against "
            f"crop catalog {crop_catalog.catalog_id!r}"
        )
    if rule_catalog.compatible_crop_catalog_version != crop_catalog.version:
        raise ValueError(
            f"rule catalog {rule_catalog.catalog_id} declares "
            f"compatible_crop_catalog_version={rule_catalog.compatible_crop_catalog_version!r}, "
            f"but was validated against crop catalog version {crop_catalog.version!r}"
        )

    known_option_ids = set(crop_catalog.crop_options.keys())

    for rule in rule_catalog.rules:
        for option_id in rule.scope.crop_option_ids:
            if option_id not in known_option_ids:
                raise ValueError(
                    f"{rule.rule_id}: scope references unknown crop option {option_id}"
                )

        effect = rule.effect
        if isinstance(effect, CandidateEffect):
            for target_id in effect.target_option_ids:
                if target_id not in known_option_ids:
                    raise ValueError(
                        f"{rule.rule_id}: effect targets unknown crop option {target_id}"
                    )

            if effect.component_variety_requirements:
                relevant_option_ids = effect.target_option_ids or rule.scope.crop_option_ids
                allowed_crop_ids: set[CropId] = set()
                for option_id in relevant_option_ids:
                    profile = crop_catalog.crop_options.get(option_id)
                    if profile is not None:
                        allowed_crop_ids.update(profile.component_crops)
                for requirement in effect.component_variety_requirements:
                    if requirement.crop_id not in allowed_crop_ids:
                        raise ValueError(
                            f"{rule.rule_id}: component variety requirement for "
                            f"{requirement.crop_id} does not match any component crop of "
                            f"the affected/target option(s) {relevant_option_ids}"
                        )


# Production V1 rule catalog. Deliberately empty: the A3/A4 contingency
# matrix has not been reviewed into production DecisionRule entries yet
# (see docs/planning/v1-execution-graph.md, Phase D). Worked examples from
# the C3 doc exist only as test fixtures, never appended here.
RULE_CATALOG_V1 = RuleCatalog(
    catalog_id="dharashiv-kharif-rules",
    version="1.0",
    district_scope=District.DHARASHIV,
    season_scope=Season.KHARIF,
    compatible_crop_catalog_id=CROP_CATALOG_V1.catalog_id,
    compatible_crop_catalog_version=CROP_CATALOG_V1.version,
    rules=(),
)

validate_rule_catalog_against_crop_catalog(RULE_CATALOG_V1, CROP_CATALOG_V1)
