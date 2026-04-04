from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    ConformanceTier,
    register_catalog,
)

MONGODB_INTERFACE = "database/mongodb"

MONGODB_READ = "read"
MONGODB_WRITE = "write"
MONGODB_PERSISTENCE = "persistence"
MONGODB_TRANSACTIONS = "transactions"
MONGODB_CHANGE_STREAMS = "change_streams"
MONGODB_AGGREGATION = "aggregation"
MONGODB_SEARCH = "search"
MONGODB_VECTOR_SEARCH = "vector_search"
MONGODB_COLLATION = "collation"
MONGODB_TOPOLOGY_DISCOVERY = "topology_discovery"

MONGODB_CORE_TIER = "core"
MONGODB_SEARCH_TIER = "search"
MONGODB_PLATFORM_TIER = "platform"

MONGODB_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=MONGODB_INTERFACE,
        description=(
            "Estándar CXP para proveedores compatibles con la interfaz "
            "database/mongodb."
        ),
        capabilities=(
            CatalogCapability(
                name=MONGODB_READ,
                description="Consultas básicas de lectura.",
            ),
            CatalogCapability(
                name=MONGODB_WRITE,
                description="Inserción, actualización y borrado de documentos.",
            ),
            CatalogCapability(
                name=MONGODB_TRANSACTIONS,
                description="Operaciones multi-documento atómicas.",
            ),
            CatalogCapability(
                name=MONGODB_AGGREGATION,
                description="Soporte para el framework de agregación.",
            ),
            CatalogCapability(
                name=MONGODB_CHANGE_STREAMS,
                description="Observabilidad de cambios en tiempo real.",
            ),
            CatalogCapability(
                name=MONGODB_SEARCH,
                description="Soporte para consultas textuales de tipo search.",
            ),
            CatalogCapability(
                name=MONGODB_VECTOR_SEARCH,
                description="Búsquedas por similitud semántica.",
            ),
            CatalogCapability(
                name=MONGODB_COLLATION,
                description="Ordenación y comparación sensibles a collation.",
            ),
            CatalogCapability(
                name=MONGODB_PERSISTENCE,
                description="Persistencia de datos más allá del proceso.",
            ),
            CatalogCapability(
                name=MONGODB_TOPOLOGY_DISCOVERY,
                description="Descubrimiento de topología y estado de nodos.",
            ),
        ),
        tiers=(
            ConformanceTier(
                name=MONGODB_CORE_TIER,
                required_capabilities=(
                    MONGODB_READ,
                    MONGODB_WRITE,
                    MONGODB_AGGREGATION,
                ),
                description="Contrato mínimo interoperable para proveedores MongoDB.",
            ),
            ConformanceTier(
                name=MONGODB_SEARCH_TIER,
                required_capabilities=(
                    MONGODB_READ,
                    MONGODB_WRITE,
                    MONGODB_SEARCH,
                    MONGODB_VECTOR_SEARCH,
                ),
                description="Capacidades de búsqueda textual y vectorial.",
            ),
            ConformanceTier(
                name=MONGODB_PLATFORM_TIER,
                required_capabilities=(
                    MONGODB_READ,
                    MONGODB_WRITE,
                    MONGODB_TRANSACTIONS,
                    MONGODB_CHANGE_STREAMS,
                    MONGODB_COLLATION,
                    MONGODB_PERSISTENCE,
                    MONGODB_TOPOLOGY_DISCOVERY,
                ),
                description="Capacidades de plataforma y operación de runtime.",
            ),
        ),
    )
)

MONGODB_MINIMAL_CAPABILITIES = (
    MONGODB_READ,
    MONGODB_WRITE,
    MONGODB_AGGREGATION,
)
MONGODB_FULL_CAPABILITIES = MONGODB_CATALOG.capability_names()
