"""C2 tests per docs/domain/c2-crop-profile.md section 21 and the task's
section 23 test list."""

import pytest
from pydantic import ValidationError

from app.modules.agronomy_rules.crops import (
    CROP_CATALOG_V1,
    CropCatalog,
    CropDefinition,
    CropId,
    CropOptionId,
    CropOptionProfile,
    CropOptionProductRole,
    CropOptionStatus,
    CropOptionType,
    ExternalOptionReference,
)
from app.modules.shared.enums import District, Season


def test_catalog_id_version_scope_are_stable():
    assert CROP_CATALOG_V1.catalog_id == "dharashiv-kharif"
    assert CROP_CATALOG_V1.version == "1.0"
    assert CROP_CATALOG_V1.district_scope == District.DHARASHIV
    assert CROP_CATALOG_V1.season_scope == Season.KHARIF


def test_exactly_four_atomic_crops():
    assert len(CROP_CATALOG_V1.crop_definitions) == 4
    assert set(CROP_CATALOG_V1.crop_definitions.keys()) == {
        CropId.SOYBEAN,
        CropId.BLACK_GRAM,
        CropId.PIGEONPEA,
        CropId.PEARL_MILLET,
    }


def test_exactly_six_active_v1_options():
    active = [o for o in CROP_CATALOG_V1.crop_options.values() if o.status == CropOptionStatus.ACTIVE_V1]
    assert len(active) == 6
    assert len(CROP_CATALOG_V1.crop_options) == 6  # no non-active options sneaked in either


def test_crop_ids_and_option_ids_are_serialized_distinctly():
    definitions_json = {k.value for k in CROP_CATALOG_V1.crop_definitions}
    options_json = {k.value for k in CROP_CATALOG_V1.crop_options}
    assert definitions_json.isdisjoint(options_json)


def test_monocrops_have_exactly_one_component():
    monocrop_ids = {
        CropOptionId.SOYBEAN_MONOCROP,
        CropOptionId.BLACK_GRAM_MONOCROP,
        CropOptionId.PIGEONPEA_MONOCROP,
        CropOptionId.PEARL_MILLET_MONOCROP,
    }
    for option_id in monocrop_ids:
        profile = CROP_CATALOG_V1.crop_options[option_id]
        assert profile.option_type == CropOptionType.MONOCROP
        assert len(profile.component_crops) == 1


def test_intercrops_have_correct_atomic_components():
    soy_tur = CROP_CATALOG_V1.crop_options[CropOptionId.SOYBEAN_PIGEONPEA_INTERCROP]
    assert soy_tur.option_type == CropOptionType.INTERCROP
    assert set(soy_tur.component_crops) == {CropId.SOYBEAN, CropId.PIGEONPEA}

    bajra_tur = CROP_CATALOG_V1.crop_options[CropOptionId.PEARL_MILLET_PIGEONPEA_INTERCROP]
    assert bajra_tur.option_type == CropOptionType.INTERCROP
    assert set(bajra_tur.component_crops) == {CropId.PEARL_MILLET, CropId.PIGEONPEA}


def test_component_order_carries_no_role_information():
    # Both orderings must be treated as equivalent membership, not roles.
    a = CropOptionProfile(
        option_id=CropOptionId.SOYBEAN_PIGEONPEA_INTERCROP,
        option_type=CropOptionType.INTERCROP,
        component_crops=(CropId.SOYBEAN, CropId.PIGEONPEA),
        display_name_key="x",
        product_role=CropOptionProductRole.DIVERSIFICATION_SYSTEM,
        supported_seasons=(Season.KHARIF,),
        evidence_source_ids=("SRC-005",),
        status=CropOptionStatus.ACTIVE_V1,
    )
    b = a.model_copy(update={"component_crops": (CropId.PIGEONPEA, CropId.SOYBEAN)})
    assert set(a.component_crops) == set(b.component_crops)


def test_every_component_resolves_to_a_valid_crop_definition():
    for option in CROP_CATALOG_V1.crop_options.values():
        for crop_id in option.component_crops:
            assert crop_id in CROP_CATALOG_V1.crop_definitions


def test_every_active_option_supports_kharif():
    for option in CROP_CATALOG_V1.crop_options.values():
        assert Season.KHARIF in option.supported_seasons


def test_every_active_option_has_canonical_source_ids():
    for option in CROP_CATALOG_V1.crop_options.values():
        assert len(option.evidence_source_ids) >= 1
        for source_id in option.evidence_source_ids:
            assert source_id.startswith("SRC-")


def test_catalog_is_immutable():
    with pytest.raises(TypeError):
        CROP_CATALOG_V1.crop_options["extra"] = None  # type: ignore[index]
    with pytest.raises(ValidationError):
        CROP_CATALOG_V1.version = "2.0"  # type: ignore[misc]


