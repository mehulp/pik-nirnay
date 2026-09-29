"""Cross-cutting enums shared by C1 (field_profile), C2 and C3 (agronomy_rules).

docs/domain/c1-farm-context.md and docs/domain/c3-decision-rule.md both
reference `Season` and `District`; this is their single authoritative
definition (see task instructions: "Do NOT independently redefine Season or
District in multiple C1/C2/C3 modules").
"""

from enum import Enum


class Season(str, Enum):
    """V1 supports only Kharif (docs/domain/c1-farm-context.md, section 3)."""

    KHARIF = "KHARIF"


class District(str, Enum):
    """V1 rules are Dharashiv-specific (docs/domain/c1-farm-context.md, section 6.1)."""

    DHARASHIV = "DHARASHIV"
