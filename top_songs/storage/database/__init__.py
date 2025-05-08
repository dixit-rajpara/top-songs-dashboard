"""
Database storage package for the Top Songs application.
"""

from .postgres import PostgresInterface, postgres_db

__all__ = ["PostgresInterface", "postgres_db"]