def test_source_only_alternatives_are_not_active_candidates():
    active_display_keys = {o.display_name_key for o in CROP_CATALOG_V1.crop_options.values()}
    for canonical_key in ("niger", "fodder_sorghum", "fodder_maize", "green_gram"):
        assert canonical_key not in active_display_keys
    # ExternalOptionReference is a valid, separate provenance shape - it
    # simply never appears inside crop_options.
    ref = ExternalOptionReference(canonical_key="fodder_sorghum", source_ids=("SRC-006",))
    assert ref.canonical_key == "fodder_sorghum"


def test_profiles_contain_no_contextual_agronomic_or_market_fields():
    profile_fields = set(CropOptionProfile.model_fields.keys())
    forbidden = {
        "sowing_dates",
        "normal_start",
        "normal_end",
        "last_sowing_date",
        "allowed_soils",
        "preferred_soils",
        "requires_irrigation",
        "duration_days",
        "risk_score",
        "drought_tolerance_score",
        "failure_probability",
        "market_price",
        "expected_profit",
        "row_ratio",
        "agmarknet_commodity_code",
    }
    assert profile_fields.isdisjoint(forbidden)


def test_catalog_version_survives_serialization_roundtrip():
    dumped = CROP_CATALOG_V1.model_dump()
    rebuilt = CropCatalog(**dumped)
    assert rebuilt.catalog_id == CROP_CATALOG_V1.catalog_id
    assert rebuilt.version == CROP_CATALOG_V1.version
    assert rebuilt.crop_options.keys() == CROP_CATALOG_V1.crop_options.keys()

    json_str = CROP_CATALOG_V1.model_dump_json()
    assert '"version":"1.0"' in json_str


def test_invalid_evidence_source_id_format_rejected():
    with pytest.raises(ValidationError):
        CropOptionProfile(
            option_id=CropOptionId.SOYBEAN_MONOCROP,
            option_type=CropOptionType.MONOCROP,
            component_crops=(CropId.SOYBEAN,),
            display_name_key="x",
            product_role=CropOptionProductRole.CORE_BASELINE,
            supported_seasons=(Season.KHARIF,),
            evidence_source_ids=("not-a-source-id",),
            status=CropOptionStatus.ACTIVE_V1,
        )


def test_monocrop_with_two_components_rejected():
    with pytest.raises(ValidationError):
        CropOptionProfile(
            option_id=CropOptionId.SOYBEAN_MONOCROP,
            option_type=CropOptionType.MONOCROP,
            component_crops=(CropId.SOYBEAN, CropId.PIGEONPEA),
            display_name_key="x",
            product_role=CropOptionProductRole.CORE_BASELINE,
            supported_seasons=(Season.KHARIF,),
            evidence_source_ids=("SRC-001",),
            status=CropOptionStatus.ACTIVE_V1,
        )


def test_intercrop_with_one_component_rejected():
    with pytest.raises(ValidationError):
        CropOptionProfile(
            option_id=CropOptionId.SOYBEAN_PIGEONPEA_INTERCROP,
            option_type=CropOptionType.INTERCROP,
            component_crops=(CropId.SOYBEAN,),
            display_name_key="x",
            product_role=CropOptionProductRole.DIVERSIFICATION_SYSTEM,
            supported_seasons=(Season.KHARIF,),
            evidence_source_ids=("SRC-001",),
            status=CropOptionStatus.ACTIVE_V1,
        )


def test_active_option_without_evidence_rejected():
    with pytest.raises(ValidationError):
        CropOptionProfile(
            option_id=CropOptionId.SOYBEAN_MONOCROP,
            option_type=CropOptionType.MONOCROP,
            component_crops=(CropId.SOYBEAN,),
            display_name_key="x",
            product_role=CropOptionProductRole.CORE_BASELINE,
            supported_seasons=(Season.KHARIF,),
            evidence_source_ids=(),
            status=CropOptionStatus.ACTIVE_V1,
        )


def test_catalog_rejects_component_crop_missing_from_definitions():
    with pytest.raises(ValidationError):
        CropCatalog(
            catalog_id="broken",
            version="0.0",
            district_scope=District.DHARASHIV,
            season_scope=Season.KHARIF,
            crop_definitions={
                CropId.SOYBEAN: CropDefinition(crop_id=CropId.SOYBEAN, display_name_key="crop.soybean.name"),
            },
            crop_options={
                CropOptionId.SOYBEAN_PIGEONPEA_INTERCROP: CropOptionProfile(
                    option_id=CropOptionId.SOYBEAN_PIGEONPEA_INTERCROP,
                    option_type=CropOptionType.INTERCROP,
                    component_crops=(CropId.SOYBEAN, CropId.PIGEONPEA),
                    display_name_key="x",
                    product_role=CropOptionProductRole.DIVERSIFICATION_SYSTEM,
                    supported_seasons=(Season.KHARIF,),
                    evidence_source_ids=("SRC-005",),
                    status=CropOptionStatus.ACTIVE_V1,
                ),
            },
        )
