# Pik Nirnay — C3 DecisionRule Domain Model

**Project:** Pik Nirnay / पीक निर्णय  
**Workstream:** C3 — DecisionRule  
**Version:** V0.2 — reviewed  
**Status:** READY TO FREEZE FOR V1  
**Scope:** Versioned, evidence-backed rule definitions for Dharashiv Kharif V1  
**Depends on:** A3 V3, A4 V0.2, Evidence Register V0.2, C1 V0.2, C2 V0.2

---

## 1. Review conclusion

C3 V0.1 had the correct central principle: preserve agricultural rule meaning rather than reduce rules to hidden scores.

The review makes six important refinements:

1. Rule `scope` and rule `conditions` no longer duplicate the same facts.
2. Candidate actions are explicitly **local to the evaluated crop option**.
3. `NO_SUPPORTED_KHARIF_OPTION` is replaced because it could incorrectly imply that no Kharif option exists for the entire assessment.
4. Scenario-advisory rules are schema-supported but **DEFERRED in the pre-sowing V1 evaluator**.
5. Variety requirements are component-specific.
6. Rule catalogs explicitly declare compatible C2 crop-catalog versions.

---

# 2. Core principle

Rules preserve the actual evidence-backed action.

Example:

```text
IF
    evaluated option = PIGEONPEA_MONOCROP
    soil = SHALLOW
    monsoon delay = ABOUT_6_WEEKS

THEN
    substitute this option with
    PEARL_MILLET_PIGEONPEA_INTERCROP
```

Not:

```text
risk_score += 27
```

The later decision engine may build farmer-facing risk cards from matched rules, but C3 itself contains no opaque scoring.

---

# 3. Rule families

```text
RuleFamily
    SOWING_WINDOW_RULE
    PRE_SOWING_CANDIDATE_RULE
    SCENARIO_ADVISORY
```

## SOWING_WINDOW_RULE

Derived from A3.

Produces a timing classification for one crop option.

## PRE_SOWING_CANDIDATE_RULE

Derived from A4 delayed-onset/candidate evidence.

Changes how the currently evaluated crop option should be handled.

## SCENARIO_ADVISORY

Represents dry-spell, terminal-drought or heavy-rain management evidence.

### V1 activation decision

The current C1 `AssessmentContext` is a **pre-sowing** model and contains no `ClimateScenario`.

Therefore:

```text
SCENARIO_ADVISORY schema = supported
SCENARIO_ADVISORY V1 evaluation = DEFERRED
```

These rules may live in the catalog for provenance/future expansion, but the first pre-sowing decision engine must not evaluate them.

This avoids adding post-sowing state to C1 merely to satisfy C3.

---

# 4. Rule identity

```text
DecisionRule
    rule_id
    version
    family
    status
    scope
    conditions
    effect
    evidence
    explanation_key
    developer_notes?
```

Example:

```text
rule_id = "R-DHAR-ONSET-6W-PP-SH"
version = "1.0"
family = PRE_SOWING_CANDIDATE_RULE
status = ACTIVE_PROTOTYPE
```

---

# 5. RuleStatus

```text
RuleStatus
    ACTIVE_PROTOTYPE
    REVIEW_REQUIRED
    DEFERRED
    RETIRED
```

### ACTIVE_PROTOTYPE
May be evaluated automatically in the research prototype.

### REVIEW_REQUIRED
May be loaded/displayed for traceability, but must not create an automatic decisive crop action.

### DEFERRED
Schema-valid rule that V1 does not evaluate.

### RETIRED
Historical rule retained for traceability.

---

# 6. RuleScope

Scope describes **where and what the rule applies to**.

```text
RuleScope
    district
    season
    decision_types[]
    crop_option_ids[]
```

V1 defaults:

```text
district = DHARASHIV
season = KHARIF
decision_types = [FIRST_SOWING]
```

Example:

```text
crop_option_ids = [
    PIGEONPEA_MONOCROP
]
```

---

# 7. Scope vs conditions

The same fact must not appear in both places.

Therefore these are **scope facts**, not `RuleCondition` facts:

