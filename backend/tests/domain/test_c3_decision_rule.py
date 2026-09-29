"""C3 tests per docs/domain/c3-decision-rule.md section 36 and the task's
section 24 test list."""

import pytest
from pydantic import ValidationError

from app.modules.agronomy_rules.crops import CROP_CATALOG_V1, CropId, CropOptionId
from app.modules.agronomy_rules.rules import (
    RULE_CATALOG_V1,
    CandidateAction,
    CandidateEffect,
    ComponentVarietyRequirement,
    ConditionFact,
    ConditionOperator,
    DecisionRule,
    EnumCondition,
    EnumSetCondition,
    MonthDay,
    MonthDayCondition,
    RuleCatalog,
    RuleEvidence,
    RuleFamily,
    RuleScope,
    RuleStatus,
    RuleSupportType,
    ScenarioAdvisoryEffect,
    SowingWindowEffect,
    SowingWindowStatus,
    VarietyDurationRequirement,
    validate_rule_catalog_against_crop_catalog,
)
from app.modules.field_profile.context import DecisionType
from app.modules.shared.enums import District, Season

from tests.domain.fixtures import ALL_FIXTURE_RULES, SHALLOW_SOIL_TUR_SIX_WEEK_DELAY


def _scope(*option_ids: CropOptionId) -> RuleScope:
    return RuleScope(
        district=District.DHARASHIV,
        season=Season.KHARIF,
        decision_types=(DecisionType.FIRST_SOWING,),
        crop_option_ids=option_ids,
    )


def _fixture_catalog(*rules: DecisionRule) -> RuleCatalog:
    return RuleCatalog(
        catalog_id="test-fixtures",
        version="0.0",
        district_scope=District.DHARASHIV,
        season_scope=Season.KHARIF,
        compatible_crop_catalog_id=CROP_CATALOG_V1.catalog_id,
        compatible_crop_catalog_version=CROP_CATALOG_V1.version,
        rules=rules,
    )


# ---------------------------------------------------------------------------
# Fixture rules build cleanly and validate against CROP_CATALOG_V1
# ---------------------------------------------------------------------------


def test_all_fixture_rules_are_valid_and_cross_validate():
    catalog = _fixture_catalog(*ALL_FIXTURE_RULES)
    validate_rule_catalog_against_crop_catalog(catalog, CROP_CATALOG_V1)


def test_rule_serialization_roundtrip():
    rule = SHALLOW_SOIL_TUR_SIX_WEEK_DELAY
    dumped = rule.model_dump()
    rebuilt = DecisionRule(**dumped)
    assert rebuilt == rule
    assert '"rule_id":"R-DHAR-ONSET-6W-PP-SH"' in rule.model_dump_json()


# ---------------------------------------------------------------------------
# Identity / uniqueness
# ---------------------------------------------------------------------------


def test_duplicate_rule_id_rejected():
    duplicate = SHALLOW_SOIL_TUR_SIX_WEEK_DELAY.model_copy()
    with pytest.raises(ValidationError):
        _fixture_catalog(SHALLOW_SOIL_TUR_SIX_WEEK_DELAY, duplicate)


# ---------------------------------------------------------------------------
# Family / effect compatibility
# ---------------------------------------------------------------------------


def test_family_effect_mismatch_rejected():
    with pytest.raises(ValidationError):
        DecisionRule(
            rule_id="BAD-FAMILY-EFFECT",
            version="1.0",
            family=RuleFamily.SOWING_WINDOW_RULE,
            status=RuleStatus.ACTIVE_PROTOTYPE,
            scope=_scope(CropOptionId.SOYBEAN_MONOCROP),
            conditions=(),
            effect=CandidateEffect(action=CandidateAction.KEEP_CANDIDATE),
            evidence=RuleEvidence(source_ids=("SRC-006",), support_type=RuleSupportType.DIRECT),
            explanation_key="x",
        )


def test_sowing_window_rule_accepts_sowing_window_effect():
    rule = DecisionRule(
        rule_id="R-WINDOW-OK",
        version="1.0",
        family=RuleFamily.SOWING_WINDOW_RULE,
        status=RuleStatus.ACTIVE_PROTOTYPE,
        scope=_scope(CropOptionId.SOYBEAN_MONOCROP),
        conditions=(),
        effect=SowingWindowEffect(status=SowingWindowStatus.NORMAL_WINDOW),
        evidence=RuleEvidence(source_ids=("SRC-006",), support_type=RuleSupportType.DIRECT),
        explanation_key="x",
    )
    assert rule.effect.status == SowingWindowStatus.NORMAL_WINDOW


