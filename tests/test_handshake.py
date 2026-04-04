from cxp import (
    CURRENT_PROTOCOL_VERSION,
    Capability,
    CapabilityMatrix,
    ComponentIdentity,
    HandshakeRequest,
    negotiate_capabilities,
)


def test_successful_negotiation():
    client = ComponentIdentity(
        interface="database/mongodb",
        provider="cosecha",
        version="1.0.0",
    )
    provider = ComponentIdentity(
        interface="database/mongodb",
        provider="mongoeco2",
        version="3.0.0",
    )

    available = CapabilityMatrix(capabilities=(
        Capability(name="transactions"),
        Capability(name="read"),
    ))

    request = HandshakeRequest(client_identity=client, required_capabilities=("read",))

    response = negotiate_capabilities(request, provider, available)

    assert response.status == "accepted"
    assert response.provider_identity.provider == "mongoeco2"
    assert response.offered_capabilities.has_capability("transactions")
    assert response.protocol_version == CURRENT_PROTOCOL_VERSION

def test_rejected_negotiation():
    client = ComponentIdentity(
        interface="database/mongodb",
        provider="cosecha",
        version="1.0.0",
    )
    provider = ComponentIdentity(
        interface="database/mongodb",
        provider="mongoeco2",
        version="3.0.0",
    )

    available = CapabilityMatrix(capabilities=(Capability(name="read"),))

    request = HandshakeRequest(
        client_identity=client,
        required_capabilities=("transactions",),
    )

    response = negotiate_capabilities(request, provider, available)

    assert response.status == "rejected"
    assert "Missing required capabilities" in response.reason
    assert response.missing_required_capabilities == ("transactions",)
    assert response.missing_optional_capabilities == ()


def test_degraded_negotiation_when_optional_capabilities_are_missing():
    client = ComponentIdentity(
        interface="database/mongodb",
        provider="cosecha",
        version="1.0.0",
    )
    provider = ComponentIdentity(
        interface="database/mongodb",
        provider="mongoeco2",
        version="3.0.0",
    )

    available = CapabilityMatrix(capabilities=(
        Capability(name="read"),
    ))

    request = HandshakeRequest(
        client_identity=client,
        required_capabilities=("read",),
        optional_capabilities=("transactions",),
    )

    response = negotiate_capabilities(request, provider, available)

    assert response.status == "degraded"
    assert response.reason is not None
    assert "Missing optional capabilities" in response.reason
    assert response.offered_capabilities.has_capability("read")
    assert response.missing_required_capabilities == ()
    assert response.missing_optional_capabilities == ("transactions",)


def test_rejected_negotiation_when_protocol_version_is_not_supported():
    client = ComponentIdentity(
        interface="database/mongodb",
        provider="cosecha",
        version="1.0.0",
    )
    provider = ComponentIdentity(
        interface="database/mongodb",
        provider="mongoeco2",
        version="3.0.0",
    )

    available = CapabilityMatrix(capabilities=(
        Capability(name="read"),
    ))

    request = HandshakeRequest(
        client_identity=client,
        required_capabilities=("read",),
        protocol_version=2,
    )

    response = negotiate_capabilities(request, provider, available)

    assert response.status == "rejected"
    assert response.reason is not None
    assert "Unsupported protocol version" in response.reason
    assert response.protocol_version == CURRENT_PROTOCOL_VERSION
    assert response.missing_required_capabilities == ()
    assert response.missing_optional_capabilities == ()


def test_rejected_negotiation_when_interfaces_do_not_match():
    client = ComponentIdentity(
        interface="execution/engine",
        provider="cosecha",
        version="1.0.0",
    )
    provider = ComponentIdentity(
        interface="database/mongodb",
        provider="mongoeco2",
        version="3.0.0",
    )

    available = CapabilityMatrix(capabilities=(
        Capability(name="read"),
    ))

    request = HandshakeRequest(
        client_identity=client,
        required_capabilities=("read",),
    )

    response = negotiate_capabilities(request, provider, available)

    assert response.status == "rejected"
    assert response.reason is not None
    assert "Interface mismatch" in response.reason
    assert response.missing_required_capabilities == ()
    assert response.missing_optional_capabilities == ()


def test_rejected_negotiation_when_required_and_optional_overlap():
    client = ComponentIdentity(
        interface="database/mongodb",
        provider="cosecha",
        version="1.0.0",
    )
    provider = ComponentIdentity(
        interface="database/mongodb",
        provider="mongoeco2",
        version="3.0.0",
    )

    available = CapabilityMatrix(capabilities=(Capability(name="read"),))

    request = HandshakeRequest(
        client_identity=client,
        required_capabilities=("read",),
        optional_capabilities=("read",),
    )

    response = negotiate_capabilities(request, provider, available)

    assert response.status == "rejected"
    assert response.reason is not None
    assert "both required and optional" in response.reason
    assert response.missing_required_capabilities == ()
    assert response.missing_optional_capabilities == ()
