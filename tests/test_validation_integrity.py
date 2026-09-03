from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Annotated

import msgspec
import pytest

from cxp import (
    DEFAULT_CATALOG_REGISTRY,
    Capability,
    CapabilityAttribute,
    CapabilityCatalog,
    CapabilityDescriptor,
    CapabilityMatrix,
    CapabilityOperationBinding,
    CapabilityProfile,
    CapabilityRequirement,
    CatalogCapability,
    CatalogOperation,
    CatalogRegistry,
    ComponentCapabilitySnapshot,
    ComponentIdentity,
    ConformanceTier,
    ContractValidationError,
    register_catalog,
)


class Limits(msgspec.Struct, frozen=True):
    count: Annotated[int, msgspec.Meta(ge=1)]


def make_catalog(*, interface="tests/integrity", result_type="action.result"):
    return CapabilityCatalog(
        interface=interface,
        capabilities=(
            CatalogCapability(
                name="run",
                metadata_schema=Limits,
                operations=(CatalogOperation(name="run", result_type=result_type),),
            ),
        ),
    )


@pytest.mark.parametrize("value", [0, "invalid", False])
def test_struct_and_mapping_metadata_obey_identical_validation(value):
    definition = make_catalog().capabilities[0]
    results = [
        definition.validate_metadata_detailed(Capability("run", metadata))
        for metadata in ({"count": value}, Limits(count=value))
    ]
    assert all(not result.is_valid() for result in results)
    assert results[0].issues[0].code == results[1].issues[0].code
    assert results[0].issues[0].path == results[1].issues[0].path == "/metadata"
    assert results[0].issues[0].cause == results[1].issues[0].cause
    assert definition.validate_metadata(Capability("run", Limits(count=value))) is False


def test_valid_struct_is_still_valid_but_is_rechecked_after_nested_mutation():
    class Container(msgspec.Struct, frozen=True):
        values: list[int]

    definition = CatalogCapability("items", metadata_schema=Container)
    values = [1]
    capability = Capability("items", Container(values))
    assert definition.validate_metadata(capability)
    values.append("bad")
    result = definition.validate_metadata_detailed(capability)
    assert result.issues[0].cause.endswith("`$.values[1]`")


@pytest.mark.parametrize(
    ("catalog", "code"),
    [
        (
            CapabilityCatalog("test", (CatalogCapability("x"),) * 2),
            "duplicate_capability",
        ),
        (
            CapabilityCatalog(
                "test",
                (CatalogCapability("x", operations=(CatalogOperation("op"),) * 2),),
            ),
            "duplicate_operation",
        ),
        (
            CapabilityCatalog("test", tiers=(ConformanceTier("core", ()),) * 2),
            "duplicate_tier",
        ),
        (
            CapabilityCatalog("test", tiers=(ConformanceTier("core", ("absent",)),)),
            "unknown_tier_capability",
        ),
        (
            CapabilityCatalog(
                "test",
                (CatalogCapability("x"),),
                tiers=(ConformanceTier("core", ("x", "x")),),
            ),
            "duplicate_tier_capability",
        ),
        (
            CapabilityCatalog("test", satisfies_interfaces=("base", "base")),
            "duplicate_interface",
        ),
        (CapabilityCatalog("test", (CatalogCapability(""),)), "invalid_identifier"),
    ],
)
def test_invalid_catalog_definitions_are_rejected_before_registration(catalog, code):
    result = catalog.validate_definition()
    assert code in {issue.code for issue in result.issues}
    registry = CatalogRegistry()
    with pytest.raises(ContractValidationError) as caught:
        registry.register(catalog)
    assert code in {issue.code for issue in caught.value.issues}
    assert registry.interfaces() == ()


@pytest.mark.parametrize(
    "duration", [0, -1, float("inf"), float("nan"), True, "bad", 10**500]
)
def test_invalid_operation_timeout_is_rejected(duration):
    catalog = CapabilityCatalog(
        "test",
        (
            CatalogCapability(
                "x", operations=(CatalogOperation("op", timeout_seconds=duration),)
            ),
        ),
    )
    assert catalog.validate_definition().issues[0].code == "invalid_timeout"