```text
DISTRICT
SEASON
DECISION_TYPE
CROP_OPTION_ID
```

This removes contradictory definitions such as:

```text
scope.crop_option = SOYBEAN
condition.crop_option = PIGEONPEA
```

---

# 8. V1 ConditionFact

Conditions should initially use facts available from C1 plus recurring date windows.

```text
ConditionFact
    TALUKA
    RAINFALL_ZONE
    SOIL_DEPTH_CLASS
    IRRIGATION_AVAILABILITY
    PROPOSED_SOWING_DATE
    MONSOON_DELAY_STAGE
    SOWING_MOISTURE_STATUS
```

Do not include:

```text
SOWING_WINDOW_STATUS
```

in V1 candidate-rule conditions yet.

Why?

That would make one rule family depend on the output of another and introduce hidden evaluation ordering before it is actually required by A4.

If a future reviewed rule genuinely needs the derived A3 status, it can be added deliberately.

`CLIMATE_SCENARIO` is reserved for deferred ScenarioAdvisory rules, not active pre-sowing V1 rules.

---

# 9. Condition semantics

All conditions in one V1 rule are combined with:

```text
AND
```

There is no arbitrary nested boolean expression language.

For OR semantics:

```text
operator = IN
```

or define multiple explicit rules.

This keeps rules auditable.

---

# 10. ConditionOperator

```text
ConditionOperator
    EQUALS
    IN
    NOT_EQUALS
    DATE_ON_OR_AFTER
    DATE_ON_OR_BEFORE
    DATE_BETWEEN_INCLUSIVE
```

Operator/fact compatibility must be validated.

Examples:

```text
SOIL_DEPTH_CLASS EQUALS SHALLOW
```

```text
TALUKA IN [BHOOM, PARANDA]
```

```text
PROPOSED_SOWING_DATE DATE_BETWEEN_INCLUSIVE [16 Jul, 20 Jul]
```

Do not support executable Python/JavaScript expressions.

---

# 11. Typed condition values

Production implementation should not use:

```python
value: Any
```

Recommended conceptual union:

```text
RuleCondition
    EnumCondition
    EnumSetCondition
    MonthDayCondition
    MonthDayRangeCondition
```

Example:

```text
EnumCondition
    fact = SOIL_DEPTH_CLASS
    operator = EQUALS
    value = SHALLOW
```

The schema validator must reject an incompatible value type for the chosen fact.

---

# 12. MonthDay

Recurring Kharif windows must not embed a fixed year.

```text
MonthDay
    month
    day
```

Example:

```text
16 July
    => MonthDay(7, 16)
```

A3 rules compare MonthDay values against the actual `proposed_sowing_date`.

V1 Kharif windows do not cross a calendar year.

---

# 13. Typed RuleEffect union

A rule has one effect appropriate to its family:

```text
RuleEffect
    SowingWindowEffect
    CandidateEffect
    ScenarioAdvisoryEffect
```

Family/effect mismatch is invalid.

---

# 14. SowingWindowEffect

Used only by:

```text
SOWING_WINDOW_RULE
```

```text
SowingWindowEffect
    status
    component_variety_requirements[]
    warning_keys[]
```

Status:

```text
SowingWindowStatus
    NORMAL_WINDOW
    DELAYED_WINDOW
    CONTINGENCY_WINDOW
    CONDITIONAL_REVIEW
    OUTSIDE_V1_WINDOW
```

---

# 15. CandidateAction

Candidate actions describe what happens to **the currently evaluated crop option**.

```text
CandidateAction
    KEEP_CANDIDATE
    KEEP_WITH_CONDITIONS
    COMPARE_ALTERNATIVE
    SUBSTITUTE_TO_SUPPORTED_OPTION
    EXCLUDE_AND_OFFER_RABI_PLANNING
    EXCLUDE_NO_SUPPORTED_REPLACEMENT
    REVIEW_REQUIRED
```

---

## 15.1 KEEP_CANDIDATE

The evaluated option remains eligible for later comparison.

---

## 15.2 KEEP_WITH_CONDITIONS

