from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

import msgspec

from cxp.capabilities import Capability, CapabilityMatrix, CapabilityMetadata
from cxp.types import ComponentIdentity

type CapabilitySupportLevel = Literal[
    "supported",
    "accepted_noop",
    "unsupported",
]
type CapabilityStability = Literal["stable", "experimental"]
type CapabilityAttributeValue = str | bool | int | float | tuple[str, ...]


class CapabilityAttribute(msgspec.Struct, frozen=True):
    name: str
    value: CapabilityAttributeValue


class CapabilityOperationBinding(msgspec.Struct, frozen=True):
    operation_name: str
    result_type: str | None = None
    freshness: str | None = None


class CapabilityDescriptor(msgspec.Struct, frozen=True):
    name: str
    level: CapabilitySupportLevel
    summary: str = ""
    stability: CapabilityStability = "stable"
    attributes: tuple[CapabilityAttribute, ...] = ()
    operations: tuple[CapabilityOperationBinding, ...] = ()
    metadata: CapabilityMetadata = msgspec.field(default_factory=dict)
    delivery_mode: str | None = None
    granularity: str | None = None

    def attribute_names(self) -> tuple[str, ...]:
        return tuple(attribute.name for attribute in self.attributes)

    def operation_names(self) -> tuple[str, ...]:
        return tuple(operation.operation_name for operation in self.operations)

    def has_operation(self, name: str) -> bool:
        return any(operation.operation_name == name for operation in self.operations)

    def get_operation(self, name: str) -> CapabilityOperationBinding | None:
        for operation in self.operations:
            if operation.operation_name == name:
                return operation
        return None

    def is_offered(self) -> bool:
        return self.level != "unsupported"

    def is_negotiable(self) -> bool:
        return self.level == "supported"

    def as_capability(self) -> Capability:
        return Capability(name=self.name, metadata=self.metadata)


class ComponentCapabilitySnapshot(msgspec.Struct, frozen=True):
    component_name: str
    capabilities: tuple[CapabilityDescriptor, ...]
    component_kind: str | None = None
    identity: ComponentIdentity | None = None

    def capability_names(
        self,
        *,
        include_unsupported: bool = True,
    ) -> tuple[str, ...]:
        return tuple(
            capability.name
            for capability in self.capabilities
            if include_unsupported or capability.is_offered()
        )

    def get_capability(self, name: str) -> CapabilityDescriptor | None:
        for capability in self.capabilities:
            if capability.name == name:
                return capability
        return None

    def offered_capabilities(self) -> tuple[CapabilityDescriptor, ...]:
        return tuple(
            capability for capability in self.capabilities if capability.is_offered()
        )

    def as_negotiated_capability_matrix(self) -> CapabilityMatrix:
        return CapabilityMatrix(
            capabilities=tuple(
                capability.as_capability()
                for capability in self.capabilities
                if capability.is_negotiable()
            ),
        )

    def as_capability_matrix_with_noop(self) -> CapabilityMatrix:
        return CapabilityMatrix(
            capabilities=tuple(
                capability.as_capability()
                for capability in self.capabilities
                if capability.is_offered()
            ),
        )


class ComponentDependencyRule(msgspec.Struct, frozen=True):
    source_component: str
    target_component: str
    dependency_kind: str
    projection_policy: str
    summary: str = ""
    required_capabilities: tuple[str, ...] = ()
    required_operations: tuple[str, ...] = ()
    shared_context_required: bool = True


class UnknownCapabilityOperations(msgspec.Struct, frozen=True):
    capability_name: str
    operation_names: tuple[str, ...]


class DescriptorValidationResult(msgspec.Struct, frozen=True):
    unknown_capabilities: tuple[str, ...] = ()
    unknown_operations: tuple[UnknownCapabilityOperations, ...] = ()
    invalid_metadata: tuple[str, ...] = ()
    interface_mismatch: str | None = None
    expected_interface: str | None = None

    def is_valid(self) -> bool:
        return (
            not self.unknown_capabilities
            and not self.unknown_operations
            and not self.invalid_metadata
            and self.interface_mismatch is None
        )

    @property
    def interface_mismatch_message(self) -> str | None:
        if self.interface_mismatch is None or self.expected_interface is None:
            return None

        return (
            "Interface mismatch: expected "
            f"{self.expected_interface!r} but received "
            f"{self.interface_mismatch!r}"
        )

    def messages(self) -> tuple[str, ...]:
        messages: list[str] = []

        if self.unknown_capabilities:
            messages.append(
                "Unknown capabilities: " + ", ".join(self.unknown_capabilities),
            )

        for unknown_operations in self.unknown_operations:
            messages.append(
                "Unknown operations for capability "
                f"{unknown_operations.capability_name!r}: "
                + ", ".join(unknown_operations.operation_names),
            )

        if self.invalid_metadata:
            messages.append(
                "Invalid metadata for capabilities: "
                + ", ".join(self.invalid_metadata),
            )

        interface_mismatch_message = self.interface_mismatch_message
        if interface_mismatch_message is not None:
            messages.append(interface_mismatch_message)

        return tuple(messages)


def offered_capability_names(
    descriptors: Iterable[CapabilityDescriptor],
) -> tuple[str, ...]:
    return tuple(
        descriptor.name for descriptor in descriptors if descriptor.is_offered()
    )
