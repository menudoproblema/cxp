from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.interfaces.printing.family import PRINTING_INTERFACE
from cxp.catalogs.results import ActionResult

PRODUCTION_PRINTING_INTERFACE = "printing/production"

# Capability Names (Finishing/Accesorios)
PRODUCTION_FOLDING = "folding"  # Plegador
PRODUCTION_GLUING = "gluing"    # Encolador
PRODUCTION_STAPLING = "stapling"
PRODUCTION_COLOR_CALIBRATION = "color_calibration"

class FinishingMetadata(msgspec.Struct, frozen=True):
    supported_folds: tuple[str, ...]  # z-fold, tri-fold, half-fold
    glue_types: tuple[str, ...]
    max_thickness_mm: float

PRODUCTION_PRINTING_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=PRODUCTION_PRINTING_INTERFACE,
        satisfies_interfaces=(PRINTING_INTERFACE,),
        description=(
            "Canonical catalog for high-volume production printers (Konica "
            "Minolta), focusing on finishing accessories and color precision."
        ),
        capabilities=(
            CatalogCapability(
                name=PRODUCTION_FOLDING,
                description="Physical paper folding (plegado) capabilities.",
                metadata_schema=FinishingMetadata,
            ),
            CatalogCapability(
                name=PRODUCTION_GLUING,
                description="Physical paper gluing (encolado) capabilities.",
            ),
            CatalogCapability(
                name=PRODUCTION_COLOR_CALIBRATION,
                description="Advanced color management and calibration.",
                operations=(
                    CatalogOperation(
                        name="production.calibrate",
                        result_type="action.result",
                        result_schema=ActionResult,
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="finisher",
                required_capabilities=(PRODUCTION_FOLDING, PRODUCTION_GLUING),
                description="Production printer with physical finishing accessories.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "PRODUCTION_PRINTING_CATALOG",
    "PRODUCTION_PRINTING_INTERFACE",
)