# ---------------------------------------------------------------------------
# Scope vs condition duplication is impossible by schema
# ---------------------------------------------------------------------------


def test_scope_facts_cannot_be_expressed_as_conditions():
    # DISTRICT/SEASON/DECISION_TYPE/CROP_OPTION_ID simply do not exist as
    # ConditionFact members, so this is a schema-level AttributeError, not a
    # runtime rejection - proving the duplication is structurally impossible.
    for forbidden in ("DISTRICT", "SEASON", "DECISION_TYPE", "CROP_OPTION_ID"):
        assert not hasattr(ConditionFact, forbidden)


# ---------------------------------------------------------------------------
# Invalid fact/operator/value combinations
# ---------------------------------------------------------------------------


def test_invalid_enum_value_for_fact_rejected():
    with pytest.raises(ValidationError):
        EnumCondition(fact=ConditionFact.SOIL_DEPTH_CLASS, operator=ConditionOperator.EQUALS, value="BHOOM")


def test_enum_condition_cannot_use_date_fact():
    with pytest.raises(ValidationError):
        EnumCondition(
            fact=ConditionFact.PROPOSED_SOWING_DATE,
            operator=ConditionOperator.EQUALS,
            value="SHALLOW",
        )


def test_enum_set_condition_requires_at_least_one_value():
    with pytest.raises(ValidationError):
        EnumSetCondition(fact=ConditionFact.TALUKA, values=())


def test_enum_set_condition_rejects_mixed_valid_and_invalid_values():
    with pytest.raises(ValidationError):
        EnumSetCondition(fact=ConditionFact.TALUKA, values=("BHOOM", "NOT_A_TALUKA"))


def test_month_day_range_condition_valid():
    condition = MonthDayCondition(
        fact=ConditionFact.PROPOSED_SOWING_DATE,
        operator=ConditionOperator.DATE_ON_OR_AFTER,
        value=MonthDay(month=7, day=16),
    )
    assert condition.value.month == 7


def test_month_day_rejects_invalid_day_for_month():
    with pytest.raises(ValidationError):
        MonthDay(month=6, day=31)  # June has 30 days


# ---------------------------------------------------------------------------
# Crop-option / crop-catalog referential validation
# ---------------------------------------------------------------------------


def _crop_catalog_missing_pearl_millet_pigeonpea_intercrop():
    """A realistic 'older' crop catalog that predates one option, used to
    exercise referential rejection without bypassing real enum validation."""
    from app.modules.agronomy_rules.crops import CropCatalog

    trimmed_options = {
        option_id: profile
        for option_id, profile in CROP_CATALOG_V1.crop_options.items()
        if option_id != CropOptionId.PEARL_MILLET_PIGEONPEA_INTERCROP
    }
    return CropCatalog(
        catalog_id=CROP_CATALOG_V1.catalog_id,
        version="0.9",
        district_scope=CROP_CATALOG_V1.district_scope,
        season_scope=CROP_CATALOG_V1.season_scope,
        crop_definitions=dict(CROP_CATALOG_V1.crop_definitions),
        crop_options=trimmed_options,
    )


def test_invalid_crop_option_reference_in_scope_rejected():
    older_catalog = _crop_catalog_missing_pearl_millet_pigeonpea_intercrop()
    rule = DecisionRule(
        rule_id="R-SCOPES-FUTURE-OPTION",
        version="1.0",
        family=RuleFamily.PRE_SOWING_CANDIDATE_RULE,
        status=RuleStatus.ACTIVE_PROTOTYPE,
        scope=_scope(CropOptionId.PEARL_MILLET_PIGEONPEA_INTERCROP),
        conditions=(),
        effect=CandidateEffect(action=CandidateAction.KEEP_CANDIDATE),
        evidence=RuleEvidence(source_ids=("SRC-006",), support_type=RuleSupportType.DIRECT),
        explanation_key="x",
    )
    catalog = _fixture_catalog(rule).model_copy(update={"compatible_crop_catalog_version": "0.9"})
    with pytest.raises(ValueError):
        validate_rule_catalog_against_crop_catalog(catalog, older_catalog)


