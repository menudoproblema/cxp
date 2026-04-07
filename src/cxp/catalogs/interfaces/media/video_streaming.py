from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    CapabilityTelemetry,
    TelemetryMetricSpec,
    register_catalog,
)
from cxp.catalogs.common import (
    CXP_RESOURCE_NAME,
    CXP_DURATION,
    UNIT_BITS_PER_SEC,
    UNIT_SECONDS,
)
from cxp.catalogs.results import (
    MediaManifest,
    TranscodingJob,
)
from cxp.catalogs.interfaces.execution.plan_run import (
    PLAN_RUN_EXECUTION_INTERFACE,
    PLAN_RUN_OP_STATUS,
)

VIDEO_STREAMING_INTERFACE = "media/video-streaming"

# Capability Names
VIDEO_ADAPTIVE_STREAMING = "adaptive_streaming"
VIDEO_TRANSCODING = "transcoding"
VIDEO_DRM_PROTECTION = "drm_protection"

# Operation Names
VIDEO_OP_PREPARE = "media.prepare_stream"
VIDEO_OP_START_JOB = "media.transcode_job_start"

class StreamingMetadata(msgspec.Struct, frozen=True):
    supported_formats: tuple[str, ...]
    max_resolution: str
    codecs: tuple[str, ...]

_MEDIA_TELEMETRY = CapabilityTelemetry(
    metrics=(
        TelemetryMetricSpec(
            name="media.playback.bitrate",
            unit=UNIT_BITS_PER_SEC,
            required_labels=(CXP_RESOURCE_NAME,),
        ),
        TelemetryMetricSpec(
            name="media.playback.buffering_seconds",
            unit=UNIT_SECONDS,
            required_labels=(CXP_RESOURCE_NAME,),
        ),
    ),
)

VIDEO_STREAMING_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=VIDEO_STREAMING_INTERFACE,
        satisfies_interfaces=(PLAN_RUN_EXECUTION_INTERFACE,),
        description=(
            "Standard catalog for video streaming providers, covering VOD, "
            "adaptive bitrate (ABR) packaging, and transcoding pipelines."
        ),
        capabilities=(
            CatalogCapability(
                name=VIDEO_ADAPTIVE_STREAMING,
                description="Delivery of ABR content via HLS or DASH manifests.",
                metadata_schema=StreamingMetadata,
                telemetry=_MEDIA_TELEMETRY,
                operations=(
                    CatalogOperation(
                        name=VIDEO_OP_PREPARE,
                        result_type="media.manifest",
                        result_schema=MediaManifest,
                        description="Generate a secure streaming manifest URL.",
                    ),
                ),
            ),
            CatalogCapability(
                name=VIDEO_TRANSCODING,
                description="Converting raw video into multi-bitrate profiles.",
                operations=(
                    CatalogOperation(
                        name=VIDEO_OP_START_JOB,
                        result_type="media.job_id",
                    ),
                    CatalogOperation(
                        name=PLAN_RUN_OP_STATUS,
                        result_type="media.job_status",
                        result_schema=TranscodingJob,
                        description="Query the status of a transcoding job (satisfies execution base).",
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(VIDEO_ADAPTIVE_STREAMING,),
                description="Standard VOD delivery provider.",
            ),
            ConformanceTier(
                name="transcoder",
                required_capabilities=(VIDEO_ADAPTIVE_STREAMING, VIDEO_TRANSCODING),
                description="Full-service provider with ingest and transcoding.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "VIDEO_STREAMING_CATALOG",
    "VIDEO_STREAMING_INTERFACE",
)
