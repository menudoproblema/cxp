from __future__ import annotations

from collections.abc import Iterable, Mapping
from threading import RLock

import msgspec

from cxp.capabilities import Capability, CapabilityMatrix
from cxp.catalogs.validation import (
    catalog_definition_issues,
    catalog_relation_issues,
    definition_is_immutable,
)
from cxp.descriptors import (
    CapabilityDescriptor,
    ComponentCapabilitySnapshot,
    DescriptorValidationResult,
    UnknownCapabilityOperations,
    offered_capability_names,
)
from cxp.telemetry import TelemetrySeverity, TelemetrySnapshot
from cxp.validation import (
    ContractValidationError,
    ValidationIssue,
    ValidationResult,
    duplicate_issues,
    validate_typed_metadata,
)

type CatalogTierName = str
type CapabilityMetadataSchema = type[msgspec.Struct] | None


class CapabilityRequirement(msgspec.Struct, frozen=True):
    capability_name: str
    required_operations: tuple[str, ...] = ()
    required_metadata_keys: tuple[str, ...] = ()


class CapabilityProfileDefinitionValidationResult(msgspec.Struct, frozen=True):
    unknown_capabilities: tuple[str, ...] = ()
    unknown_operations: tuple[UnknownCapabilityOperations, ...] = ()
    unknown_metadata_keys: tuple[str, ...] = ()
    interface_mismatch: str | None = None
    expected_interface: str | None = None
    diagnostics: tuple[ValidationIssue, ...] = ()

    def is_valid(self) -> bool:
        return (
            not self.unknown_capabilities
            and not self.unknown_operations
            and not self.unknown_metadata_keys
            and self.interface_mismatch is None
            and not self.diagnostics
        )

    def messages(self) -> tuple[str, ...]:
        messages: list[str] = []

        if self.unknown_capabilities:
            messages.append(
                "Unknown profile capabilities: " + ", ".join(self.unknown_capabilities),
            )

        if self.unknown_operations:
            for unknown in self.unknown_operations:
                messages.append(
                    "Unknown profile operations for capability "
                    f"{unknown.capability_name!r}: "
                    + ", ".join(unknown.operation_names),
                )

        if self.unknown_metadata_keys:
            messages.append(
                "Unknown profile metadata keys: "
                + ", ".join(self.unknown_metadata_keys),
            )

        if self.interface_mismatch is not None:
            messages.append(
                "Interface mismatch: "
                f"{self.interface_mismatch!r} != {self.expected_interface!r}",
            )

        messages.extend(issue.message for issue in self.diagnostics)
        return tuple(messages)


class TelemetryFieldRequirement(msgspec.Struct, frozen=True):
    name: str
    description: str | None = None


class TelemetrySpanSpec(msgspec.Struct, frozen=True):
    name: str
    required_attributes: tuple[TelemetryFieldRequirement, ...] = ()
    description: str | None = None


class TelemetryMetricSpec(msgspec.Struct, frozen=True):
    name: str
    unit: str | None = None
    required_labels: tuple[TelemetryFieldRequirement, ...] = ()
    description: str | None = None


class TelemetryEventSpec(msgspec.Struct, frozen=True):
    event_type: str
    severity: TelemetrySeverity | None = None
    required_payload_keys: tuple[TelemetryFieldRequirement, ...] = ()
    description: str | None = None


class CapabilityTelemetry(msgspec.Struct, frozen=True):
    spans: tuple[TelemetrySpanSpec, ...] = ()
    metrics: tuple[TelemetryMetricSpec, ...] = ()
    events: tuple[TelemetryEventSpec, ...] = ()
    description: str | None = None


class TelemetryValidationResult(msgspec.Struct, frozen=True):
    unknown_capabilities: tuple[str, ...] = ()
    unknown_spans: tuple[str, ...] = ()
    unknown_metrics: tuple[str, ...] = ()
    unknown_events: tuple[str, ...] = ()
    missing_span_attributes: tuple[str, ...] = ()
    missing_metric_labels: tuple[str, ...] = ()
    missing_event_payload_keys: tuple[str, ...] = ()
    invalid_metric_units: tuple[str, ...] = ()
    invalid_event_severities: tuple[str, ...] = ()

    def is_valid(self) -> bool:
        return (
            not self.unknown_capabilities
            and not self.unknown_spans
            and not self.unknown_metrics
            and not self.unknown_events
            and not self.missing_span_attributes
            and not self.missing_metric_labels
            and not self.missing_event_payload_keys
            and not self.invalid_metric_units
            and not self.invalid_event_severities
        )

    def messages(self) -> tuple[str, ...]:
        messages: list[str] = []

        if self.unknown_capabilities:
            messages.append(
                "Unknown capabilities for telemetry validation: "
                + ", ".join(self.unknown_capabilities),
            )

        if self.unknown_spans:
            messages.append("Unknown telemetry spans: " + ", ".join(self.unknown_spans))

        if self.unknown_metrics:
            messages.append(
                "Unknown telemetry metrics: " + ", ".join(self.unknown_metrics),
            )

        if self.unknown_events:
            messages.append(
                "Unknown telemetry events: " + ", ".join(self.unknown_events)
            )

        if self.missing_span_attributes:
            messages.append(
                "Missing span attributes: " + ", ".join(self.missing_span_attributes),
            )

        if self.missing_metric_labels:
            messages.append(
                "Missing metric labels: " + ", ".join(self.missing_metric_labels),
            )

        if self.missing_event_payload_keys:
            messages.append(
                "Missing event payload keys: "
                + ", ".join(self.missing_event_payload_keys),
            )

        if self.invalid_metric_units:
            messages.append(
                "Invalid metric units: " + ", ".join(self.invalid_metric_units),
            )

        if self.invalid_event_severities:
            messages.append(
                "Invalid event severities: " + ", ".join(self.invalid_event_severities),
            )

        return tuple(messages)


