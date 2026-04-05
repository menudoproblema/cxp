from cxp.catalogs.base import CapabilityCatalog, register_catalog

BROWSER_AUTOMATION_INTERFACE = "browser/automation"

BROWSER_AUTOMATION_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=BROWSER_AUTOMATION_INTERFACE,
        abstract=True,
        description=(
            "Abstract family for browser automation providers exposed to the "
            "orchestrator."
        ),
    )
)

__all__ = (
    "BROWSER_AUTOMATION_CATALOG",
    "BROWSER_AUTOMATION_INTERFACE",
)
