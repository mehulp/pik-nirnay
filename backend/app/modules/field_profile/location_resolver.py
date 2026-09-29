"""C1 — deterministic taluka -> rainfall-zone resolver.

Authoritative source: docs/domain/c1-farm-context.md, sections 6.4 and 18.

This is location normalization derived from the legacy Dharashiv
contingency plan, not crop recommendation logic. It is intentionally kept
separate from the `LocationContext` model: this function only computes the
zone. Callers are responsible for setting `rainfall_zone_source =
ContextSource.RULE_DERIVED` when they use this resolver's output to build a
`LocationContext`.
"""

from __future__ import annotations

from app.modules.field_profile.context import RainfallZone, Taluka

_LOWER_RAINFALL_TALUKAS: frozenset[Taluka] = frozenset({Taluka.BHOOM, Taluka.PARANDA})

_OTHER_DHARASHIV_TALUKAS: frozenset[Taluka] = frozenset(
    {
        Taluka.DHARASHIV,
        Taluka.TULJAPUR,
        Taluka.OMERGA,
        Taluka.LOHARA,
        Taluka.KALLAM,
        Taluka.WASHI,
    }
)


def resolve_rainfall_zone(taluka: Taluka) -> RainfallZone:
    """Map a Dharashiv taluka to its rainfall zone.

    BHOOM, PARANDA                              -> LOWER_RAINFALL_BHOOM_PARANDA
    DHARASHIV, TULJAPUR, OMERGA, LOHARA,
    KALLAM, WASHI                                -> OTHER_DHARASHIV
    UNKNOWN (or anything else)                   -> UNKNOWN
    """
    if taluka in _LOWER_RAINFALL_TALUKAS:
        return RainfallZone.LOWER_RAINFALL_BHOOM_PARANDA
    if taluka in _OTHER_DHARASHIV_TALUKAS:
        return RainfallZone.OTHER_DHARASHIV
    return RainfallZone.UNKNOWN