class CapabilityProfileValidationResult(msgspec.Struct, frozen=True):
    unknown_profile_capabilities: tuple[str, ...] = ()
    missing_capabilities: tuple[str, ...] = ()
    missing_operations: tuple[UnknownCapabilityOperations, ...] = ()
    missing_metadata_keys: tuple[str, ...] = ()
    invalid_metadata: tuple[str, ...] = ()
    interface_mismatch: str | None = None
    expected_interface: str | None = None
    diagnostics: tuple[ValidationIssue, ...] = ()

    def is_valid(self) -> bool:
        return (
            not self.unknown_profile_capabilities
            and not self.missing_capabilities
            and not self.missing_operations
            and not self.missing_metadata_keys
            and not self.invalid_metadata
            and self.interface_mismatch is None
            and not self.diagnostics
        )

    def messages(self) -> tuple[str, ...]:
        messages: list[str] = []

        if self.unknown_profile_capabilities:
            messages.append(
                "Unknown profile capabilities: "
                + ", ".join(self.unknown_profile_capabilities),
            )

        if self.missing_capabilities:
            messages.append(
                "Missing capabilities: " + ", ".join(self.missing_capabilities),
            )

        if self.missing_operations:
            for unknown in self.missing_operations:
                messages.append(
                    "Missing operations for capability "
                    f"{unknown.capability_name!r}: "
                    + ", ".join(unknown.operation_names),
                )

        if self.missing_metadata_keys:
            messages.append(
                "Missing metadata keys: " + ", ".join(self.missing_metadata_keys),
            )

        if self.invalid_metadata:
            messages.append(
                "Invalid metadata for capabilities: "
                + ", ".join(self.invalid_metadata),
            )

        if self.interface_mismatch is not None:
            messages.append(
                "Interface mismatch: "
                f"{self.interface_mismatch!r} != {self.expected_interface!r}",
            )

        messages.extend(
            issue.message
            for issue in self.diagnostics
            if issue.code != "invalid_metadata"
        )
        return tuple(messages)


class CapabilityProfile(msgspec.Struct, frozen=True):
    name: str
    interface: str
    requirements: tuple[CapabilityRequirement, ...]
    description: str | None = None

    def __post_init__(self) -> None:
        catalog = get_catalog(self.interface)
        if catalog is None:
            msg = (
                f"Capability profile {self.name!r} references "
                f"unregistered interface {self.interface!r}"
            )
            raise ValueError(msg)

        validation = catalog.validate_profile_definition(self)
        if validation.is_valid():
            return

        msg = (
            f"Invalid capability profile {self.name!r} for "
            f"interface {self.interface!r}: " + "; ".join(validation.messages())
        )
        raise ValueError(msg)


class CapabilityMatrixValidationResult(msgspec.Struct, frozen=True):
    unknown_capabilities: tuple[str, ...] = ()
    invalid_metadata: tuple[str, ...] = ()
    required_tier: CatalogTierName | None = None
    missing_tier_capabilities: tuple[str, ...] = ()
    unknown_required_tier: CatalogTierName | None = None
    diagnostics: tuple[ValidationIssue, ...] = ()

    def is_valid(self) -> bool:
        return (
            not self.unknown_capabilities
            and not self.invalid_metadata
            and not self.missing_tier_capabilities
            and self.unknown_required_tier is None
            and not self.diagnostics
        )

    def messages(self) -> tuple[str, ...]:
        messages: list[str] = []

        if self.unknown_capabilities:
            messages.append(
                "Unknown capabilities: " + ", ".join(self.unknown_capabilities),
            )

        if self.invalid_metadata:
            messages.append(
                "Invalid metadata for capabilities: "
                + ", ".join(self.invalid_metadata),
            )

        if self.unknown_required_tier is not None:
            messages.append(
                f"Unknown required tier: {self.unknown_required_tier!r}",
            )
        elif self.required_tier is not None and self.missing_tier_capabilities:
            messages.append(
                "Missing capabilities for required tier "
                f"{self.required_tier!r}: " + ", ".join(self.missing_tier_capabilities),
            )

        messages.extend(
            issue.message
            for issue in self.diagnostics
            if issue.code != "invalid_metadata"
        )
        return tuple(messages)


class CatalogOperation(msgspec.Struct, frozen=True):
    name: str
    input_schema: CapabilityMetadataSchema = None  # Validation for request
    result_type: str | None = None
    result_schema: CapabilityMetadataSchema = None  # Validation for response
    idempotent: bool = False  # Safe to retry?
    timeout_seconds: float | None = None  # Recommended timeout
    description: str | None = None