The evaluated option remains eligible but carries explicit requirements/warnings.

---

## 15.3 COMPARE_ALTERNATIVE

The evaluated option remains possible, but one or more alternatives must be surfaced prominently.

Example:

```text
SOYBEAN_MONOCROP
    compare with
SOYBEAN_PIGEONPEA_INTERCROP
```

---

## 15.4 SUBSTITUTE_TO_SUPPORTED_OPTION

The source-backed contingency transition replaces the evaluated option with one supported C2 option.

V1 validation:

```text
exactly one target option required
```

If several alternatives are possible, use `COMPARE_ALTERNATIVE` or `REVIEW_REQUIRED`; do not pretend there is one deterministic substitute.

---

## 15.5 EXCLUDE_AND_OFFER_RABI_PLANNING

The evaluated Kharif option should be removed and the source explicitly supports Kharif fallow / preparation for Rabi.

Important:

This does **not** mean no other V1 Kharif option can exist for the same AssessmentContext.

It is local to the evaluated crop option.

---

## 15.6 EXCLUDE_NO_SUPPORTED_REPLACEMENT

The evaluated crop option is not retained and the source alternatives are outside the active V1 crop catalog.

Example source alternatives:

```text
Niger
Fodder Sorghum
Fodder Maize
```

Again, this does not mean the entire assessment has no Kharif alternatives.

---

## 15.7 REVIEW_REQUIRED

Evidence is unresolved enough that no automatic candidate action should be taken.

---

# 16. CandidateEffect

```text
CandidateEffect
    action
    target_option_ids[]
    source_alternatives[]
    component_variety_requirements[]
    requirement_keys[]
    warning_keys[]
    mitigation_keys[]
```

### Target validation

```text
SUBSTITUTE_TO_SUPPORTED_OPTION
    => exactly 1 target

COMPARE_ALTERNATIVE
    => 1 or more targets

other actions
    => normally 0 targets
```

---

# 17. Component-specific variety requirements

The V0.1 model treated variety requirements too generically.

For an intercrop such as:

```text
PEARL_MILLET_PIGEONPEA_INTERCROP
```

a source may require **early-duration Pigeonpea**, not an early-duration version of every component.

Use:

```text
ComponentVarietyRequirement
    crop_id
    requirement
```

Requirement:

```text
VarietyDurationRequirement
    ANY_APPROVED
    EARLY_OR_SHORT_DURATION_REQUIRED
    CROP_SPECIFIC_APPROVED_VARIETY_REQUIRED
    UNKNOWN
```

Example:

```text
crop_id = PIGEONPEA
requirement = EARLY_OR_SHORT_DURATION_REQUIRED
```

---

# 18. ScenarioAdvisoryEffect

Schema for future/post-sowing use:

```text
ScenarioAdvisoryEffect
    warning_keys[]
    mitigation_keys[]
```

It cannot:

- substitute an option,
- exclude an option,
- alter candidate eligibility,
- carry a risk-score delta.

All current ScenarioAdvisory rules should be:

```text
status = DEFERRED
```

in the first pre-sowing V1 rule catalog.

---

# 19. Source alternatives

Use C2's provenance-only object:

```text
ExternalOptionReference
```

Example:

```text
canonical_key = "fodder_sorghum"
source_ids = [SRC-006]
```

`source_alternatives` must preserve source choices even when the V1 UI cannot compare them.

---

# 20. Rule evidence

Do not duplicate source age/currentness inside C3.

The Evidence Register already owns source-level metadata.

C3 only needs to describe **how the sources support this rule interpretation**.

Recommended:

```text
RuleEvidence
    source_ids[]
    support_type
```

---

## 20.1 RuleSupportType

```text
RuleSupportType
    DIRECT
    CORROBORATED
    CONFLICTING
    PRODUCT_DERIVED
```

### DIRECT
The rule effect closely follows the cited source.

### CORROBORATED
Multiple sources support the same direction.

### CONFLICTING
Sources disagree; the software effect intentionally preserves that conflict.

### PRODUCT_DERIVED
The product transforms source alternatives because of V1 scope.

Example:

