"""C1 location resolver tests (docs/domain/c1-farm-context.md, section 18)."""

import pytest

from app.modules.field_profile.context import RainfallZone, Taluka
from app.modules.field_profile.location_resolver import resolve_rainfall_zone


def test_bhoom_resolves_to_lower_rainfall_zone():
    assert resolve_rainfall_zone(Taluka.BHOOM) == RainfallZone.LOWER_RAINFALL_BHOOM_PARANDA


def test_paranda_resolves_to_lower_rainfall_zone():
    assert resolve_rainfall_zone(Taluka.PARANDA) == RainfallZone.LOWER_RAINFALL_BHOOM_PARANDA


@pytest.mark.parametrize(
    "taluka",
    [
        Taluka.DHARASHIV,
        Taluka.TULJAPUR,
        Taluka.OMERGA,
        Taluka.LOHARA,
        Taluka.KALLAM,
        Taluka.WASHI,
    ],
)
def test_other_dharashiv_talukas_resolve_to_other_dharashiv(taluka: Taluka):
    assert resolve_rainfall_zone(taluka) == RainfallZone.OTHER_DHARASHIV


def test_unknown_taluka_resolves_to_unknown_zone():
    assert resolve_rainfall_zone(Taluka.UNKNOWN) == RainfallZone.UNKNOWN


def test_resolver_covers_every_taluka_member():
    # No Taluka should be silently unhandled (guards against a future
    # Taluka addition that the resolver's static sets forget to cover).
    for taluka in Taluka:
        zone = resolve_rainfall_zone(taluka)
        assert isinstance(zone, RainfallZone)