class CatalogCapability(msgspec.Struct, frozen=True):
    name: str
    description: str | None = None
    operations: tuple[CatalogOperation, ...] = ()
    metadata_schema: CapabilityMetadataSchema = None
    telemetry: CapabilityTelemetry | None = None

    def operation_names(self) -> tuple[str, ...]:
        return tuple(operation.name for operation in self.operations)

    def has_operation(self, name: str) -> bool:
        return any(operation.name == name for operation in self.operations)

    def get_operation(self, name: str) -> CatalogOperation | None:
        for operation in self.operations:
            if operation.name == name:
                return operation
        return None

    def metadata_keys(self) -> tuple[str, ...]:
        if self.metadata_schema is None:
            return ()

        return tuple(getattr(self.metadata_schema, "__struct_fields__", ()))

    def validate_metadata(self, capability: Capability) -> bool:
        return self.validate_metadata_detailed(capability).is_valid()

    def validate_metadata_detailed(
        self, capability: Capability, *, path: str = "/metadata"
    ) -> ValidationResult:
        return validate_typed_metadata(
            capability.metadata, self.metadata_schema, path=path
        )


class ConformanceTier(msgspec.Struct, frozen=True):
    name: CatalogTierName
    required_capabilities: tuple[str, ...]
    description: str | None = None

    def is_satisfied_by(self, capability_names: Iterable[str]) -> bool:
        offered = frozenset(capability_names)
        return all(name in offered for name in self.required_capabilities)


