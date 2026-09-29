"""Agronomy Rules module.

Owns: versioned crop profiles and contingency rules sourced from approved
research (docs/product/PRD.md, section 11; CLAUDE.md, section 5 "Domain
Rules Are Controlled Requirements").

C2 (crop/crop-option catalog) is implemented in `crops.py`, per
docs/domain/c2-crop-profile.md. C3 (decision rule schema) is implemented in
`rules.py`, per docs/domain/c3-decision-rule.md.

`rules.RULE_CATALOG_V1` intentionally contains zero agricultural rules —
the A3/A4 contingency matrix has not been approved into production rules
yet (see docs/planning/v1-execution-graph.md, Phase D gating). No rule
evaluator exists in this module.
"""
