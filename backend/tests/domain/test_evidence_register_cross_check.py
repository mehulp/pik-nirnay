"""Cross-checks C2/C3 evidence source ids against docs/research/evidence-register.md.

Per the task instructions (section 9): "Validate their syntax/shape
appropriately and ensure all IDs used by the six reviewed profiles match
IDs actually documented in the Evidence Register." This test reads the
register directly rather than duplicating its contents as a Python
registry.
"""

import re
from pathlib import Path

from app.modules.agronomy_rules.crops import CROP_CATALOG_V1

_EVIDENCE_REGISTER_PATH = Path(__file__).resolve().parents[3] / "docs" / "research" / "evidence-register.md"
_HEADING_SRC_PATTERN = re.compile(r"^#{1,3}\s+(SRC-\d+)\b", re.MULTILINE)


def _documented_source_ids() -> set[str]:
    text = _EVIDENCE_REGISTER_PATH.read_text(encoding="utf-8")
    return set(_HEADING_SRC_PATTERN.findall(text))


def test_evidence_register_is_readable():
    assert _EVIDENCE_REGISTER_PATH.is_file()
    assert len(_documented_source_ids()) > 0


def test_all_crop_catalog_evidence_ids_are_documented():
    documented = _documented_source_ids()
    used = {
        source_id
        for option in CROP_CATALOG_V1.crop_options.values()
        for source_id in option.evidence_source_ids
    }
    undocumented = used - documented
    assert not undocumented, f"evidence ids used in CROP_CATALOG_V1 but not in evidence register: {undocumented}"