class CapabilityCatalog(msgspec.Struct, frozen=True, dict=True):
    interface: str
    capabilities: tuple[CatalogCapability, ...] = ()
    tiers: tuple[ConformanceTier, ...] = ()
    description: str | None = None
    abstract: bool = False
    satisfies_interfaces: tuple[str, ...] = ()

    def validate_definition(self) -> ValidationResult:
        # La caché es privada de la instancia y no añade campos al contrato JSON.
        cached = self.__dict__.get("_definition_validation")
        if isinstance(cached, ValidationResult):
            return cached
        validation = ValidationResult(issues=catalog_definition_issues(self))
        # Solo fijamos resultados de árboles congelados, no de contenedores mutables.
        cacheable = self.__dict__.get("_definition_cacheable")
        if cacheable is None:
            cacheable = definition_is_immutable(self)
            self.__dict__["_definition_cacheable"] = cacheable
        if cacheable:
            self.__dict__["_definition_validation"] = validation
        return validation

    def _ensure_concrete(
        self,
        operation_name: str,
    ) -> None:
        # No evaluamos contra un catálogo con identidades ambiguas.
        validation = self.validate_definition()
        if not validation.is_valid():
            raise ContractValidationError(validation.issues)
        if not self.abstract:
            return

        msg = f"Abstract catalog {self.interface!r} cannot perform {operation_name}"
        raise ValueError(msg)

    def capability_names(self) -> tuple[str, ...]:
        return tuple(capability.name for capability in self.capabilities)

    def has_capability(self, name: str) -> bool:
        return any(capability.name == name for capability in self.capabilities)

    def get_capability(self, name: str) -> CatalogCapability | None:
        for capability in self.capabilities:
            if capability.name == name:
                return capability
        return None

    def capability_operation_names(
        self,
        capability_name: str,
    ) -> tuple[str, ...]:
        capability = self.get_capability(capability_name)
        if capability is None:
            return ()
        return capability.operation_names()

    def has_operation(
        self,
        capability_name: str,
        operation_name: str,
    ) -> bool:
        capability = self.get_capability(capability_name)
        if capability is None:
            return False
        return capability.has_operation(operation_name)

    def get_operation(
        self,
        capability_name: str,
        operation_name: str,
    ) -> CatalogOperation | None:
        capability = self.get_capability(capability_name)
        if capability is None:
            return None
        return capability.get_operation(operation_name)

    def get_capability_telemetry(
        self,
        capability_name: str,
    ) -> CapabilityTelemetry | None:
        capability = self.get_capability(capability_name)
        if capability is None:
            return None
        return capability.telemetry

    def telemetry_span_names(
        self,
        capability_name: str,
    ) -> tuple[str, ...]:
        telemetry = self.get_capability_telemetry(capability_name)
        if telemetry is None:
            return ()
        return tuple(span.name for span in telemetry.spans)

    def telemetry_metric_names(
        self,
        capability_name: str,
    ) -> tuple[str, ...]:
        telemetry = self.get_capability_telemetry(capability_name)
        if telemetry is None:
            return ()
        return tuple(metric.name for metric in telemetry.metrics)

    def telemetry_event_types(
        self,
        capability_name: str,
    ) -> tuple[str, ...]:
        telemetry = self.get_capability_telemetry(capability_name)
        if telemetry is None:
            return ()
        return tuple(event.event_type for event in telemetry.events)

    def invalid_capability_metadata(
        self,
        matrix: CapabilityMatrix,
    ) -> tuple[str, ...]:
        self._ensure_concrete("capability metadata validation")
        invalid_capabilities: list[str] = []

        for capability in matrix.capabilities:
            catalog_capability = self.get_capability(capability.name)
            if catalog_capability is None:
                continue

            if not catalog_capability.validate_metadata(capability):
                invalid_capabilities.append(capability.name)

        return tuple(invalid_capabilities)

    def validate_capability_descriptors(
        self,
        descriptors: Iterable[CapabilityDescriptor],
    ) -> DescriptorValidationResult:
        self._ensure_concrete("descriptor validation")
        unknown_capabilities: list[str] = []
        unknown_operations: list[UnknownCapabilityOperations] = []
        invalid_metadata: list[str] = []

        descriptors = tuple(descriptors)
        diagnostics = list(
            duplicate_issues(
                (descriptor.name for descriptor in descriptors),
                path="/capabilities",
                code="duplicate_capability",
            )
        )

        for index, descriptor in enumerate(descriptors):
            path = f"/capabilities/{index}"
            diagnostics.extend(
                duplicate_issues(
                    descriptor.operation_names(),
                    path=f"{path}/operations",
                    code="duplicate_operation",
                )
            )
            diagnostics.extend(
                duplicate_issues(
                    descriptor.attribute_names(),
                    path=f"{path}/attributes",
                    code="duplicate_attribute",
                )
            )
            # Las construcciones Python también respetan el enum del contrato.
            if descriptor.level not in ("supported", "accepted_noop", "unsupported"):
                diagnostics.append(
                    ValidationIssue(
                        code="invalid_support",
                        path=f"{path}/level",
                        message="Unknown capability support level",
                        observed=str(descriptor.level),
                    )
                )
            catalog_capability = self.get_capability(descriptor.name)
            if catalog_capability is None:
                unknown_capabilities.append(descriptor.name)
                continue

            descriptor_unknown_operations = tuple(
                operation_name
                for operation_name in descriptor.operation_names()
                if not catalog_capability.has_operation(operation_name)
            )
            if descriptor_unknown_operations:
                unknown_operations.append(
                    UnknownCapabilityOperations(
                        capability_name=descriptor.name,
                        operation_names=descriptor_unknown_operations,
                    ),
                )

            for offset, binding in enumerate(descriptor.operations):
                operation = catalog_capability.get_operation(binding.operation_name)
                # Un resultado omitido es desconocido; uno contradictorio es inválido.
                if (
                    operation is not None
                    and binding.result_type is not None
                    and operation.result_type is not None
                    and (operation.result_type != binding.result_type)
                ):
                    diagnostics.append(
                        ValidationIssue(
                            code="conflicting_operation_result",
                            path=f"{path}/operations/{offset}/result_type",
                            message=(
                                f"Operation {binding.operation_name!r} "
                                "has a conflicting result type"
                            ),
                            expected=operation.result_type,
                            observed=binding.result_type,
                        )
                    )
            metadata_validation = catalog_capability.validate_metadata_detailed(
                descriptor.as_capability(), path=f"{path}/metadata"
            )
            diagnostics.extend(metadata_validation.issues)
            if not metadata_validation.is_valid():
                invalid_metadata.append(descriptor.name)

        return DescriptorValidationResult(
            unknown_capabilities=tuple(unknown_capabilities),
            unknown_operations=tuple(unknown_operations),
            invalid_metadata=tuple(invalid_metadata),
            diagnostics=tuple(diagnostics),
        )

    def validate_component_snapshot(
        self,
        snapshot: ComponentCapabilitySnapshot,
    ) -> DescriptorValidationResult:
        self._ensure_concrete("component snapshot validation")
        validation = self.validate_capability_descriptors(snapshot.capabilities)

        if (
            snapshot.identity is not None
            and snapshot.identity.interface != self.interface
        ):
            return DescriptorValidationResult(
                unknown_capabilities=validation.unknown_capabilities,
                unknown_operations=validation.unknown_operations,
                invalid_metadata=validation.invalid_metadata,
                interface_mismatch=snapshot.identity.interface,
                expected_interface=self.interface,
                diagnostics=validation.diagnostics,
            )

        return validation

    def get_tier(self, name: CatalogTierName) -> ConformanceTier | None:
        for tier in self.tiers:
            if tier.name == name:
                return tier
        return None

    def validate_component_snapshot_against_profile(
        self,
        snapshot: ComponentCapabilitySnapshot,
        profile: CapabilityProfile,
    ) -> CapabilityProfileValidationResult:
        self._ensure_concrete("profile validation")
        if (
            snapshot.identity is not None
            and snapshot.identity.interface != self.interface
        ):
            return CapabilityProfileValidationResult(
                interface_mismatch=snapshot.identity.interface,
                expected_interface=self.interface,
            )

        if profile.interface != self.interface:
            return CapabilityProfileValidationResult(
                interface_mismatch=profile.interface,
                expected_interface=self.interface,
            )

        unknown_profile_capabilities: list[str] = []
        missing_capabilities: list[str] = []
        missing_operations: list[UnknownCapabilityOperations] = []
        missing_metadata_keys: list[str] = []
        invalid_metadata: list[str] = []

        # Validamos identidades y bindings antes de construir el índice por nombre.
        descriptor_validation = self.validate_capability_descriptors(
            snapshot.capabilities
        )
        profile_validation = self.validate_profile_definition(profile)
        diagnostics = list(
            tuple(
                issue
                for issue in descriptor_validation.diagnostics
                if issue.code != "invalid_metadata"
            )
            + profile_validation.diagnostics
        )

        descriptors_by_name = {
            descriptor.name: descriptor
            for descriptor in snapshot.capabilities
            if isinstance(descriptor.name, str)
        }
        descriptor_paths = {
            descriptor.name: f"/capabilities/{index}/metadata"
            for index, descriptor in enumerate(snapshot.capabilities)
            if isinstance(descriptor.name, str)
        }

        for requirement in profile.requirements:
            catalog_capability = self.get_capability(requirement.capability_name)
            if catalog_capability is None:
                unknown_profile_capabilities.append(requirement.capability_name)
                continue

            descriptor = descriptors_by_name.get(requirement.capability_name)
            if descriptor is None or descriptor.level == "unsupported":
                missing_capabilities.append(requirement.capability_name)
                continue

            metadata_validation = catalog_capability.validate_metadata_detailed(
                descriptor.as_capability(),
                path=descriptor_paths[requirement.capability_name],
            )
            diagnostics.extend(metadata_validation.issues)
            if not metadata_validation.is_valid():
                invalid_metadata.append(requirement.capability_name)

            missing_requirement_operations = tuple(
                operation_name
                for operation_name in requirement.required_operations
                if operation_name not in descriptor.operation_names()
            )
            if missing_requirement_operations:
                missing_operations.append(
                    UnknownCapabilityOperations(
                        capability_name=requirement.capability_name,
                        operation_names=missing_requirement_operations,
                    )
                )

            descriptor_metadata = _metadata_key_set(descriptor.metadata)
            for metadata_key in requirement.required_metadata_keys:
                if metadata_key not in descriptor_metadata:
                    missing_metadata_keys.append(
                        f"{requirement.capability_name}.{metadata_key}"
                    )

        return CapabilityProfileValidationResult(
            unknown_profile_capabilities=tuple(unknown_profile_capabilities),
            missing_capabilities=tuple(missing_capabilities),
            missing_operations=tuple(missing_operations),
            missing_metadata_keys=tuple(missing_metadata_keys),
            invalid_metadata=tuple(invalid_metadata),
            diagnostics=tuple(diagnostics),
        )

    def validate_profile_definition(
        self,
        profile: CapabilityProfile,
    ) -> CapabilityProfileDefinitionValidationResult:
        self._ensure_concrete("profile definition validation")
        if profile.interface != self.interface:
            return CapabilityProfileDefinitionValidationResult(
                interface_mismatch=profile.interface,
                expected_interface=self.interface,
            )

        unknown_capabilities: list[str] = []
        unknown_operations: list[UnknownCapabilityOperations] = []
        unknown_metadata_keys: list[str] = []

        diagnostics = list(
            duplicate_issues(
                (requirement.capability_name for requirement in profile.requirements),
                path="/requirements",
                code="duplicate_requirement",
            )
        )

        for index, requirement in enumerate(profile.requirements):
            diagnostics.extend(
                duplicate_issues(
                    requirement.required_operations,
                    path=f"/requirements/{index}/required_operations",
                    code="duplicate_operation",
                )
            )
            diagnostics.extend(
                duplicate_issues(
                    requirement.required_metadata_keys,
                    path=f"/requirements/{index}/required_metadata_keys",
                    code="duplicate_metadata_key",
                )
            )
            catalog_capability = self.get_capability(requirement.capability_name)
            if catalog_capability is None:
                unknown_capabilities.append(requirement.capability_name)
                continue

            invalid_requirement_operations = tuple(
                operation_name
                for operation_name in requirement.required_operations
                if not catalog_capability.has_operation(operation_name)
            )
            if invalid_requirement_operations:
                unknown_operations.append(
                    UnknownCapabilityOperations(
                        capability_name=requirement.capability_name,
                        operation_names=invalid_requirement_operations,
                    )
                )

            known_metadata_keys = frozenset(catalog_capability.metadata_keys())
            for metadata_key in requirement.required_metadata_keys:
                if metadata_key not in known_metadata_keys:
                    unknown_metadata_keys.append(
                        f"{requirement.capability_name}.{metadata_key}"
                    )

        return CapabilityProfileDefinitionValidationResult(
            unknown_capabilities=tuple(unknown_capabilities),
            unknown_operations=tuple(unknown_operations),
            unknown_metadata_keys=tuple(unknown_metadata_keys),
            diagnostics=tuple(diagnostics),
        )

    def is_component_snapshot_profile_compliant(
        self,
        snapshot: ComponentCapabilitySnapshot,
        profile: CapabilityProfile,
    ) -> bool:
        return self.validate_component_snapshot_against_profile(
            snapshot,
            profile,
        ).is_valid()

    def validate_telemetry_snapshot(
        self,
        snapshot: TelemetrySnapshot,
        capability_names: Iterable[str],
        *,
        reject_unknown_signals: bool = False,
    ) -> TelemetryValidationResult:
        self._ensure_concrete("telemetry validation")
        offered_capabilities = tuple(capability_names)
        unknown_capabilities = self.validate_capability_names(offered_capabilities)
        telemetry_sets = tuple(
            telemetry
            for capability_name in offered_capabilities
            if capability_name not in unknown_capabilities
            for telemetry in (self.get_capability_telemetry(capability_name),)
            if telemetry is not None
        )
        span_specs = _merge_span_specs(telemetry_sets)
        metric_specs = _merge_metric_specs(telemetry_sets)
        event_specs = _merge_event_specs(telemetry_sets)

        unknown_spans: list[str] = []
        missing_span_attributes: list[str] = []
        for span in snapshot.spans:
            span_spec = span_specs.get(span.name)
            if span_spec is None:
                if reject_unknown_signals:
                    unknown_spans.append(span.name)
                continue
            for field in span_spec.required_attributes:
                if field.name not in span.attributes:
                    missing_span_attributes.append(f"{span.name}.{field.name}")

        unknown_metrics: list[str] = []
        missing_metric_labels: list[str] = []
        invalid_metric_units: list[str] = []
        for metric in snapshot.metrics:
            metric_spec = metric_specs.get(metric.name)
            if metric_spec is None:
                if reject_unknown_signals:
                    unknown_metrics.append(metric.name)
                continue
            for field in metric_spec.required_labels:
                if field.name not in metric.labels:
                    missing_metric_labels.append(f"{metric.name}.{field.name}")
            if metric_spec.unit is not None and metric.unit != metric_spec.unit:
                invalid_metric_units.append(
                    f"{metric.name}: expected {metric_spec.unit!r}, got {metric.unit!r}"
                )

        unknown_events: list[str] = []
        missing_event_payload_keys: list[str] = []
        invalid_event_severities: list[str] = []
        for event in snapshot.events:
            event_spec = event_specs.get(event.event_type)
            if event_spec is None:
                if reject_unknown_signals:
                    unknown_events.append(event.event_type)
                continue
            for field in event_spec.required_payload_keys:
                if field.name not in event.payload:
                    missing_event_payload_keys.append(
                        f"{event.event_type}.{field.name}"
                    )
            if (
                event_spec.severity is not None
                and event.severity != event_spec.severity
            ):
                invalid_event_severities.append(
                    f"{event.event_type}: expected {event_spec.severity!r}, "
                    f"got {event.severity!r}"
                )

        return TelemetryValidationResult(
            unknown_capabilities=unknown_capabilities,
            unknown_spans=tuple(unknown_spans),
            unknown_metrics=tuple(unknown_metrics),
            unknown_events=tuple(unknown_events),
            missing_span_attributes=tuple(missing_span_attributes),
            missing_metric_labels=tuple(missing_metric_labels),
            missing_event_payload_keys=tuple(missing_event_payload_keys),
            invalid_metric_units=tuple(invalid_metric_units),
            invalid_event_severities=tuple(invalid_event_severities),
        )

    def is_telemetry_snapshot_compliant(
        self,
        snapshot: TelemetrySnapshot,
        capability_names: Iterable[str],
        *,
        reject_unknown_signals: bool = False,
    ) -> bool:
        return self.validate_telemetry_snapshot(
            snapshot,
            capability_names,
            reject_unknown_signals=reject_unknown_signals,
        ).is_valid()

    def validate_capability_set(
        self,
        capability_names: Iterable[str],
        required_tier: CatalogTierName | None = None,
    ) -> CapabilityMatrixValidationResult:
        self._ensure_concrete("capability set validation")
        offered = tuple(capability_names)
        unknown_capabilities = self.validate_capability_names(offered)

        missing_tier_capabilities: tuple[str, ...] = ()
        unknown_required_tier: CatalogTierName | None = None

        if required_tier is not None:
            tier = self.get_tier(required_tier)
            if tier is None:
                unknown_required_tier = required_tier
            else:
                offered_set = frozenset(offered)
                missing_tier_capabilities = tuple(
                    capability_name
                    for capability_name in tier.required_capabilities
                    if capability_name not in offered_set
                )

        return CapabilityMatrixValidationResult(
            unknown_capabilities=unknown_capabilities,
            required_tier=required_tier,
            missing_tier_capabilities=missing_tier_capabilities,
            unknown_required_tier=unknown_required_tier,
            diagnostics=duplicate_issues(
                offered, path="/capabilities", code="duplicate_capability"
            ),
        )

    def validate_capability_matrix(
        self,
        matrix: CapabilityMatrix,
        required_tier: CatalogTierName | None = None,
        *,
        validate_metadata: bool = True,
    ) -> CapabilityMatrixValidationResult:
        base_validation = self.validate_capability_set(
            tuple(capability.name for capability in matrix.capabilities),
            required_tier=required_tier,
        )
        invalid_metadata: list[str] = []
        diagnostics = list(base_validation.diagnostics)
        # La exclusión explícita de metadata no desactiva las demás invariantes.
        if validate_metadata:
            for index, capability in enumerate(matrix.capabilities):
                definition = self.get_capability(capability.name)
                if definition is None:
                    continue
                result = definition.validate_metadata_detailed(
                    capability, path=f"/capabilities/{index}/metadata"
                )
                diagnostics.extend(result.issues)
                if not result.is_valid():
                    invalid_metadata.append(capability.name)

        return CapabilityMatrixValidationResult(
            unknown_capabilities=base_validation.unknown_capabilities,
            invalid_metadata=tuple(invalid_metadata),
            required_tier=base_validation.required_tier,
            missing_tier_capabilities=base_validation.missing_tier_capabilities,
            unknown_required_tier=base_validation.unknown_required_tier,
            diagnostics=tuple(diagnostics),
        )

    def validate_capability_names(
        self,
        capability_names: Iterable[str],
    ) -> tuple[str, ...]:
        self._ensure_concrete("capability name validation")
        known_capabilities = frozenset(self.capability_names())
        return tuple(
            name for name in capability_names if name not in known_capabilities
        )

    def satisfied_tiers(
        self,
        capability_names: Iterable[str],
    ) -> tuple[CatalogTierName, ...]:
        self._ensure_concrete("tier satisfaction evaluation")
        offered = tuple(capability_names)
        return tuple(tier.name for tier in self.tiers if tier.is_satisfied_by(offered))

    def is_matrix_compliant(
        self,
        capability_names: Iterable[str],
        required_tier: CatalogTierName | None = None,
    ) -> bool:
        return self.validate_capability_set(
            capability_names,
            required_tier=required_tier,
        ).is_valid()

    def is_capability_matrix_compliant(
        self,
        matrix: CapabilityMatrix,
        required_tier: CatalogTierName | None = None,
        *,
        validate_metadata: bool = True,
    ) -> bool:
        return self.validate_capability_matrix(
            matrix,
            required_tier=required_tier,
            validate_metadata=validate_metadata,
        ).is_valid()

    def is_component_snapshot_compliant(
        self,
        snapshot: ComponentCapabilitySnapshot,
        required_tier: CatalogTierName | None = None,
        *,
        validate_metadata: bool = True,
    ) -> bool:
        offered = offered_capability_names(snapshot.capabilities)

        if not self.is_matrix_compliant(
            offered,
            required_tier=required_tier,
        ):
            return False

        validation = self.validate_component_snapshot(snapshot)
        if (
            validation.unknown_capabilities
            or validation.unknown_operations
            or validation.interface_mismatch is not None
            or any(issue.code != "invalid_metadata" for issue in validation.diagnostics)
        ):
            return False

        if validate_metadata and validation.invalid_metadata:
            return False

        return True


