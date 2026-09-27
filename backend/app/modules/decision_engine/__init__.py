"""Decision Engine module.

Owns: candidate filtering, scenario scoring and explanation generation
(docs/product/PRD.md, section 8 "Decision Engine Requirements"). Must remain
explainable — every output traceable to inputs, rule versions and data
timestamps (CLAUDE.md, section 11).

Depends on Agronomy Rules and Data Adapters; must not be implemented ahead
of an approved rule matrix (docs/planning/v1-execution-graph.md, Phase D).
Not yet implemented.
"""
