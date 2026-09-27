"""Data Adapters module.

Owns: external provider clients (weather, climate, market), response
validation, retries/fallbacks and normalization into project-owned domain
contracts. Provider-specific schemas must never leak past this module
(docs/product/PRD.md, section 10 "Data Sources and Provider Strategy").

Provider contracts and implementations are a separate task
(docs/planning/v1-execution-graph.md, Phase B) — only the module boundary
is established here.
"""