def test_same_operation_name_in_different_capabilities_is_not_a_duplicate():
    CatalogRegistry(
        (
            CapabilityCatalog(
                "test",
                tuple(
                    CatalogCapability(name, operations=(CatalogOperation("op"),))
                    for name in ("read", "write")
                ),
            ),
        )
    )


@pytest.mark.parametrize("metadata", [{"count": 1}, {"count": 0}])
def test_duplicate_snapshot_and_matrix_cannot_be_hidden_by_projection(metadata):
    catalog = make_catalog()
    snapshot = ComponentCapabilitySnapshot(
        "provider", (CapabilityDescriptor("run", "supported", metadata=metadata),) * 2
    )
    result = catalog.validate_component_snapshot(snapshot)
    assert result.diagnostics[0].code == "duplicate_capability"
    assert not result.is_valid()
    assert not catalog.is_component_snapshot_compliant(
        snapshot, validate_metadata=False
    )
    matrix = CapabilityMatrix((Capability("run", metadata),) * 2)
    assert not catalog.validate_capability_matrix(
        matrix, validate_metadata=False
    ).is_valid()


def test_binding_and_attribute_diagnostics_survive_identity_mismatch():
    snapshot = ComponentCapabilitySnapshot(
        "provider",
        (
            CapabilityDescriptor(
                "run",
                "supported",
                metadata={"count": 1},
                attributes=(CapabilityAttribute("a", True),) * 2,
                operations=(CapabilityOperationBinding("run", "wrong.result"),) * 2,
            ),
        ),
        identity=ComponentIdentity("other", "provider", "1"),
    )
    result = make_catalog().validate_component_snapshot(snapshot)
    assert not result.is_valid()
    assert {issue.code for issue in result.diagnostics} == {
        "duplicate_attribute",
        "duplicate_operation",
        "conflicting_operation_result",
    }
    assert result.interface_mismatch == "other"


@pytest.mark.parametrize("result_type", [None, "action.result"])
def test_compatible_or_unreported_binding_result_is_valid(result_type):
    snapshot = ComponentCapabilitySnapshot(
        "provider",
        (
            CapabilityDescriptor(
                "run",
                "supported",
                metadata={"count": 1},
                operations=(CapabilityOperationBinding("run", result_type),),
            ),
        ),
    )
    assert make_catalog().validate_component_snapshot(snapshot).is_valid()


def test_profile_constructor_keeps_validation_and_rejects_duplicated_requirements():
    catalog = make_catalog(interface="tests/integrity-profile")
    register_catalog(catalog, replace=True)
    with pytest.raises(ValueError, match="Duplicate declaration"):
        CapabilityProfile("bad", catalog.interface, (CapabilityRequirement("run"),) * 2)
    profile = CapabilityProfile(
        "valid", catalog.interface, (CapabilityRequirement("run"),)
    )
    snapshot = ComponentCapabilitySnapshot(
        "provider",
        (CapabilityDescriptor("run", "accepted_noop", metadata={"count": 1}),),
    )
    assert catalog.validate_component_snapshot_against_profile(
        snapshot, profile
    ).is_valid()


def test_conflicting_family_result_is_rejected_atomically_even_on_replacement():
    parent = CapabilityCatalog(
        "base",
        (
            CatalogCapability(
                "run", operations=(CatalogOperation("run", result_type="first"),)
            ),
        ),
        abstract=True,
    )
    child = CapabilityCatalog(
        "child", parent.capabilities, satisfies_interfaces=("base",)
    )
    registry = CatalogRegistry((parent, child))
    replacement = CapabilityCatalog(
        "base",
        (
            CatalogCapability(
                "run", operations=(CatalogOperation("run", result_type="second"),)
            ),
        ),
        abstract=True,
    )
    with pytest.raises(ContractValidationError):
        registry.register(replacement, replace=True)
    assert registry.get("base") is parent
    assert registry.get("child") is child


