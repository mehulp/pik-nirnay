"""Field Profile module.

Owns: validation of location, soil class, irrigation availability and
sowing date entered by the user (docs/product/PRD.md, section 11).

C1 (AssessmentContext and its component models) is implemented in
`context.py`, per docs/domain/c1-farm-context.md. The taluka -> rainfall
zone resolver lives separately in `location_resolver.py`.

Acreage/budget capture and any application-level policy (e.g. rejecting
RESOWING as unsupported by V1 rules) are not yet implemented.
"""
