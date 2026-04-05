from cxp.catalogs.base import CapabilityCatalog, register_catalog

HTTP_APPLICATION_INTERFACE = "application/http"

HTTP_APPLICATION_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=HTTP_APPLICATION_INTERFACE,
        abstract=True,
        description=(
            "Abstract family for any HTTP application exposed to the "
            "orchestrator."
        ),
    )
)

__all__ = (
    "HTTP_APPLICATION_CATALOG",
    "HTTP_APPLICATION_INTERFACE",
)
