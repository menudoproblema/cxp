from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.common import (
    CXP_RESOURCE_NAME,
    CXP_OPERATION_NAME,
    CXP_OPERATION_STATUS,
)
from cxp.catalogs.results import (
    AuthClaims,
    UserProfile,
)

AUTH_PROVIDER_INTERFACE = "identity/auth-provider"

# Capability Names
AUTH_TOKEN_INTROSPECTION = "token_introspection"
AUTH_USER_INFO = "user_info"
AUTH_POLICY_ENFORCEMENT = "policy_enforcement"

# Operation Names (Standardized: AUTH_OP_{ACTION})
AUTH_OP_INTROSPECT = "auth.introspect_token"
AUTH_OP_GET_USER = "auth.get_user_info"
AUTH_OP_AUTHORIZE = "auth.authorize_action"

class TokenMetadata(msgspec.Struct, frozen=True):
    supported_algorithms: tuple[str, ...]
    issuer: str

AUTH_PROVIDER_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=AUTH_PROVIDER_INTERFACE,
        description="Canonical catalog for identity and access management.",
        capabilities=(
            CatalogCapability(
                name=AUTH_TOKEN_INTROSPECTION,
                description="Validation and metadata extraction from security tokens.",
                metadata_schema=TokenMetadata,
                operations=(
                    CatalogOperation(
                        name=AUTH_OP_INTROSPECT,
                        result_type="auth.token_claims",
                        result_schema=AuthClaims,
                        description="Validate a token and return its claims.",
                    ),
                ),
            ),
            CatalogCapability(
                name=AUTH_USER_INFO,
                description="Resolution of user profiles from identities.",
                operations=(
                    CatalogOperation(
                        name=AUTH_OP_GET_USER,
                        result_type="auth.user_profile",
                        result_schema=UserProfile,
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(AUTH_TOKEN_INTROSPECTION,),
                description="Basic identity validator.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "AUTH_PROVIDER_CATALOG",
    "AUTH_PROVIDER_INTERFACE",
    "AUTH_OP_INTROSPECT",
    "AUTH_OP_GET_USER",
    "AUTH_OP_AUTHORIZE",
)
