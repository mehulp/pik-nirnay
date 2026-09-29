"""C3 test-only agricultural rule fixtures.

These are the worked examples from docs/domain/c3-decision-rule.md (sections
28-33), reproduced here for schema testing only. They MUST NOT be added to
`app.modules.agronomy_rules.rules.RULE_CATALOG_V1` — that catalog is the
production V1 rule set, which the execution graph gates behind a separately
approved A3/A4 contingency matrix.
"""

from app.modules.agronomy_rules.crops import (
    CropId,
    CropOptionId,
    ExternalOptionReference,
)
from app.modules.agronomy_rules.rules import (
    CandidateAction,
    CandidateEffect,
    ComponentVarietyRequirement,
    ConditionFact,
    ConditionOperator,
    DecisionRule,
    EnumCondition,
    RuleEvidence,
    RuleFamily,
    RuleScope,
    RuleStatus,
    RuleSupportType,
    ScenarioAdvisoryEffect,
    VarietyDurationRequirement,
)
from app.modules.field_profile.context import DecisionType
from app.modules.shared.enums import District, Season


def _v1_scope(*option_ids: CropOptionId) -> RuleScope:
    return RuleScope(
        district=District.DHARASHIV,
        season=Season.KHARIF,
        decision_types=(DecisionType.FIRST_SOWING,),
        crop_option_ids=option_ids,
    )


# Section 28 — shallow-soil Tur at six-week delay -> substitute.
SHALLOW_SOIL_TUR_SIX_WEEK_DELAY = DecisionRule(
    rule_id="R-DHAR-ONSET-6W-PP-SH",
    version="1.0",
    family=RuleFamily.PRE_SOWING_CANDIDATE_RULE,
    status=RuleStatus.ACTIVE_PROTOTYPE,
    scope=_v1_scope(CropOptionId.PIGEONPEA_MONOCROP),
    conditions=(
        EnumCondition(
            fact=ConditionFact.MONSOON_DELAY_STAGE,
            operator=ConditionOperator.EQUALS,
            value="ABOUT_6_WEEKS",
        ),
        EnumCondition(
            fact=ConditionFact.SOIL_DEPTH_CLASS,
            operator=ConditionOperator.EQUALS,
            value="SHALLOW",
        ),
    ),
    effect=CandidateEffect(
        action=CandidateAction.SUBSTITUTE_TO_SUPPORTED_OPTION,
        target_option_ids=(CropOptionId.PEARL_MILLET_PIGEONPEA_INTERCROP,),
    ),
    evidence=RuleEvidence(source_ids=("SRC-006",), support_type=RuleSupportType.DIRECT),
    explanation_key="rule.dhar.onset_6w.pigeonpea_shallow",
)

# Section 29 — late Soybean -> compare Soybean+Tur, preserving source conflict.
LATE_SOYBEAN_COMPARE_INTERCROP = DecisionRule(
    rule_id="R-DHAR-ONSET-6W-SOY",
    version="1.0",
    family=RuleFamily.PRE_SOWING_CANDIDATE_RULE,
    status=RuleStatus.ACTIVE_PROTOTYPE,
    scope=_v1_scope(CropOptionId.SOYBEAN_MONOCROP),
    conditions=(
        EnumCondition(
            fact=ConditionFact.MONSOON_DELAY_STAGE,
            operator=ConditionOperator.EQUALS,
            value="ABOUT_6_WEEKS",
        ),
    ),
    effect=CandidateEffect(
        action=CandidateAction.COMPARE_ALTERNATIVE,
        target_option_ids=(CropOptionId.SOYBEAN_PIGEONPEA_INTERCROP,),
        warning_keys=("late_sowing_substantial_downside",),
    ),
    evidence=RuleEvidence(
        source_ids=("SRC-006", "SRC-007", "SRC-010", "SRC-011"),
        support_type=RuleSupportType.CONFLICTING,
    ),
    explanation_key="rule.dhar.onset_6w.soybean_compare",
)