class CatalogRegistry:
    def __init__(self, catalogs: Iterable[CapabilityCatalog] = ()) -> None:
        self._catalogs: dict[str, CapabilityCatalog] = {}
        self._lock = RLock()
        for catalog in catalogs:
            self.register(catalog)

    def register(
        self,
        catalog: CapabilityCatalog,
        *,
        replace: bool = False,
    ) -> CapabilityCatalog:
        with self._lock:
            validation = catalog.validate_definition()
            if not validation.is_valid():
                raise ContractValidationError(validation.issues)
            existing = self._catalogs.get(catalog.interface)
            if existing is not None:
                if existing == catalog:
                    return existing

                if not replace:
                    msg = f"Catalog interface already registered: {catalog.interface!r}"
                    raise ValueError(msg)

            self._validate_catalog_telemetry(catalog)
            self._validate_catalog_relations(catalog)
            candidate_catalogs = dict(self._catalogs)
            candidate_catalogs[catalog.interface] = catalog
            # Revisamos también los consumidores de una definición reemplazada.
            for candidate in candidate_catalogs.values():
                closure: dict[str, CapabilityCatalog] = {}
                pending = [candidate.interface]
                while pending:
                    name = pending.pop()
                    if name in closure:
                        continue
                    member = candidate_catalogs[name]
                    closure[name] = member
                    pending.extend(member.satisfies_interfaces)
                members = tuple(closure.values())
                # Incluimos conflictos transitivos y ramas de una composición.
                for index, member in enumerate(members):
                    for other in members[index + 1 :]:
                        issues = catalog_relation_issues(member, other)
                        if issues:
                            raise ContractValidationError(issues)
                self._validate_catalog_telemetry(
                    CapabilityCatalog(
                        interface=candidate.interface,
                        capabilities=tuple(
                            capability
                            for member in members
                            for capability in member.capabilities
                        ),
                    )
                )
            self._catalogs[catalog.interface] = catalog
            return catalog

    def get(self, interface: str) -> CapabilityCatalog | None:
        with self._lock:
            return self._catalogs.get(interface)

    def interfaces(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._catalogs))

    def satisfies_interface(
        self,
        offered_interface: str,
        required_interface: str,
    ) -> bool:
        with self._lock:
            return _catalog_satisfies_interface(
                offered_interface=offered_interface,
                required_interface=required_interface,
                catalogs=dict(self._catalogs),
            )

    def _validate_catalog_relations(
        self,
        catalog: CapabilityCatalog,
    ) -> None:
        candidate_catalogs = dict(self._catalogs)
        candidate_catalogs[catalog.interface] = catalog

        for satisfied_interface in catalog.satisfies_interfaces:
            if satisfied_interface == catalog.interface:
                msg = f"Catalog interface cannot satisfy itself: {catalog.interface!r}"
                raise ValueError(msg)

            if satisfied_interface not in candidate_catalogs:
                msg = (
                    "Catalog references unknown satisfied interface: "
                    f"{satisfied_interface!r}"
                )
                raise ValueError(msg)

            if _catalog_satisfies_interface(
                offered_interface=satisfied_interface,
                required_interface=catalog.interface,
                catalogs=candidate_catalogs,
            ):
                msg = (
                    "Catalog interface hierarchy cannot contain cycles: "
                    f"{catalog.interface!r} -> {satisfied_interface!r}"
                )
                raise ValueError(msg)

    def _validate_catalog_telemetry(
        self,
        catalog: CapabilityCatalog,
    ) -> None:
        span_specs: dict[str, tuple[str, frozenset[str]]] = {}
        metric_specs: dict[str, tuple[str, str | None, frozenset[str]]] = {}
        event_specs: dict[
            str, tuple[str, TelemetrySeverity | None, frozenset[str]]
        ] = {}

        for capability in catalog.capabilities:
            if capability.telemetry is None:
                continue

            for span in capability.telemetry.spans:
                field_names = frozenset(
                    field.name for field in span.required_attributes
                )
                existing_span = span_specs.get(span.name)
                if existing_span is None:
                    span_specs[span.name] = (capability.name, field_names)
                    continue
                if existing_span[1] != field_names:
                    msg = (
                        "Conflicting telemetry span definition for "
                        f"{span.name!r} in catalog {catalog.interface!r}: "
                        f"{existing_span[0]!r} vs {capability.name!r}"
                    )
                    raise ValueError(msg)

            for metric in capability.telemetry.metrics:
                label_names = frozenset(field.name for field in metric.required_labels)
                existing_metric = metric_specs.get(metric.name)
                if existing_metric is None:
                    metric_specs[metric.name] = (
                        capability.name,
                        metric.unit,
                        label_names,
                    )
                    continue
                if (
                    existing_metric[1] != metric.unit
                    or existing_metric[2] != label_names
                ):
                    msg = (
                        "Conflicting telemetry metric definition for "
                        f"{metric.name!r} in catalog {catalog.interface!r}: "
                        f"{existing_metric[0]!r} vs {capability.name!r}"
                    )
                    raise ValueError(msg)

            for event in capability.telemetry.events:
                payload_keys = frozenset(
                    field.name for field in event.required_payload_keys
                )
                existing_event = event_specs.get(event.event_type)
                if existing_event is None:
                    event_specs[event.event_type] = (
                        capability.name,
                        event.severity,
                        payload_keys,
                    )
                    continue
                if (
                    existing_event[1] != event.severity
                    or existing_event[2] != payload_keys
                ):
                    msg = (
                        "Conflicting telemetry event definition for "
                        f"{event.event_type!r} in catalog {catalog.interface!r}: "
                        f"{existing_event[0]!r} vs {capability.name!r}"
                    )
                    raise ValueError(msg)