def test_invalid_target_option_reference_rejected():
    older_catalog = _crop_catalog_missing_pearl_millet_pigeonpea_intercrop()
    rule = SHALLOW_SOIL_TUR_SIX_WEEK_DELAY.model_copy(
        update={"rule_id": "R-TARGETS-FUTURE-OPTION"}
    )  # targets PEARL_MILLET_PIGEONPEA_INTERCROP, absent from older_catalog
    catalog = _fixture_catalog(rule).model_copy(update={"compatible_crop_catalog_version": "0.9"})
    with pytest.raises(ValueError):
        validate_rule_catalog_against_crop_catalog(catalog, older_catalog)


def test_incompatible_crop_catalog_version_rejected():
    catalog = _fixture_catalog(SHALLOW_SOIL_TUR_SIX_WEEK_DELAY).model_copy(
        update={"compatible_crop_catalog_version": "9.9"}
    )
    with pytest.raises(ValueError):
        validate_rule_catalog_against_crop_catalog(catalog, CROP_CATALOG_V1)


def test_incompatible_crop_catalog_id_rejected():
    catalog = _fixture_catalog(SHALLOW_SOIL_TUR_SIX_WEEK_DELAY).model_copy(
        update={"compatible_crop_catalog_id": "some-other-catalog"}
    )
    with pytest.raises(ValueError):
        validate_rule_catalog_against_crop_catalog(catalog, CROP_CATALOG_V1)


# ---------------------------------------------------------------------------
# Candidate target-count validation
# ---------------------------------------------------------------------------


def test_substitute_requires_exactly_one_target():
    with pytest.raises(ValidationError):
        CandidateEffect(action=CandidateAction.SUBSTITUTE_TO_SUPPORTED_OPTION, target_option_ids=())
    with pytest.raises(ValidationError):
        CandidateEffect(
            action=CandidateAction.SUBSTITUTE_TO_SUPPORTED_OPTION,
            target_option_ids=(CropOptionId.PEARL_MILLET_MONOCROP, CropOptionId.PIGEONPEA_MONOCROP),
        )


def test_compare_requires_at_least_one_target():
    with pytest.raises(ValidationError):
        CandidateEffect(action=CandidateAction.COMPARE_ALTERNATIVE, target_option_ids=())
    effect = CandidateEffect(
        action=CandidateAction.COMPARE_ALTERNATIVE,
        target_option_ids=(CropOptionId.PEARL_MILLET_MONOCROP,),
    )
    assert len(effect.target_option_ids) == 1


def test_exclusion_actions_reject_targets():
    for action in (
        CandidateAction.KEEP_CANDIDATE,
        CandidateAction.KEEP_WITH_CONDITIONS,
        CandidateAction.EXCLUDE_AND_OFFER_RABI_PLANNING,
        CandidateAction.EXCLUDE_NO_SUPPORTED_REPLACEMENT,
        CandidateAction.REVIEW_REQUIRED,
    ):
        with pytest.raises(ValidationError):
            CandidateEffect(action=action, target_option_ids=(CropOptionId.PEARL_MILLET_MONOCROP,))


def test_exclusion_actions_do_not_imply_no_kharif_option_globally():
    # EXCLUDE_NO_SUPPORTED_REPLACEMENT is local to the evaluated option; this
    # test documents that the effect carries no field claiming a global
    # "no Kharif option" conclusion.
    effect = CandidateEffect(action=CandidateAction.EXCLUDE_NO_SUPPORTED_REPLACEMENT)
    assert not hasattr(effect, "no_kharif_option_available")
    assert effect.action == CandidateAction.EXCLUDE_NO_SUPPORTED_REPLACEMENT


# ---------------------------------------------------------------------------
# Component-variety-requirement validation against target/affected components
# ---------------------------------------------------------------------------