```text
source:
    fodder maize / fodder sorghum / Rabi

V1 effect:
    EXCLUDE_NO_SUPPORTED_REPLACEMENT

support_type:
    PRODUCT_DERIVED
```

Whether the underlying source is current or legacy is looked up via `SRC-*` metadata in the Evidence Register.

---

# 21. Rule review state vs lifecycle

Do not add a second evidence-review enum that duplicates `RuleStatus`.

Use:

```text
RuleStatus.REVIEW_REQUIRED
```

when human review is still required.

Use Evidence Register source metadata for source limitations.

This keeps one authoritative rule lifecycle state.

---

# 22. Explanation and UI text

Every active rule has:

```text
explanation_key
```

Example:

```text
rule.dhar.onset_6w.pigeonpea_shallow
```

Rules must not embed long Marathi/English farmer prose.

Localization owns text.

Effects may additionally carry:

```text
warning_keys[]
requirement_keys[]
mitigation_keys[]
```

---

# 23. Rule conflict and resolution principles

C3 must preserve enough information for a later resolver.

Do not add:

```text
priority = 97
```

or a hidden weighting score.

Future resolution principles:

1. `REVIEW_REQUIRED` rules cannot produce automatic decisive actions.
2. More specific matched conditions may refine broader rules.
3. A current/legacy source conflict is represented, not averaged away.
4. Scenario advisories cannot override candidate eligibility.
5. Sowing-window and candidate rules may both apply because they answer different questions.
6. Two incompatible candidate effects must be returned as a conflict for D1/D2 to handle explicitly.

The exact resolver algorithm is not part of C3.

---

# 24. Rule specificity

Do not store hand-authored specificity numbers.

Specificity can later be derived from structured context dimensions.

Example:

```text
monsoon delay
```

is less specific than:

```text
monsoon delay
+ soil depth
+ rainfall zone
```

Scope fields should not be double-counted as conditions.

---

# 25. Missing facts

UNKNOWN does not mean false.

If a rule requires:

```text
SOIL_DEPTH_CLASS = SHALLOW
```

and C1 has:

```text
SOIL_DEPTH_CLASS = UNKNOWN
```

the evaluator should eventually return:

```text
NOT_EVALUABLE_MISSING_FACT
```

rather than simply `NOT_MATCHED`.

Future evaluation status:

```text
RuleEvaluationStatus
    MATCHED
    NOT_MATCHED
    NOT_EVALUABLE_MISSING_FACT
    NOT_EVALUABLE_UNSUPPORTED_CONTEXT
```

This is an evaluation-result contract for D1, not static rule state.

---

# 26. RuleCatalog

```text
RuleCatalog
    catalog_id
    version
    district_scope
    season_scope
    compatible_crop_catalog_id
    compatible_crop_catalog_version
    rules[]
```

V1:

```text
catalog_id = "dharashiv-kharif-rules"
version = "1.0"

district_scope = DHARASHIV
season_scope = KHARIF

compatible_crop_catalog_id = "dharashiv-kharif"
compatible_crop_catalog_version = "1.0"
```

This prevents a rule catalog from silently targeting option IDs from an incompatible C2 catalog.

The catalog is immutable for a version.

---

# 27. Rule version vs assessment date

Do not use a rule's software version as an agronomic date condition.

For historical replay:

```text
assessment_date = 2023-07-25
rule_catalog_version = 1.0
```

means:

> Evaluate the 2023 context using rule catalog 1.0.

It does **not** mean the rule must have existed publicly in 2023.

Source publication dates remain provenance metadata in the Evidence Register.

---

# 28. Example — shallow-soil Tur at six-week delay

```text
rule_id = R-DHAR-ONSET-6W-PP-SH
version = 1.0

family = PRE_SOWING_CANDIDATE_RULE
status = ACTIVE_PROTOTYPE

scope:
    district = DHARASHIV
    season = KHARIF
    decision_types = [FIRST_SOWING]
    crop_option_ids = [PIGEONPEA_MONOCROP]

conditions:
    MONSOON_DELAY_STAGE EQUALS ABOUT_6_WEEKS
    SOIL_DEPTH_CLASS EQUALS SHALLOW

effect:
    action = SUBSTITUTE_TO_SUPPORTED_OPTION
    target_option_ids = [
        PEARL_MILLET_PIGEONPEA_INTERCROP
    ]

evidence:
    source_ids = [SRC-006]
    support_type = DIRECT

explanation_key:
    rule.dhar.onset_6w.pigeonpea_shallow
```