def test_transitive_diamond_cannot_hide_conflicting_operations():
    left = CapabilityCatalog(
        "left",
        (
            CatalogCapability(
                "run", operations=(CatalogOperation("run", result_type="left"),)
            ),
        ),
        abstract=True,
    )
    right = CapabilityCatalog(
        "right",
        (
            CatalogCapability(
                "run", operations=(CatalogOperation("run", result_type="right"),)
            ),
        ),
        abstract=True,
    )
    registry = CatalogRegistry((left, right))
    registry.register(CapabilityCatalog("middle", satisfies_interfaces=("left",)))
    with pytest.raises(ContractValidationError):
        registry.register(
            CapabilityCatalog("combined", satisfies_interfaces=("middle", "right"))
        )
    assert registry.get("combined") is None


def test_every_bundled_catalog_obeys_definition_integrity():
    for interface in DEFAULT_CATALOG_REGISTRY.interfaces():
        result = DEFAULT_CATALOG_REGISTRY.get(interface).validate_definition()
        assert result.is_valid(), (interface, result.issues)


def test_legacy_31_exports_and_struct_fields_are_preserved():
    inventory = json.loads(
        (Path(__file__).parent / "fixtures/legacy-3.1-api.json").read_text()
    )
    for module_name, names in inventory["exports"].items():
        module = importlib.import_module(module_name)
        assert set(names) <= set(module.__all__), module_name
        assert all(hasattr(module, name) for name in names), module_name
    for qualified, fields in inventory["struct_fields"].items():
        module_name, class_name = qualified.split(":")
        struct = getattr(importlib.import_module(module_name), class_name)
        assert tuple(struct.__struct_fields__[: len(fields)]) == tuple(fields), (
            qualified
        )


def test_profile_retains_detailed_required_metadata_diagnostics():
    catalog = make_catalog(interface="tests/profile-metadata-details")
    register_catalog(catalog, replace=True)
    profile = CapabilityProfile(
        "valid", catalog.interface, (CapabilityRequirement("run"),)
    )
    snapshot = ComponentCapabilitySnapshot(
        "provider", (CapabilityDescriptor("run", "supported", metadata=Limits(0)),)
    )
    report = catalog.validate_component_snapshot_against_profile(snapshot, profile)
    assert report.invalid_metadata == ("run",)
    assert report.diagnostics[0].path == "/capabilities/0/metadata"
    assert report.diagnostics[0].cause


def test_invalid_unhashable_catalog_identity_is_a_diagnostic():
    catalog = CapabilityCatalog("test", (CatalogCapability([]),))
    assert catalog.validate_definition().issues[0].code == "invalid_identifier"


def test_definition_validation_is_cached_per_immutable_instance(monkeypatch):
    import cxp.catalogs.base as base

    original = base.catalog_definition_issues
    calls = []

    def counted(catalog):
        calls.append(id(catalog))
        return original(catalog)

    monkeypatch.setattr(base, "catalog_definition_issues", counted)
    catalog = make_catalog()
    wire = msgspec.json.encode(catalog, enc_hook=lambda value: value.__name__)
    for _ in range(5):
        assert catalog.validate_capability_matrix(CapabilityMatrix()).is_valid()
    assert calls == [id(catalog)]
    assert msgspec.json.encode(catalog, enc_hook=lambda value: value.__name__) == wire
    copy = msgspec.structs.replace(catalog, capabilities=catalog.capabilities * 2)
    assert copy.validate_definition().issues[0].code == "duplicate_capability"
    assert calls == [id(catalog), id(copy)]


def test_mutable_nested_catalog_definitions_never_use_a_stale_cache():
    operations = [CatalogOperation("op")]
    catalog = CapabilityCatalog(
        "test/mutable", (CatalogCapability("cap", operations=operations),)
    )
    assert catalog.validate_definition().is_valid()
    operations.append(CatalogOperation("op"))
    assert catalog.validate_definition().issues[0].code == "duplicate_operation"
    operations.pop()
    assert catalog.validate_definition().is_valid()


def test_external_catalog_subclasses_are_not_assumed_immutable():
    from cxp.catalogs.validation import definition_is_immutable

    class CustomCatalog(CapabilityCatalog):
        pass

    assert not definition_is_immutable(CustomCatalog("test/custom"))
