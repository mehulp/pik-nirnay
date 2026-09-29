"""Shared domain primitives reused across C1/C2/C3.

Holds only the handful of enums/types that genuinely span multiple domain
modules (e.g. `Season`, `District`), so each is defined exactly once instead
of being redefined per module. This is not a general-purpose dumping
ground — anything specific to one module's domain belongs in that module.
"""
