"""Database engine/session scaffolding.

This module only owns connectivity plumbing (engine, session factory, the
declarative base). No ORM models exist yet — they will be added alongside
the domain modules that need persistence, along with Alembic migrations.
"""
