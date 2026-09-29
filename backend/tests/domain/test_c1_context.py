"""C1 tests per docs/domain/c1-farm-context.md section 20 and the task's
section 22 test list."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.modules.field_profile.context import (
    AssessmentContext,
    ContextSource,
    DecisionType,
    FarmContext,
    IrrigationAvailability,
    LocationContext,
    MonsoonDelayStage,
    RainfallZone,
    SeasonContext,
    SoilContext,
    SoilDepthClass,
    SowingIntent,
    SowingMoistureStatus,
    Taluka,
    WaterContext,
)
from app.modules.shared.enums import District, Season


def _valid_context(**overrides) -> AssessmentContext:
    defaults = dict(
        assessment_date=date(2027, 7, 27),
        season=Season.KHARIF,
        farm=FarmContext(
            location=LocationContext(
                district=District.DHARASHIV,
                taluka=Taluka.BHOOM,
                rainfall_zone=RainfallZone.LOWER_RAINFALL_BHOOM_PARANDA,
                rainfall_zone_source=ContextSource.RULE_DERIVED,
            ),
            soil=SoilContext(depth_class=SoilDepthClass.MEDIUM_DEEP, source=ContextSource.USER_REPORTED),
            water=WaterContext(
                irrigation_availability=IrrigationAvailability.PROTECTIVE_IRRIGATION_AVAILABLE,
                source=ContextSource.USER_REPORTED,
            ),
        ),
        sowing_intent=SowingIntent(
            decision_type=DecisionType.FIRST_SOWING, proposed_sowing_date=date(2027, 7, 27)
        ),
        season_context=SeasonContext(
            monsoon_delay_stage=MonsoonDelayStage.ABOUT_6_WEEKS,
            monsoon_delay_source=ContextSource.PROVIDER_DERIVED,
            sowing_moisture_status=SowingMoistureStatus.READY,
            moisture_status_source=ContextSource.PROVIDER_DERIVED,
            as_of_date=date(2027, 7, 27),
        ),
    )
    defaults.update(overrides)
    return AssessmentContext(**defaults)


def test_complete_valid_assessment_context():
    ctx = _valid_context()
    assert ctx.season == Season.KHARIF
    assert ctx.farm.location.district == District.DHARASHIV


def test_all_unknown_paths_are_legitimate():
    ctx = _valid_context(
        farm=FarmContext(
            location=LocationContext(
                district=District.DHARASHIV,
                taluka=Taluka.UNKNOWN,
                rainfall_zone=RainfallZone.UNKNOWN,
                rainfall_zone_source=ContextSource.RULE_DERIVED,
            ),
            soil=SoilContext(depth_class=SoilDepthClass.UNKNOWN, source=ContextSource.UNKNOWN),
            water=WaterContext(
                irrigation_availability=IrrigationAvailability.UNKNOWN, source=ContextSource.UNKNOWN
            ),
        ),
        season_context=SeasonContext(
            monsoon_delay_stage=MonsoonDelayStage.UNKNOWN,
            monsoon_delay_source=ContextSource.UNKNOWN,
            sowing_moisture_status=SowingMoistureStatus.UNKNOWN,
            moisture_status_source=ContextSource.UNKNOWN,
            as_of_date=date(2027, 7, 27),
        ),
    )
    assert ctx.farm.location.taluka == Taluka.UNKNOWN
    assert ctx.farm.soil.depth_class == SoilDepthClass.UNKNOWN
    assert ctx.season_context.monsoon_delay_stage == MonsoonDelayStage.UNKNOWN
    assert ctx.season_context.sowing_moisture_status == SowingMoistureStatus.UNKNOWN


def test_non_dharashiv_district_rejected():
    with pytest.raises(ValidationError):
        LocationContext(
            district="PUNE",
            taluka=Taluka.DHARASHIV,
            rainfall_zone=RainfallZone.OTHER_DHARASHIV,
            rainfall_zone_source=ContextSource.RULE_DERIVED,
        )


def test_zero_and_negative_observed_depth_rejected():
    with pytest.raises(ValidationError):
        SoilContext(depth_class=SoilDepthClass.UNKNOWN, source=ContextSource.UNKNOWN, observed_depth_cm=0)
    with pytest.raises(ValidationError):
        SoilContext(depth_class=SoilDepthClass.UNKNOWN, source=ContextSource.UNKNOWN, observed_depth_cm=-5)


def test_positive_observed_depth_accepted_independently_of_class():
    # C1 does not attempt to prove observed_depth_cm and depth_class agree.
    soil = SoilContext(depth_class=SoilDepthClass.UNKNOWN, source=ContextSource.FIELD_MEASURED, observed_depth_cm=42)
    assert soil.observed_depth_cm == 42
    assert soil.depth_class == SoilDepthClass.UNKNOWN


def test_negative_monsoon_delay_days_rejected():
    with pytest.raises(ValidationError):
        SeasonContext(
            monsoon_delay_stage=MonsoonDelayStage.UNKNOWN,
            monsoon_delay_days=-1,
            monsoon_delay_source=ContextSource.UNKNOWN,
            sowing_moisture_status=SowingMoistureStatus.UNKNOWN,
            moisture_status_source=ContextSource.UNKNOWN,
            as_of_date=date(2027, 7, 27),
        )


def test_zero_monsoon_delay_days_accepted():
    ctx = SeasonContext(
        monsoon_delay_stage=MonsoonDelayStage.NORMAL_OR_LT_2_WEEKS,
        monsoon_delay_days=0,
        monsoon_delay_source=ContextSource.PROVIDER_DERIVED,
        sowing_moisture_status=SowingMoistureStatus.UNKNOWN,
        moisture_status_source=ContextSource.UNKNOWN,
        as_of_date=date(2027, 7, 27),
    )
    assert ctx.monsoon_delay_days == 0


def test_exact_sowing_date_preserved():
    ctx = _valid_context()
    assert ctx.sowing_intent.proposed_sowing_date == date(2027, 7, 27)


def test_no_automatic_soil_depth_classification_from_observed_depth():
    # Same observed depth, two different (independently set) classes: proves
    # there is no hidden cm -> class conversion inside the model.
    shallow = SoilContext(depth_class=SoilDepthClass.SHALLOW, source=ContextSource.FIELD_MEASURED, observed_depth_cm=42)
    deep = SoilContext(depth_class=SoilDepthClass.DEEP, source=ContextSource.FIELD_MEASURED, observed_depth_cm=42)
    assert shallow.observed_depth_cm == deep.observed_depth_cm == 42
    assert shallow.depth_class != deep.depth_class


def test_no_automatic_monsoon_day_classification():
    # Same delay-day count, two different (independently set) stages: proves
    # there is no hidden days -> stage conversion inside the model.
    a = SeasonContext(
        monsoon_delay_stage=MonsoonDelayStage.ABOUT_4_WEEKS,
        monsoon_delay_days=30,
        monsoon_delay_source=ContextSource.PROVIDER_DERIVED,
        sowing_moisture_status=SowingMoistureStatus.UNKNOWN,
        moisture_status_source=ContextSource.UNKNOWN,
        as_of_date=date(2027, 7, 27),
    )
    b = SeasonContext(
        monsoon_delay_stage=MonsoonDelayStage.ABOUT_6_WEEKS,
        monsoon_delay_days=30,
        monsoon_delay_source=ContextSource.PROVIDER_DERIVED,
        sowing_moisture_status=SowingMoistureStatus.UNKNOWN,
        moisture_status_source=ContextSource.UNKNOWN,
        as_of_date=date(2027, 7, 27),
    )
    assert a.monsoon_delay_days == b.monsoon_delay_days == 30
    assert a.monsoon_delay_stage != b.monsoon_delay_stage


def test_resowing_can_be_represented():
    intent = SowingIntent(decision_type=DecisionType.RESOWING, proposed_sowing_date=date(2027, 8, 10))
    ctx = _valid_context(sowing_intent=intent)
    assert ctx.sowing_intent.decision_type == DecisionType.RESOWING


def test_resowing_does_not_raise_or_invoke_first_sowing_logic():
    # C1 itself has no policy opinion on RESOWING - constructing it must not
    # raise, and there is no first-sowing-only code path in this module for
    # it to accidentally hit.
    intent = SowingIntent(decision_type=DecisionType.RESOWING, proposed_sowing_date=date(2027, 8, 10))
    assert intent.decision_type == DecisionType.RESOWING


def test_provenance_and_as_of_date_serialize_correctly():
    ctx = _valid_context()
    dumped = ctx.model_dump()
    assert dumped["farm"]["location"]["rainfall_zone_source"] == "RULE_DERIVED"
    assert dumped["season_context"]["monsoon_delay_source"] == "PROVIDER_DERIVED"
    assert dumped["season_context"]["moisture_status_source"] == "PROVIDER_DERIVED"
    assert dumped["season_context"]["as_of_date"] == date(2027, 7, 27)

    restored = AssessmentContext(**dumped)
    assert restored == ctx


def test_models_are_frozen():
    ctx = _valid_context()
    with pytest.raises(ValidationError):
        ctx.assessment_date = date(2020, 1, 1)
