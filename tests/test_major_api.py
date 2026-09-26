"""The removal major installs only exchange and neutral validation APIs."""

import importlib.util

import cxp
from cxp import ContractValidationError, ValidationIssue
from cxp.exchange import Document


def test_root_keeps_only_neutral_public_symbols() -> None:
    assert cxp.__version__
    assert ContractValidationError is not None
    assert ValidationIssue is not None
    assert Document is not None
    for name in (
        "CapabilityMatrix",
        "ComponentCapabilitySnapshot",
        "HandshakeRequest",
        "negotiate_capabilities",
        "DEFAULT_CATALOG_REGISTRY",
    ):
        assert not hasattr(cxp, name)


def test_legacy_component_modules_are_absent() -> None:
    for name in (
        "cxp.capabilities",
        "cxp.catalogs",
        "cxp.compliance",
        "cxp.contracts",
        "cxp.descriptors",
        "cxp.handshake",
        "cxp.integration",
        "cxp.telemetry",
        "cxp.types",
    ):
        assert importlib.util.find_spec(name) is None