---

# 29. Example — late Soybean conflict

```text
rule_id = R-DHAR-ONSET-6W-SOY
version = 1.0

family = PRE_SOWING_CANDIDATE_RULE
status = ACTIVE_PROTOTYPE

scope:
    crop_option_ids = [SOYBEAN_MONOCROP]

conditions:
    MONSOON_DELAY_STAGE EQUALS ABOUT_6_WEEKS

effect:
    action = COMPARE_ALTERNATIVE
    target_option_ids = [
        SOYBEAN_PIGEONPEA_INTERCROP
    ]
    warning_keys = [
        "late_sowing_substantial_downside"
    ]

evidence:
    source_ids = [
        SRC-006,
        SRC-007,
        SRC-010,
        SRC-011
    ]
    support_type = CONFLICTING
```

This preserves disagreement without creating false certainty.

---

# 30. Example — Black Gram, source alternatives outside V1

```text
rule_id = R-DHAR-ONSET-8W-BG
version = 1.0

family = PRE_SOWING_CANDIDATE_RULE
status = ACTIVE_PROTOTYPE

scope:
    crop_option_ids = [BLACK_GRAM_MONOCROP]

conditions:
    MONSOON_DELAY_STAGE EQUALS ABOUT_8_WEEKS

effect:
    action = EXCLUDE_NO_SUPPORTED_REPLACEMENT

    source_alternatives = [
        NIGER,
        FODDER_SORGHUM,
        RABI_PLANNING
    ]

evidence:
    source_ids = [SRC-006]
    support_type = PRODUCT_DERIVED
```

This says:

> Black Gram is excluded by this matched rule and its source-backed replacements are outside the current V1 crop catalog / decision surface.

It does not say:

> No Kharif crop is suitable for the farmer.

---

# 31. Example — explicit Rabi-planning transition

```text
rule_id = R-DHAR-ONSET-8W-SOY
version = 1.0

family = PRE_SOWING_CANDIDATE_RULE
status = ACTIVE_PROTOTYPE

scope:
    crop_option_ids = [SOYBEAN_MONOCROP]

conditions:
    MONSOON_DELAY_STAGE EQUALS ABOUT_8_WEEKS

effect:
    action = EXCLUDE_AND_OFFER_RABI_PLANNING

evidence:
    source_ids = [SRC-006]
    support_type = DIRECT
```

This action applies to Soybean, not automatically to every other crop option.

---

# 32. Example — component-specific variety requirement

```text
rule_id = R-DHAR-ONSET-8W-PP
version = 1.0

scope:
    crop_option_ids = [PIGEONPEA_MONOCROP]

conditions:
    MONSOON_DELAY_STAGE EQUALS ABOUT_8_WEEKS

effect:
    action = SUBSTITUTE_TO_SUPPORTED_OPTION

    target_option_ids = [
        PEARL_MILLET_PIGEONPEA_INTERCROP
    ]

    component_variety_requirements = [
        {
            crop_id = PIGEONPEA,
            requirement = EARLY_OR_SHORT_DURATION_REQUIRED
        }
    ]
```

The requirement is explicitly attached to the Pigeonpea component.

---

# 33. Example — deferred scenario advisory

```text
rule_id = R-DHAR-HEAVYRAIN-SOY
version = 1.0

family = SCENARIO_ADVISORY
status = DEFERRED

scope:
    crop_option_ids = [SOYBEAN_MONOCROP]

effect:
    warning_keys = [
        "climate.heavy_rain_waterlogging"
    ]
    mitigation_keys = [
        "mitigation.drain_excess_water"
    ]

evidence:
    source_ids = [SRC-006, SRC-014, SRC-015]
    support_type = CORROBORATED
```