# Section 30 — Black Gram excluded, source alternatives outside the V1 catalog.
BLACK_GRAM_EXCLUDE_SOURCE_ONLY_ALTERNATIVES = DecisionRule(
    rule_id="R-DHAR-ONSET-8W-BG",
    version="1.0",
    family=RuleFamily.PRE_SOWING_CANDIDATE_RULE,
    status=RuleStatus.ACTIVE_PROTOTYPE,
    scope=_v1_scope(CropOptionId.BLACK_GRAM_MONOCROP),
    conditions=(
        EnumCondition(
            fact=ConditionFact.MONSOON_DELAY_STAGE,
            operator=ConditionOperator.EQUALS,
            value="ABOUT_8_WEEKS",
        ),
    ),
    effect=CandidateEffect(
        action=CandidateAction.EXCLUDE_NO_SUPPORTED_REPLACEMENT,
        source_alternatives=(
            ExternalOptionReference(canonical_key="niger", source_ids=("SRC-006",)),
            ExternalOptionReference(canonical_key="fodder_sorghum", source_ids=("SRC-006",)),
            ExternalOptionReference(canonical_key="rabi_planning", source_ids=("SRC-006",)),
        ),
    ),
    evidence=RuleEvidence(source_ids=("SRC-006",), support_type=RuleSupportType.PRODUCT_DERIVED),
    explanation_key="rule.dhar.onset_8w.black_gram_exclude",
)

# Section 32 — component-specific variety requirement on a substitution target.
PIGEONPEA_SUBSTITUTE_WITH_EARLY_VARIETY_REQUIREMENT = DecisionRule(
    rule_id="R-DHAR-ONSET-8W-PP",
    version="1.0",
    family=RuleFamily.PRE_SOWING_CANDIDATE_RULE,
    status=RuleStatus.ACTIVE_PROTOTYPE,
    scope=_v1_scope(CropOptionId.PIGEONPEA_MONOCROP),
    conditions=(
        EnumCondition(
            fact=ConditionFact.MONSOON_DELAY_STAGE,
            operator=ConditionOperator.EQUALS,
            value="ABOUT_8_WEEKS",
        ),
    ),
    effect=CandidateEffect(
        action=CandidateAction.SUBSTITUTE_TO_SUPPORTED_OPTION,
        target_option_ids=(CropOptionId.PEARL_MILLET_PIGEONPEA_INTERCROP,),
        component_variety_requirements=(
            ComponentVarietyRequirement(
                crop_id=CropId.PIGEONPEA,
                requirement=VarietyDurationRequirement.EARLY_OR_SHORT_DURATION_REQUIRED,
            ),
        ),
    ),
    evidence=RuleEvidence(source_ids=("SRC-006",), support_type=RuleSupportType.DIRECT),
    explanation_key="rule.dhar.onset_8w.pigeonpea_substitute",
)

# Section 33 — deferred heavy-rain scenario advisory (schema-only, V1 does not evaluate it).
DEFERRED_HEAVY_RAIN_SOYBEAN_ADVISORY = DecisionRule(
    rule_id="R-DHAR-HEAVYRAIN-SOY",
    version="1.0",
    family=RuleFamily.SCENARIO_ADVISORY,
    status=RuleStatus.DEFERRED,
    scope=_v1_scope(CropOptionId.SOYBEAN_MONOCROP),
    conditions=(),
    effect=ScenarioAdvisoryEffect(
        warning_keys=("climate.heavy_rain_waterlogging",),
        mitigation_keys=("mitigation.drain_excess_water",),
    ),
    evidence=RuleEvidence(
        source_ids=("SRC-006", "SRC-014", "SRC-015"), support_type=RuleSupportType.CORROBORATED
    ),
    explanation_key="rule.dhar.heavy_rain.soybean",
)

ALL_FIXTURE_RULES = (
    SHALLOW_SOIL_TUR_SIX_WEEK_DELAY,
    LATE_SOYBEAN_COMPARE_INTERCROP,
    BLACK_GRAM_EXCLUDE_SOURCE_ONLY_ALTERNATIVES,
    PIGEONPEA_SUBSTITUTE_WITH_EARLY_VARIETY_REQUIREMENT,
    DEFERRED_HEAVY_RAIN_SOYBEAN_ADVISORY,
)
