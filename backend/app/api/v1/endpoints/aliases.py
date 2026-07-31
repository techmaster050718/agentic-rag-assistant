from __future__ import annotations

"""
Convenience alias routes.
All routes here are thin wrappers that delegate to the canonical endpoints.
NO duplicate route paths — each alias has a unique path.
"""

from fastapi import APIRouter

router = APIRouter()

# This module intentionally contains no duplicate routes.
# If you need to add an alias, use a different path prefix, e.g.:
#
# @router.get("/v1/health-check", include_in_schema=False)
# async def health_alias():
#     from app.api.v1.endpoints.health import health_check
#     return await health_check()