The first pre-sowing V1 evaluator ignores this deferred rule.

---

# 34. Storage strategy

For V1 use version-controlled immutable rule definitions.

Recommended implementation options:

1. Python/Pydantic registry, or
2. tightly validated YAML/JSON loaded into Pydantic models.

For the first implementation, Python/Pydantic fixtures are simpler and safer.

No database CRUD or rule-editor UI is needed.

---

# 35. Startup catalog validation

Validate:

1. rule IDs unique,
2. rule family matches effect type,
3. scope district/season compatible with catalog,
4. scoped crop options exist in compatible C2 catalog,
5. target options exist,
6. source IDs use canonical `SRC-*`,
7. every active/review-required rule has evidence,
8. all conditions use allowed facts/operators/value types,
9. all V1 conditions are AND semantics,
10. substitute action has exactly one target,
11. compare action has at least one target,
12. exclusion actions have no supported target unless explicitly allowed by schema,
13. scenario advisory cannot contain candidate action,
14. deferred ScenarioAdvisory rules are not evaluated by V1,
15. sowing-window effect cannot substitute/exclude,
16. component variety requirements refer to component crops of the affected/target option,
17. catalog declares a compatible C2 catalog,
18. active catalog/rules are immutable.

---

# 36. Suggested tests

Claude should eventually test:

1. valid rule serialization,
2. duplicate ID rejection,
3. family/effect mismatch rejection,
4. scope/condition duplication is impossible by schema,
5. invalid crop-option reference rejected,
6. incompatible crop-catalog version rejected,
7. invalid source ID rejected,
8. invalid operator/fact pairing rejected,
9. substitute requires exactly one target,
10. compare requires one or more targets,
11. exclusion actions do not imply global no-crop result,
12. component variety requirement validates component membership,
13. deferred ScenarioAdvisory is skipped,
14. UNKNOWN required fact yields `NOT_EVALUABLE_MISSING_FACT`,
15. multiple matches can be represented,
16. no numeric priority exists,
17. no risk-score field exists,
18. catalog version survives serialization.

---

# 37. Mapping change required in A4 terminology

C3 V0.2 uses more precise software action names than A4 V0.2.

Map:

```text
A4 RABI_PLANNING_OPTION
    -> C3 EXCLUDE_AND_OFFER_RABI_PLANNING

A4 NO_SUPPORTED_KHARIF_OPTION
    -> C3 EXCLUDE_NO_SUPPORTED_REPLACEMENT
```

This is a terminology refinement, not a change to the agricultural evidence.

A4 may be updated later for naming consistency, but C3 V0.2 is the authoritative software action vocabulary.

---

# 38. Review decisions

| Question | Frozen V1 decision |
|---|---|
| Generic base rule + typed effects? | **Yes** |
| Scope and conditions may repeat crop/district/season? | **No** |
| Nested arbitrary boolean expressions? | **No** — AND + typed IN/date operators only |
| Candidate actions local or global? | **Local to evaluated crop option** |
| Numeric rule priority? | **No** |
| Scenario advisories active in pre-sowing V1? | **No — DEFERRED** |
| Candidate rules depend on SowingWindowStatus? | **Not in V1 unless later evidence requires it** |
| Generic variety requirement? | **No — component-specific** |
| Duplicate evidence-currentness enum in C3? | **No — Evidence Register owns source metadata** |
| Versioned rule catalog? | **Yes** |
| Rule catalog tied to C2 catalog version? | **Yes** |
| Database CRUD? | **No** |

---

# 39. C3 freeze decision

**Status: `READY_TO_FREEZE` for V1.**

The reviewed model now preserves a clean chain:

```text
C1 AssessmentContext
        +
C2 versioned CropCatalog
        +
C3 versioned RuleCatalog
        ↓
future rule evaluator
```

while preventing:

- global conclusions from crop-local rules,
- scenario warnings from becoming recommendations,
- duplicated scope/condition facts,
- arbitrary numeric priorities,
- hidden source conflicts,
- and unsupported variety assumptions.