DEFAULT_CATALOG_REGISTRY = CatalogRegistry()


def register_catalog(
    catalog: CapabilityCatalog,
    *,
    replace: bool = False,
) -> CapabilityCatalog:
    return DEFAULT_CATALOG_REGISTRY.register(catalog, replace=replace)


def get_catalog(interface: str) -> CapabilityCatalog | None:
    return DEFAULT_CATALOG_REGISTRY.get(interface)


def _catalog_satisfies_interface(
    *,
    offered_interface: str,
    required_interface: str,
    catalogs: dict[str, CapabilityCatalog],
    visited: set[str] | None = None,
) -> bool:
    if offered_interface == required_interface:
        return True

    catalog = catalogs.get(offered_interface)
    if catalog is None:
        return False

    if visited is None:
        visited = set()
    if offered_interface in visited:
        return False
    visited.add(offered_interface)

    return any(
        _catalog_satisfies_interface(
            offered_interface=satisfied_interface,
            required_interface=required_interface,
            catalogs=catalogs,
            visited=visited,
        )
        for satisfied_interface in catalog.satisfies_interfaces
    )


def catalog_satisfies_interface(
    offered_interface: str,
    required_interface: str,
) -> bool:
    return DEFAULT_CATALOG_REGISTRY.satisfies_interface(
        offered_interface=offered_interface,
        required_interface=required_interface,
    )


