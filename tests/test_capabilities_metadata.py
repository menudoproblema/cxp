import msgspec

from cxp.capabilities import Capability


class MongoReadMetadata(msgspec.Struct, frozen=True):
    max_pool_size: int = 10
    supports_sessions: bool = True
    replica_set: str | None = None


def test_capability_supports_raw_dictionary_metadata():
    cap = Capability(
        name="read", metadata={"max_pool_size": 20, "supports_sessions": False}
    )

    assert cap.metadata["max_pool_size"] == 20
    assert cap.metadata["supports_sessions"] is False


def test_capability_supports_msgspec_struct_metadata():
    meta = MongoReadMetadata(max_pool_size=50, replica_set="rs0")
    cap = Capability(name="read", metadata=meta)

    # Verificamos acceso directo
    assert cap.metadata.max_pool_size == 50
    assert cap.metadata.replica_set == "rs0"
    assert cap.metadata.supports_sessions is True  # Valor por defecto del Struct


def test_capability_metadata_serialization_roundtrip():
    meta = MongoReadMetadata(max_pool_size=100)
    cap = Capability(name="test", metadata=meta)

    json_data = msgspec.json.encode(cap)
    decoded = msgspec.json.decode(json_data, type=Capability)

    assert isinstance(decoded.metadata, dict)
    assert decoded.metadata["max_pool_size"] == 100


def test_generic_metadata_decodes_without_catalog_validation():
    decoded = msgspec.json.decode(
        b'{"name": "test", "metadata": {"max_pool_size": "not-an-int"}}',
        type=Capability,
    )

    assert isinstance(decoded.metadata, dict)
    assert decoded.metadata["max_pool_size"] == "not-an-int"
