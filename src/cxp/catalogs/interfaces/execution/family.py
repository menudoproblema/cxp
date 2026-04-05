from cxp.catalogs.base import CapabilityCatalog, register_catalog

EXECUTION_ENGINE_FAMILY_INTERFACE = "execution/engine"

EXECUTION_ENGINE_FAMILY_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=EXECUTION_ENGINE_FAMILY_INTERFACE,
        abstract=True,
        description=(
            "Abstract family for execution-oriented engines exposed to the "
            "orchestrator."
        ),
    )
)

__all__ = (
    "EXECUTION_ENGINE_FAMILY_CATALOG",
    "EXECUTION_ENGINE_FAMILY_INTERFACE",
)