def test_component_variety_requirement_validates_against_target_components():
    catalog = _fixture_catalog(
        DecisionRule(
            rule_id="R-BAD-COMPONENT",
            version="1.0",
            family=RuleFamily.PRE_SOWING_CANDIDATE_RULE,
            status=RuleStatus.ACTIVE_PROTOTYPE,
            scope=_scope(CropOptionId.PIGEONPEA_MONOCROP),
            conditions=(),
            effect=CandidateEffect(
                action=CandidateAction.SUBSTITUTE_TO_SUPPORTED_OPTION,
                target_option_ids=(CropOptionId.PEARL_MILLET_PIGEONPEA_INTERCROP,),
                component_variety_requirements=(
                    ComponentVarietyRequirement(
                        crop_id=CropId.SOYBEAN,  # not a component of the target option
                        requirement=VarietyDurationRequirement.EARLY_OR_SHORT_DURATION_REQUIRED,
                    ),
                ),
            ),
            evidence=RuleEvidence(source_ids=("SRC-006",), support_type=RuleSupportType.DIRECT),
            explanation_key="x",
        )
    )
    with pytest.raises(ValueError):
        validate_rule_catalog_against_crop_catalog(catalog, CROP_CATALOG_V1)


# ---------------------------------------------------------------------------
# ScenarioAdvisory: deferred, and cannot carry candidate semantics
# ---------------------------------------------------------------------------


def test_scenario_advisory_fixture_is_deferred():
    from tests.domain.fixtures import DEFERRED_HEAVY_RAIN_SOYBEAN_ADVISORY

    assert DEFERRED_HEAVY_RAIN_SOYBEAN_ADVISORY.status == RuleStatus.DEFERRED
    assert DEFERRED_HEAVY_RAIN_SOYBEAN_ADVISORY.family == RuleFamily.SCENARIO_ADVISORY


def test_non_deferred_scenario_advisory_rejected_by_catalog():
    from tests.domain.fixtures import DEFERRED_HEAVY_RAIN_SOYBEAN_ADVISORY

    active_advisory = DEFERRED_HEAVY_RAIN_SOYBEAN_ADVISORY.model_copy(
        update={"rule_id": "NOT-DEFERRED", "status": RuleStatus.ACTIVE_PROTOTYPE}
    )
    with pytest.raises(ValidationError):
        _fixture_catalog(active_advisory)


def test_scenario_advisory_effect_cannot_carry_candidate_fields():
    effect = ScenarioAdvisoryEffect(warning_keys=("x",))
    assert not hasattr(effect, "action")
    assert not hasattr(effect, "target_option_ids")


# ---------------------------------------------------------------------------
# Source-only alternatives retained, not silently dropped
# ---------------------------------------------------------------------------


def test_source_only_alternatives_are_retained_on_exclude_effect():
    from tests.domain.fixtures import BLACK_GRAM_EXCLUDE_SOURCE_ONLY_ALTERNATIVES as rule

    keys = {ref.canonical_key for ref in rule.effect.source_alternatives}
    assert keys == {"niger", "fodder_sorghum", "rabi_planning"}


# ---------------------------------------------------------------------------
# No numeric priority, no risk-score field
# ---------------------------------------------------------------------------


def test_no_numeric_priority_field_on_decision_rule_or_scope():
    assert "priority" not in DecisionRule.model_fields
    assert "priority" not in RuleScope.model_fields


def test_no_risk_score_field_anywhere_in_rule_schema():
    for model in (DecisionRule, RuleScope, CandidateEffect, SowingWindowEffect, ScenarioAdvisoryEffect):
        assert not any("risk_score" in field_name for field_name in model.model_fields)


# ---------------------------------------------------------------------------
# Production catalog stays empty; fixtures never appear in it
# ---------------------------------------------------------------------------


def test_production_rule_catalog_has_no_agricultural_rules():
    assert RULE_CATALOG_V1.rules == ()


def test_fixture_rules_do_not_appear_in_production_catalog():
    production_ids = {rule.rule_id for rule in RULE_CATALOG_V1.rules}
    fixture_ids = {rule.rule_id for rule in ALL_FIXTURE_RULES}
    assert production_ids.isdisjoint(fixture_ids)
    assert production_ids == set()


def test_catalog_version_survives_serialization():
    dumped = RULE_CATALOG_V1.model_dump()
    rebuilt = RuleCatalog(**dumped)
    assert rebuilt.version == "1.0"
    assert rebuilt.compatible_crop_catalog_version == CROP_CATALOG_V1.version


def test_rule_catalog_is_immutable():
    with pytest.raises(ValidationError):
        RULE_CATALOG_V1.version = "2.0"  # type: ignore[misc]
