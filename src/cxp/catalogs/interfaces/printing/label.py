from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.interfaces.printing.family import PRINTING_INTERFACE
from cxp.catalogs.results import LabelMetadata

LABEL_PRINTING_INTERFACE = "printing/label"

# Capability Names
LABEL_ZPL_SUPPORT = "zpl_language"
LABEL_THERMAL_MANAGEMENT = "thermal_management"
LABEL_MEDIA_VALIDATION = "media_validation"

# Operation Names
LABEL_OP_GET_MEDIA_INFO = "label.get_media_info"

LABEL_PRINTING_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=LABEL_PRINTING_INTERFACE,
        satisfies_interfaces=(PRINTING_INTERFACE,),
        description=(
            "Canonical catalog for label printers (Zebra, TSC), with focus on "
            "ZPL/TSPL languages and precise media validation."
        ),
        capabilities=(
            CatalogCapability(
                name=LABEL_ZPL_SUPPORT,
                description="Support for Zebra Programming Language (ZPL).",
            ),
            CatalogCapability(
                name=LABEL_MEDIA_VALIDATION,
                description="Validation of label dimensions and sensor type.",
                metadata_schema=LabelMetadata,
                operations=(
                    CatalogOperation(
                        name=LABEL_OP_GET_MEDIA_INFO,
                        result_type="label.metadata",
                        result_schema=LabelMetadata,
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="industrial",
                required_capabilities=(LABEL_ZPL_SUPPORT, LABEL_MEDIA_VALIDATION),
                description="Professional industrial label printer.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "LABEL_PRINTING_CATALOG",
    "LABEL_PRINTING_INTERFACE",
)
