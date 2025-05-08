"""
Object storage package for the Top Songs application.
"""

from .s3 import ObjectStoreInterface, object_store

__all__ = ["ObjectStoreInterface", "object_store"]
