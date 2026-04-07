from pytest import raises

from cxp import (
    CapabilityMatrix,
    CapabilityCatalog,
    CatalogRegistry,
    ComponentIdentity,
    EXECUTION_ENGINE_FAMILY_CATALOG,
    EXECUTION_ENGINE_FAMILY_INTERFACE,
    HandshakeRequest,
    PLAN_RUN_EXECUTION_CATALOG,
    PLAN_RUN_EXECUTION_INTERFACE,
    EXECUTION_ENGINE_CATALOG,
    EXECUTION_ENGINE_INTERFACE,
    catalog_satisfies_interface,
    get_catalog,
    negotiate_capabilities,
)
from cxp.catalogs.interfaces.execution.plan_run import PLAN_RUN_OP_CANCEL, PLAN_RUN_OP_STATUS


def test_execution_family_and_plan_run_catalogs_are_registered() -> None:
    assert get_catalog(EXECUTION_ENGINE_FAMILY_INTERFACE) is EXECUTION_ENGINE_FAMILY_CATALOG
    assert get_catalog(PLAN_RUN_EXECUTION_INTERFACE) is PLAN_RUN_EXECUTION_CATALOG
    assert EXECUTION_ENGINE_CATALOG is PLAN_RUN_EXECUTION_CATALOG
    assert EXECUTION_ENGINE_INTERFACE == PLAN_RUN_EXECUTION_INTERFACE


def test_execution_family_catalog_is_abstract() -> None:
    with raises(ValueError, match="Abstract catalog"):
        EXECUTION_ENGINE_FAMILY_CATALOG.validate_capability_matrix(CapabilityMatrix())


def test_execution_catalog_hierarchy_reports_plan_run_compatibility() -> None:
    assert catalog_satisfies_interface("execution/plan-run", "execution/engine")
    assert catalog_satisfies_interface("execution/engine", "execution/plan-run") is False


def test_handshake_accepts_plan_run_for_execution_family() -> None:
    request = HandshakeRequest(
        client_identity=ComponentIdentity(
            interface="execution/engine",
            provider="cosecha",
            version="1.0.0",
        ),
        required_capabilities=(),
    )
    provider_identity = ComponentIdentity(
        interface="execution/plan-run",
        provider="gherkin",
        version="1.0.0",
    )

    response = negotiate_capabilities(
        request,
        provider_identity,
        CapabilityMatrix(),
    )

    assert response.status == "accepted"


def test_handshake_rejects_abstract_execution_family_for_plan_run_requirement() -> None:
    request = HandshakeRequest(
        client_identity=ComponentIdentity(
            interface="execution/plan-run",
            provider="cosecha",
            version="1.0.0",
        ),
        required_capabilities=(),
    )
    provider_identity = ComponentIdentity(
        interface="execution/engine",
        provider="generic-engine",
        version="1.0.0",
    )

    response = negotiate_capabilities(
        request,
        provider_identity,
        CapabilityMatrix(),
    )

    assert response.status == "rejected"


def test_execution_registry_rejects_unknown_or_cyclic_hierarchy() -> None:
    registry = CatalogRegistry(catalogs=(EXECUTION_ENGINE_FAMILY_CATALOG,))

    with raises(ValueError, match="unknown satisfied interface"):
        registry.register(
            CapabilityCatalog(
                interface="execution/custom-run",
                satisfies_interfaces=("execution/missing",),
            )
        )


def test_plan_run_status_capability_exposes_status_and_cancel_operations() -> None:
    assert (
        PLAN_RUN_EXECUTION_CATALOG.has_operation("execution_status", PLAN_RUN_OP_STATUS)
        is True
    )
    assert (
        PLAN_RUN_EXECUTION_CATALOG.has_operation("execution_status", PLAN_RUN_OP_CANCEL)
        is True
    )

    registry = CatalogRegistry(
        catalogs=(
            EXECUTION_ENGINE_FAMILY_CATALOG,
            PLAN_RUN_EXECUTION_CATALOG,
        )
    )

    with raises(ValueError, match="cannot contain cycles"):
        registry.register(
            CapabilityCatalog(
                interface=EXECUTION_ENGINE_FAMILY_INTERFACE,
                abstract=True,
                satisfies_interfaces=(PLAN_RUN_EXECUTION_INTERFACE,),
            ),
            replace=True,
        )
