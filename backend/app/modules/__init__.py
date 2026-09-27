"""Domain modules of the Pik Nirnay modular monolith.

Each submodule is an isolated boundary (see docs/product/PRD.md, section 11
"Technical Architecture"). Modules communicate through explicit contracts,
not shared mutable state, so that any module could later be split into its
own service without redesigning the others.
"""