def _merge_span_specs(
    telemetry_sets: tuple[CapabilityTelemetry, ...],
) -> dict[str, TelemetrySpanSpec]:
    merged: dict[str, TelemetrySpanSpec] = {}
    for telemetry in telemetry_sets:
        for span in telemetry.spans:
            current = merged.get(span.name)
            if current is None:
                merged[span.name] = span
                continue
            merged[span.name] = TelemetrySpanSpec(
                name=span.name,
                required_attributes=_merge_field_requirements(
                    current.required_attributes,
                    span.required_attributes,
                ),
                description=current.description or span.description,
            )
    return merged


def _merge_metric_specs(
    telemetry_sets: tuple[CapabilityTelemetry, ...],
) -> dict[str, TelemetryMetricSpec]:
    merged: dict[str, TelemetryMetricSpec] = {}
    for telemetry in telemetry_sets:
        for metric in telemetry.metrics:
            current = merged.get(metric.name)
            if current is None:
                merged[metric.name] = metric
                continue
            merged[metric.name] = TelemetryMetricSpec(
                name=metric.name,
                unit=current.unit or metric.unit,
                required_labels=_merge_field_requirements(
                    current.required_labels,
                    metric.required_labels,
                ),
                description=current.description or metric.description,
            )
    return merged


def _merge_event_specs(
    telemetry_sets: tuple[CapabilityTelemetry, ...],
) -> dict[str, TelemetryEventSpec]:
    merged: dict[str, TelemetryEventSpec] = {}
    for telemetry in telemetry_sets:
        for event in telemetry.events:
            current = merged.get(event.event_type)
            if current is None:
                merged[event.event_type] = event
                continue
            merged[event.event_type] = TelemetryEventSpec(
                event_type=event.event_type,
                severity=current.severity or event.severity,
                required_payload_keys=_merge_field_requirements(
                    current.required_payload_keys,
                    event.required_payload_keys,
                ),
                description=current.description or event.description,
            )
    return merged


def _merge_field_requirements(
    left: tuple[TelemetryFieldRequirement, ...],
    right: tuple[TelemetryFieldRequirement, ...],
) -> tuple[TelemetryFieldRequirement, ...]:
    merged: dict[str, TelemetryFieldRequirement] = {field.name: field for field in left}
    for field in right:
        existing = merged.get(field.name)
        if existing is None:
            merged[field.name] = field
            continue
        if existing.description is None and field.description is not None:
            merged[field.name] = field
    return tuple(merged[name] for name in sorted(merged))


def _metadata_key_set(metadata: object) -> frozenset[str]:
    if isinstance(metadata, Mapping):
        return frozenset(str(key) for key in metadata)
    struct_fields = getattr(type(metadata), "__struct_fields__", None)
    if struct_fields is not None:
        return frozenset(str(field_name) for field_name in struct_fields)
    return frozenset()
