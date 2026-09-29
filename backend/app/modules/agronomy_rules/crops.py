"""C2 — Crop / Crop-Option domain model.

Authoritative source: docs/domain/c2-crop-profile.md (V0.2, READY_TO_FREEZE).

Two deliberately separate levels (section 2):

    CropDefinition      identity/taxonomy metadata only
        -> CropOptionProfile   the V1 decision option (monocrop/intercrop)
            -> CropCatalog     the versioned, immutable Dharashiv Kharif registry

This module does NOT implement (section 13, explicitly excluded from
static profiles): sowing dates, soil suitability, irrigation requirement,
crop duration, risk/failure scores, market prices, AGMARKNET codes, or row
ratios. Evidence is referenced by canonical `SRC-*` id only — the Evidence
Register (docs/research/evidence-register.md) remains the sole owner of
source metadata (section 9 of the task instructions; section 20 of the
C3 doc states the same principle for rules).
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from enum import Enum
from types import MappingProxyType

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator, model_validator

from app.modules.shared.enums import District, Season

SRC_ID_PATTERN = re.compile(r"^SRC-\d{3}$")


def ensure_valid_source_ids(source_ids: Iterable[str]) -> tuple[str, ...]:
    """Validate canonical `SRC-###` shape. Shared by C2 and C3 so the regex
    is defined once; this is a format check only, not a source registry —
    the Evidence Register remains the sole source of truth for what a SRC-id
    actually documents."""
    values = tuple(source_ids)
    for source_id in values:
        if not SRC_ID_PATTERN.match(source_id):
            raise ValueError(f"invalid evidence source id (expected 'SRC-###'): {source_id!r}")
    return values


class CropId(str, Enum):
    """Atomic/biological crop identity (section 3). Only crops required by
    an active V1 decision option belong here."""

    SOYBEAN = "SOYBEAN"
    BLACK_GRAM = "BLACK_GRAM"
    PIGEONPEA = "PIGEONPEA"
    PEARL_MILLET = "PEARL_MILLET"


class CropOptionId(str, Enum):
    """V1 decision options (section 5) — deliberately distinct from
    `CropId` so JSON/logs/analytics remain self-explanatory."""

    SOYBEAN_MONOCROP = "SOYBEAN_MONOCROP"
    BLACK_GRAM_MONOCROP = "BLACK_GRAM_MONOCROP"
    PIGEONPEA_MONOCROP = "PIGEONPEA_MONOCROP"
    SOYBEAN_PIGEONPEA_INTERCROP = "SOYBEAN_PIGEONPEA_INTERCROP"
    PEARL_MILLET_MONOCROP = "PEARL_MILLET_MONOCROP"
    PEARL_MILLET_PIGEONPEA_INTERCROP = "PEARL_MILLET_PIGEONPEA_INTERCROP"


class CropOptionType(str, Enum):
    """Section 6. Explicit, never derived by parsing the option-id string."""

    MONOCROP = "MONOCROP"
    INTERCROP = "INTERCROP"


class CropOptionProductRole(str, Enum):
    """Section 7. UX/analytics/documentation metadata only — never a
    candidate-selection rule. The decision engine must never branch on this
    field; A3/A4 rules determine relevance."""

    CORE_BASELINE = "CORE_BASELINE"
    CORE_CURRENT_CROP = "CORE_CURRENT_CROP"
    DIVERSIFICATION_SYSTEM = "DIVERSIFICATION_SYSTEM"
    CLIMATE_CONTINGENCY_CROP = "CLIMATE_CONTINGENCY_CROP"
    SEVERE_DELAY_CONTINGENCY_SYSTEM = "SEVERE_DELAY_CONTINGENCY_SYSTEM"


class CropOptionStatus(str, Enum):
    """Section 9."""

    ACTIVE_V1 = "ACTIVE_V1"
    DEFERRED = "DEFERRED"
    RETIRED = "RETIRED"


class CropDefinition(BaseModel):
    """Section 4. Identity/taxonomy only — no seasons, no evidence here
    (those are option/catalog concerns, to avoid two sources of truth)."""

    model_config = ConfigDict(frozen=True)

    crop_id: CropId
    display_name_key: str
    alias_keys: tuple[str, ...] = ()


class ExternalOptionReference(BaseModel):
    """Section 15. Provenance-only pointer to a source-mentioned alternative
    that V1 does not actively model (e.g. Niger, fodder sorghum, Rabi
    planning). Never promoted into an active `CropOptionProfile`."""

    model_config = ConfigDict(frozen=True)

    canonical_key: str
    display_name_key: str | None = None
    source_ids: tuple[str, ...] = ()

    @field_validator("source_ids")
    @classmethod
    def _validate_source_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return ensure_valid_source_ids(value)


class CropOptionProfile(BaseModel):
    """Section 8. Static reference data for one V1 decision option.

    `component_crops` order carries no agronomic meaning (section 12): it
    is not main-crop/secondary-crop, not row ratio, not revenue/seed share.
    """

    model_config = ConfigDict(frozen=True)

    option_id: CropOptionId
    option_type: CropOptionType
    component_crops: tuple[CropId, ...]
    display_name_key: str
    product_role: CropOptionProductRole
    supported_seasons: tuple[Season, ...]
    evidence_source_ids: tuple[str, ...]
    status: CropOptionStatus

    @field_validator("evidence_source_ids")
    @classmethod
    def _validate_evidence_source_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return ensure_valid_source_ids(value)

    @model_validator(mode="after")
    def _validate_component_count(self) -> "CropOptionProfile":
        if self.option_type == CropOptionType.MONOCROP and len(self.component_crops) != 1:
            raise ValueError(
                f"{self.option_id}: MONOCROP options must have exactly one component crop"
            )
        if self.option_type == CropOptionType.INTERCROP and len(self.component_crops) < 2:
            raise ValueError(
                f"{self.option_id}: INTERCROP options must have at least two component crops"
            )
        return self

    @model_validator(mode="after")
    def _validate_active_v1_constraints(self) -> "CropOptionProfile":
        if self.status == CropOptionStatus.ACTIVE_V1:
            if Season.KHARIF not in self.supported_seasons:
                raise ValueError(f"{self.option_id}: active V1 options must support KHARIF")
            if not self.evidence_source_ids:
                raise ValueError(
                    f"{self.option_id}: active V1 options must have at least one evidence source id"
                )
        return self


class CropCatalog(BaseModel):
    """Section 10. Immutable, versioned registry — the decision engine
    evaluates `CropOptionProfile` entries from a specific catalog version,
    never a mutable live collection."""

    model_config = ConfigDict(frozen=True)

    catalog_id: str
    version: str
    district_scope: District
    season_scope: Season
    crop_definitions: dict[CropId, CropDefinition]
    crop_options: dict[CropOptionId, CropOptionProfile]

    @field_validator("crop_definitions", "crop_options", mode="after")
    @classmethod
    def _freeze_mapping(cls, value: dict) -> MappingProxyType:
        # A frozen Pydantic model still allows in-place mutation of a plain
        # dict field; wrap in MappingProxyType so `catalog.crop_options[x] =
        # y` raises instead of silently succeeding.
        return MappingProxyType(dict(value))

    @field_serializer("crop_definitions")
    def _serialize_crop_definitions(self, value: MappingProxyType, _info) -> dict[str, dict]:
        return {k.value: v.model_dump() for k, v in value.items()}

    @field_serializer("crop_options")
    def _serialize_crop_options(self, value: MappingProxyType, _info) -> dict[str, dict]:
        return {k.value: v.model_dump() for k, v in value.items()}

    @model_validator(mode="after")
    def _validate_components_resolve(self) -> "CropCatalog":
        for option in self.crop_options.values():
            for crop_id in option.component_crops:
                if crop_id not in self.crop_definitions:
                    raise ValueError(
                        f"{option.option_id}: component crop {crop_id} has no CropDefinition "
                        f"in this catalog"
                    )
        return self

    @model_validator(mode="after")
    def _validate_option_ids_match_keys(self) -> "CropCatalog":
        for key, option in self.crop_options.items():
            if key != option.option_id:
                raise ValueError(f"crop_options key {key} does not match option_id {option.option_id}")
        for key, definition in self.crop_definitions.items():
            if key != definition.crop_id:
                raise ValueError(f"crop_definitions key {key} does not match crop_id {definition.crop_id}")
        return self


def _profile(
    option_id: CropOptionId,
    option_type: CropOptionType,
    component_crops: tuple[CropId, ...],
    display_name_key: str,
    product_role: CropOptionProductRole,
    evidence_source_ids: tuple[str, ...],
) -> CropOptionProfile:
    return CropOptionProfile(
        option_id=option_id,
        option_type=option_type,
        component_crops=component_crops,
        display_name_key=display_name_key,
        product_role=product_role,
        supported_seasons=(Season.KHARIF,),
        evidence_source_ids=evidence_source_ids,
        status=CropOptionStatus.ACTIVE_V1,
    )


# V1 Dharashiv Kharif catalog (docs/domain/c2-crop-profile.md, sections 10-11).
# Exactly 4 atomic crops and 6 active V1 options. No production agricultural
# rules live here — this is C2 (crop reference data), not C3 (rules).
CROP_CATALOG_V1 = CropCatalog(
    catalog_id="dharashiv-kharif",
    version="1.0",
    district_scope=District.DHARASHIV,
    season_scope=Season.KHARIF,
    crop_definitions={
        CropId.SOYBEAN: CropDefinition(
            crop_id=CropId.SOYBEAN,
            display_name_key="crop.soybean.name",
        ),
        CropId.BLACK_GRAM: CropDefinition(
            crop_id=CropId.BLACK_GRAM,
            display_name_key="crop.black_gram.name",
            alias_keys=("crop.black_gram.alias.udid", "crop.black_gram.alias.urad"),
        ),
        CropId.PIGEONPEA: CropDefinition(
            crop_id=CropId.PIGEONPEA,
            display_name_key="crop.pigeonpea.name",
            alias_keys=("crop.pigeonpea.alias.tur",),
        ),
        CropId.PEARL_MILLET: CropDefinition(
            crop_id=CropId.PEARL_MILLET,
            display_name_key="crop.pearl_millet.name",
            alias_keys=("crop.pearl_millet.alias.bajra",),
        ),
    },
    crop_options={
        CropOptionId.SOYBEAN_MONOCROP: _profile(
            option_id=CropOptionId.SOYBEAN_MONOCROP,
            option_type=CropOptionType.MONOCROP,
            component_crops=(CropId.SOYBEAN,),
            display_name_key="crop_option.soybean_monocrop.name",
            product_role=CropOptionProductRole.CORE_BASELINE,
            evidence_source_ids=("SRC-001", "SRC-004", "SRC-005", "SRC-006", "SRC-007"),
        ),
        CropOptionId.BLACK_GRAM_MONOCROP: _profile(
            option_id=CropOptionId.BLACK_GRAM_MONOCROP,
            option_type=CropOptionType.MONOCROP,
            component_crops=(CropId.BLACK_GRAM,),
            display_name_key="crop_option.black_gram_monocrop.name",
            product_role=CropOptionProductRole.CORE_CURRENT_CROP,
            evidence_source_ids=("SRC-001", "SRC-005", "SRC-006"),
        ),
        CropOptionId.PIGEONPEA_MONOCROP: _profile(
            option_id=CropOptionId.PIGEONPEA_MONOCROP,
            option_type=CropOptionType.MONOCROP,
            component_crops=(CropId.PIGEONPEA,),
            display_name_key="crop_option.pigeonpea_monocrop.name",
            product_role=CropOptionProductRole.CORE_CURRENT_CROP,
            evidence_source_ids=("SRC-001", "SRC-004", "SRC-005", "SRC-006", "SRC-007"),
        ),
        CropOptionId.SOYBEAN_PIGEONPEA_INTERCROP: _profile(
            option_id=CropOptionId.SOYBEAN_PIGEONPEA_INTERCROP,
            option_type=CropOptionType.INTERCROP,
            component_crops=(CropId.SOYBEAN, CropId.PIGEONPEA),
            display_name_key="crop_option.soybean_pigeonpea.name",
            product_role=CropOptionProductRole.DIVERSIFICATION_SYSTEM,
            evidence_source_ids=("SRC-005", "SRC-006", "SRC-011", "SRC-013"),
        ),
        CropOptionId.PEARL_MILLET_MONOCROP: _profile(
            option_id=CropOptionId.PEARL_MILLET_MONOCROP,
            option_type=CropOptionType.MONOCROP,
            component_crops=(CropId.PEARL_MILLET,),
            display_name_key="crop_option.pearl_millet_monocrop.name",
            product_role=CropOptionProductRole.CLIMATE_CONTINGENCY_CROP,
            evidence_source_ids=("SRC-001", "SRC-006", "SRC-007", "SRC-012"),
        ),
        CropOptionId.PEARL_MILLET_PIGEONPEA_INTERCROP: _profile(
            option_id=CropOptionId.PEARL_MILLET_PIGEONPEA_INTERCROP,
            option_type=CropOptionType.INTERCROP,
            component_crops=(CropId.PEARL_MILLET, CropId.PIGEONPEA),
            display_name_key="crop_option.pearl_millet_pigeonpea_intercrop.name",
            product_role=CropOptionProductRole.SEVERE_DELAY_CONTINGENCY_SYSTEM,
            evidence_source_ids=("SRC-006", "SRC-013"),
        ),
    },
)
