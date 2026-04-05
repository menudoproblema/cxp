from __future__ import annotations

from collections.abc import Iterable
from threading import RLock

import msgspec

from cxp.capabilities import Capability, CapabilityMatrix
from cxp.descriptors import (
    CapabilityDescriptor,
    ComponentCapabilitySnapshot,
    DescriptorValidationResult,
    UnknownCapabilityOperations,
    offered_capability_names,
)

type CatalogTierName = str
type CapabilityMetadataSchema = type[msgspec.Struct] | None


class CapabilityRequirement(msgspec.Struct, frozen=True):
    capability_name: str
    required_operations: tuple[str, ...] = ()
    required_metadata_keys: tuple[str, ...] = ()


class CapabilityProfileValidationResult(msgspec.Struct, frozen=True):
    unknown_profile_capabilities: tuple[str, ...] = ()
    missing_capabilities: tuple[str, ...] = ()
    missing_operations: tuple[UnknownCapabilityOperations, ...] = ()
    missing_metadata_keys: tuple[str, ...] = ()
    invalid_metadata: tuple[str, ...] = ()
    interface_mismatch: str | None = None
    expected_interface: str | None = None

    def is_valid(self) -> bool:
        return (
            not self.unknown_profile_capabilities
            and not self.missing_capabilities
            and not self.missing_operations
            and not self.missing_metadata_keys
            and not self.invalid_metadata
            and self.interface_mismatch is None
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

        return tuple(messages)


class CapabilityProfile(msgspec.Struct, frozen=True):
    name: str
    interface: str
    requirements: tuple[CapabilityRequirement, ...]
    description: str | None = None


class CapabilityMatrixValidationResult(msgspec.Struct, frozen=True):
    unknown_capabilities: tuple[str, ...] = ()
    invalid_metadata: tuple[str, ...] = ()
    required_tier: CatalogTierName | None = None
    missing_tier_capabilities: tuple[str, ...] = ()
    unknown_required_tier: CatalogTierName | None = None

    def is_valid(self) -> bool:
        return (
            not self.unknown_capabilities
            and not self.invalid_metadata
            and not self.missing_tier_capabilities
            and self.unknown_required_tier is None
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

        return tuple(messages)


class CatalogOperation(msgspec.Struct, frozen=True):
    name: str
    result_type: str | None = None
    description: str | None = None


class CatalogCapability(msgspec.Struct, frozen=True):
    name: str
    description: str | None = None
    operations: tuple[CatalogOperation, ...] = ()
    metadata_schema: CapabilityMetadataSchema = None

    def operation_names(self) -> tuple[str, ...]:
        return tuple(operation.name for operation in self.operations)

    def has_operation(self, name: str) -> bool:
        return any(operation.name == name for operation in self.operations)

    def get_operation(self, name: str) -> CatalogOperation | None:
        for operation in self.operations:
            if operation.name == name:
                return operation
        return None

    def validate_metadata(self, capability: Capability) -> bool:
        if self.metadata_schema is None:
            return True

        try:
            capability.get_metadata(self.metadata_schema)
        except (TypeError, ValueError, msgspec.ValidationError):
            return False

        return True


class ConformanceTier(msgspec.Struct, frozen=True):
    name: CatalogTierName
    required_capabilities: tuple[str, ...]
    description: str | None = None

    def is_satisfied_by(self, capability_names: Iterable[str]) -> bool:
        offered = frozenset(capability_names)
        return all(name in offered for name in self.required_capabilities)


class CapabilityCatalog(msgspec.Struct, frozen=True):
    interface: str
    capabilities: tuple[CatalogCapability, ...]
    tiers: tuple[ConformanceTier, ...] = ()
    description: str | None = None

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

    def invalid_capability_metadata(
        self,
        matrix: CapabilityMatrix,
    ) -> tuple[str, ...]:
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
        unknown_capabilities: list[str] = []
        unknown_operations: list[UnknownCapabilityOperations] = []
        invalid_metadata: list[str] = []

        for descriptor in descriptors:
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

            if not catalog_capability.validate_metadata(
                descriptor.as_capability(),
            ):
                invalid_metadata.append(descriptor.name)

        return DescriptorValidationResult(
            unknown_capabilities=tuple(unknown_capabilities),
            unknown_operations=tuple(unknown_operations),
            invalid_metadata=tuple(invalid_metadata),
        )

    def validate_component_snapshot(
        self,
        snapshot: ComponentCapabilitySnapshot,
    ) -> DescriptorValidationResult:
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
        if snapshot.identity is not None and snapshot.identity.interface != self.interface:
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

        descriptors_by_name = {
            descriptor.name: descriptor for descriptor in snapshot.capabilities
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

            if not catalog_capability.validate_metadata(descriptor.as_capability()):
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

            descriptor_metadata = descriptor.metadata
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

    def validate_capability_set(
        self,
        capability_names: Iterable[str],
        required_tier: CatalogTierName | None = None,
    ) -> CapabilityMatrixValidationResult:
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
        invalid_metadata = (
            self.invalid_capability_metadata(matrix) if validate_metadata else ()
        )

        return CapabilityMatrixValidationResult(
            unknown_capabilities=base_validation.unknown_capabilities,
            invalid_metadata=invalid_metadata,
            required_tier=base_validation.required_tier,
            missing_tier_capabilities=base_validation.missing_tier_capabilities,
            unknown_required_tier=base_validation.unknown_required_tier,
        )

    def validate_capability_names(
        self,
        capability_names: Iterable[str],
    ) -> tuple[str, ...]:
        known_capabilities = frozenset(self.capability_names())
        return tuple(
            name for name in capability_names if name not in known_capabilities
        )

    def satisfied_tiers(
        self,
        capability_names: Iterable[str],
    ) -> tuple[CatalogTierName, ...]:
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
            existing = self._catalogs.get(catalog.interface)
            if existing is not None:
                if existing == catalog:
                    return existing

                if not replace:
                    msg = f"Catalog interface already registered: {catalog.interface!r}"
                    raise ValueError(msg)

            self._catalogs[catalog.interface] = catalog
            return catalog

    def get(self, interface: str) -> CapabilityCatalog | None:
        with self._lock:
            return self._catalogs.get(interface)

    def interfaces(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._catalogs))


DEFAULT_CATALOG_REGISTRY = CatalogRegistry()


def register_catalog(
    catalog: CapabilityCatalog,
    *,
    replace: bool = False,
) -> CapabilityCatalog:
    return DEFAULT_CATALOG_REGISTRY.register(catalog, replace=replace)


def get_catalog(interface: str) -> CapabilityCatalog | None:
    return DEFAULT_CATALOG_REGISTRY.get(interface)
