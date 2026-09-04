"""Contratos públicos del intercambio, sin proveedores ni registro global."""

import copy
import itertools
import json
from dataclasses import FrozenInstanceError
from decimal import localcontext

import pytest

from cxp.exchange import (
    CatalogStore,
    Document,
    EvaluationResult,
    ExchangeAgreement,
    InvalidDocumentError,
    Quantity,
    UnsupportedContractError,
    catalog_reference,
    document_schema,
    evaluate_requirements,
    evaluate_requirements_detailed,
    load_document,
    negotiate_exchange,
    normalize_decimal,
    quantity_from_input,
)


def doc(kind, payload, **extra):
    return Document(
        {"document_type": kind, "spec_version": 1, "payload": payload, **extra},
        expected_type=kind,
    )


@pytest.fixture
def catalog():
    return doc(
        "cxp.catalog",
        {
            "identity": {
                "namespace": "org.example",
                "name": "test",
                "version": "1.0.0",
            },
            "owner": "Example",
            "capabilities": [
                {
                    "name": "print",
                    "properties": {
                        "width": {"kind": "quantity", "dimension": "length"},
                        "quality": {"kind": "decimal"},
                        "count": {"kind": "integer"},
                        "duplex": {"kind": "boolean"},
                        "material": {
                            "kind": "string",
                            "nullable": True,
                            "null_meaning": "No material configured",
                        },
                        "colors": {"kind": "string_set"},
                    },
                    "operations": [{"name": "submit", "result_type": "example.result"}],
                },
                {"name": "cut", "properties": {}, "operations": []},
            ],
        },
    )


def snapshot(catalog, *, properties=None, support="supported", **updates):
    payload = {
        "provider_id": "adapter-1",
        "subject_id": "subject-1",
        "catalog": catalog_reference(catalog),
        "configuration_revision": "config-1",
        "observed_at": "2026-09-03T10:00:00Z",
        "source": {"kind": "declared", "reference": "declaration-1"},
        "capabilities": [
            {
                "name": "print",
                "support": support,
                "properties": properties
                if properties is not None
                else {
                    "width": {"value": "25.40", "unit": "mm"},
                    "quality": "0.30",
                    "count": 3,
                    "duplex": True,
                    "material": None,
                    "colors": ["white", "cmyk"],
                },
                "operations": [{"name": "submit", "result_type": "example.result"}],
            }
        ],
    }
    payload.update(updates)
    return doc("cxp.snapshot", payload)


def context(**updates):
    return doc(
        "cxp.context",
        {
            "subject_id": "subject-1",
            "configuration_revision": "config-1",
            **updates,
        },
    )


def requirements(catalog, node):
    return doc(
        "cxp.requirements", {"catalog": catalog_reference(catalog), "requirement": node}
    )


def leaf(operator="support", **fields):
    return {"id": "r1", "capability": "print", "operator": operator, **fields}


def evaluate(catalog, node, *, snap=None, ctx=None):
    return evaluate_requirements(
        snapshot(catalog) if snap is None else snap,
        requirements(catalog, node),
        context() if ctx is None else ctx,
        catalogs=CatalogStore([catalog]),
    )


@pytest.mark.parametrize(
    "text,normalized", [("-0.00", "0"), ("25.400", "25.4"), ("1", "1")]
)
def test_decimal_normalization(text, normalized):
    assert normalize_decimal(text) == normalized


@pytest.mark.parametrize(
    "value",
    [1, 1.1, True, None, "NaN", "Infinity", "1e2", "01", "+1", ".1", "1.", "1" * 129],
)
def test_decimal_rejects_noncontract_values(value):
    with pytest.raises(InvalidDocumentError):
        normalize_decimal(value)


def test_units_are_exact_and_independent_of_decimal_context():
    with localcontext() as ctx:
        ctx.prec = 1
        assert Quantity("72", "pt").compare(Quantity("1", "in")) == 0
        assert Quantity("1", "pt").exact_value.denominator == 360
        assert Quantity("1", "kg").compare(Quantity("1000", "g")) == 0
        assert Quantity("1000", "um").compare(Quantity("1", "mm")) == 0
    with pytest.raises(InvalidDocumentError, match="dimensions"):
        Quantity("1", "g").compare(Quantity("1", "mm"))
    with pytest.raises(InvalidDocumentError, match="Unknown unit"):
        Quantity("1", "meter")


@pytest.mark.parametrize(
    "value,unit,expected",
    [
        ("1", "cm", Quantity("10", "mm")),
        ("0.001", "m", Quantity("1", "mm")),
        ("-0.50", "cm", Quantity("-5", "mm")),
        ("72", "pt", Quantity("72", "pt")),
    ],
)
def test_input_quantity_helper_preserves_the_document_contract(value, unit, expected):
    with localcontext() as ctx:
        ctx.prec = 1
        assert quantity_from_input(value, unit) == expected
    with pytest.raises(InvalidDocumentError, match="Unknown unit"):
        Quantity("1", "cm")


def test_documents_own_all_data_and_roundtrip(catalog):
    data = snapshot(catalog).as_dict()
    document = Document(data, expected_type="cxp.snapshot")
    original = document.to_bytes()
    data["payload"]["capabilities"][0]["properties"]["count"] = 100
    document.payload["capabilities"].clear()
    document.as_dict()["extensions"]["org.example:x"] = True
    assert document.to_bytes() == original
    assert load_document(original, expected_type="cxp.snapshot") == document
    with pytest.raises(FrozenInstanceError):
        document._canonical = b"{}"
    schema = document_schema()
    schema.clear()
    assert "$defs" in document_schema()


def test_canonicalization_defaults_order_and_opaque_extensions(catalog):
    first = snapshot(catalog).as_dict()
    second = copy.deepcopy(first)
    second["payload"]["capabilities"][0]["properties"]["colors"].reverse()
    second["payload"]["capabilities"][0]["properties"]["width"]["value"] = "25.4000"
    second["payload"]["observed_at"] = "2026-09-03T10:00:00Z"
    second.pop("extensions")
    second.pop("critical_extensions")
    assert (
        Document(first, expected_type="cxp.snapshot").sha256
        == Document(second, expected_type="cxp.snapshot").sha256
    )
    extension = {
        "critical_extensions": ["unknown"],
        "value": "1.00",
        "unit": "fictional",
    }
    opaque = doc(
        "cxp.context", context().payload, extensions={"org.example:x": extension}
    )
    assert opaque.as_dict()["extensions"]["org.example:x"] == extension


@pytest.mark.parametrize(
    "raw,path",
    [
        (
            '{"document_type":"cxp.context","document_type":"cxp.context"}',
            "/document_type",
        ),
        ('{"payload":{"a/b":1,"a/b":2}}', "/payload/a~1b"),
        ('{"payload":{"a": [{"b":1,"b":2}]}}', "/payload/a/0/b"),
    ],
)
def test_duplicate_json_keys_are_rejected_before_schema(raw, path):
    with pytest.raises(InvalidDocumentError) as error:
        load_document(raw, expected_type="cxp.context")
    assert error.value.issues[0].code == "duplicate_key"
    assert error.value.issues[0].path == path


@pytest.mark.parametrize(
    "token", ["NaN", "Infinity", "1e999", "9007199254740992", "0.123456789012345678901"]
)
def test_unsafe_json_numbers_rejected_even_in_extensions(token):
    raw = (
        json.dumps(context().as_dict())[:-1]
        + ', "extensions":{"org.example:n":'
        + token
        + "}}"
    )
    # Eliminamos la clave previa para no confundir esta prueba con duplicados.
    raw = raw.replace('"extensions": {}, ', "")
    with pytest.raises(InvalidDocumentError) as error:
        load_document(raw, expected_type="cxp.context")
    assert error.value.issues[0].code in {
        "invalid_number",
        "unsafe_integer",
        "lossy_number",
    }


@pytest.mark.parametrize(
    "extra",
    [
        {"org.example:x": float("nan")},
        {"org.example:x": "\ud800"},
        {"org.example:x": "x" * 16385},
    ],
)
def test_invalid_python_json_input_is_rejected(extra):
    with pytest.raises(InvalidDocumentError):
        doc("cxp.context", context().payload, extensions=extra)


def test_resource_limits_and_cycles():
    with pytest.raises(InvalidDocumentError):
        load_document(b" " * (1024 * 1024 + 1), expected_type="cxp.context")
    value = []
    value.append(value)
    with pytest.raises(InvalidDocumentError, match="limits"):
        doc("cxp.context", context().payload, extensions={"org.example:x": value})
    with pytest.raises(InvalidDocumentError, match="limits"):
        doc("cxp.context", context().payload, extensions={"org.example:x": [0] * 20000})


@pytest.mark.parametrize(
    "field,value,error_type",
    [
        ("spec_version", 2, UnsupportedContractError),
        ("spec_version", True, InvalidDocumentError),
        ("document_type", "cxp.future", UnsupportedContractError),
        (
            "payload",
            {"subject_id": "s", "configuration_revision": "c", "surprise": 1},
            InvalidDocumentError,
        ),
    ],
)
def test_closed_versioned_contract(field, value, error_type):
    data = context().as_dict()
    data[field] = value
    with pytest.raises(error_type):
        Document(data, expected_type="cxp.context")


def test_critical_extension_rejects_entire_any(catalog):
    node = {
        "id": "all",
        "operator": "any",
        "conditions": [
            leaf(),
            leaf(
                id="r2",
                extensions={"org.example:x": 1},
                critical_extensions=["org.example:x"],
            ),
        ],
    }
    with pytest.raises(UnsupportedContractError) as error:
        evaluate(catalog, node)
    assert error.value.issues[0].path.endswith("/conditions/1/critical_extensions")
    with pytest.raises(InvalidDocumentError, match="no value"):
        doc("cxp.context", context().payload, critical_extensions=["org.example:x"])


def test_catalog_store_isolated_hash_bound_and_duplicate_safe(catalog):
    first = CatalogStore([catalog])
    ref = catalog_reference(catalog)
    assert first.resolve(ref) == catalog
    with pytest.raises(InvalidDocumentError, match="not registered"):
        CatalogStore().resolve(ref)
    with pytest.raises(InvalidDocumentError, match="content"):
        first.resolve({**ref, "sha256": "0" * 64})
    with pytest.raises(InvalidDocumentError, match="Duplicate catalog"):
        CatalogStore([catalog, catalog])
    assert first.validate_snapshot(snapshot(catalog)) == catalog


@pytest.mark.parametrize(
    "properties,code",
    [
        ({"count": True}, "property_type_mismatch"),
        ({"count": None}, "null_not_allowed"),
        ({"width": {"value": "1", "unit": "g"}}, "dimension_mismatch"),
        ({"quality": 1}, "property_type_mismatch"),
        ({"quality": "1e5"}, "invalid_decimal"),
        ({"mystery": 1}, "unknown_property"),
    ],
)
def test_catalog_typed_values_reject_bad_data(catalog, properties, code):
    with pytest.raises(InvalidDocumentError) as error:
        CatalogStore([catalog]).validate_snapshot(
            snapshot(catalog, properties=properties)
        )
    assert error.value.issues[0].code == code
    assert error.value.issues[0].path.startswith("/payload/capabilities/0/properties/")


def test_binding_contract_and_duplicate_identifiers(catalog):
    data = snapshot(catalog).payload
    data["capabilities"][0]["operations"][0]["result_type"] = "example.wrong"
    with pytest.raises(InvalidDocumentError, match="contradicts"):
        CatalogStore([catalog]).validate_snapshot(doc("cxp.snapshot", data))
    data["capabilities"].append(copy.deepcopy(data["capabilities"][0]))
    with pytest.raises(InvalidDocumentError, match="Duplicate"):
        doc("cxp.snapshot", data)
    with pytest.raises(InvalidDocumentError) as error:
        requirements(
            catalog, {"id": "g", "operator": "all", "conditions": [leaf(), leaf()]}
        )
    assert error.value.issues[0].path == "/payload/requirement/conditions/1/id"


@pytest.mark.parametrize(
    "node,verdict",
    [
        (leaf(), "compatible"),
        (leaf(capability="cut"), "indeterminate"),
        (leaf("equals", path="/properties/count", value=3), "compatible"),
        (leaf("equals", path="/properties/count", value=4), "incompatible"),
        (leaf("one_of", path="/properties/count", values=[1, 3]), "compatible"),
        (
            leaf("contains_all", path="/properties/colors", values=["white"]),
            "compatible",
        ),
        (
            leaf("contains_all", path="/properties/colors", values=["gloss"]),
            "incompatible",
        ),
        (leaf("equals", path="/properties/material", value=None), "compatible"),
        (leaf("equals", path="/properties/material", value="paper"), "incompatible"),
        (
            leaf(
                "equals", path="/properties/width", value={"value": "1", "unit": "in"}
            ),
            "compatible",
        ),
        (
            leaf(
                "range",
                path="/properties/quality",
                minimum="0.1",
                step="0.1",
                origin="0",
            ),
            "compatible",
        ),
        (
            leaf("range", path="/properties/count", minimum=3, minimum_inclusive=False),
            "incompatible",
        ),
        (leaf("range", path="/properties/count", maximum=3), "compatible"),
        (
            leaf("range", path="/properties/count", maximum=3, maximum_inclusive=False),
            "incompatible",
        ),
        (
            leaf("range", path="/properties/count", minimum=0, step=2, origin=0),
            "incompatible",
        ),
    ],
)
def test_comparison_operators(catalog, node, verdict):
    result = evaluate(catalog, node)
    assert result.payload["verdict"] == verdict
    assert result.payload["findings"][0]["requirement_id"] == "r1"
    assert result.payload["inputs"]["catalog"] == catalog.sha256


@pytest.mark.parametrize(
    "support,effective,verdict",
    [
        ("supported", True, "compatible"),
        ("unsupported", False, "incompatible"),
        ("accepted_noop", True, "incompatible"),
        ("accepted_noop", False, "compatible"),
    ],
)
def test_effective_support_policy(catalog, support, effective, verdict):
    assert (
        evaluate(
            catalog,
            leaf(require_effective=effective),
            snap=snapshot(catalog, support=support),
        ).payload["verdict"]
        == verdict
    )


@pytest.mark.parametrize("operator", ["all", "any"])
@pytest.mark.parametrize(
    "states",
    tuple(itertools.product(["compatible", "incompatible", "indeterminate"], repeat=2)),
)
def test_all_any_truth_tables(catalog, operator, states):
    nodes = {
        "compatible": leaf(),
        "incompatible": leaf("equals", path="/properties/count", value=999),
        "indeterminate": leaf(capability="cut"),
    }
    node = {
        "id": "g",
        "operator": operator,
        "conditions": [
            {**nodes[state], "id": f"r{i}"} for i, state in enumerate(states)
        ],
    }
    dominant = "incompatible" if operator == "all" else "compatible"
    expected = (
        dominant
        if dominant in states
        else "indeterminate"
        if "indeterminate" in states
        else states[0]
    )
    result = evaluate(catalog, node)
    assert result.payload["verdict"] == expected
    assert [item["verdict"] for item in result.payload["findings"]] == list(states)


def test_unknown_does_not_hide_known_negative_and_invalid_branches(catalog):
    data = snapshot(catalog).payload
    data["capabilities"][0]["operations"] = []
    snap = doc("cxp.snapshot", data)
    node = leaf("equals", path="/properties/count", value=999, operations=["submit"])
    assert evaluate(catalog, node, snap=snap).payload["verdict"] == "incompatible"
    node["value"] = 3
    assert evaluate(catalog, node, snap=snap).payload["verdict"] == "indeterminate"
    with pytest.raises(InvalidDocumentError, match="absent from catalog"):
        evaluate(
            catalog,
            {
                "id": "g",
                "operator": "any",
                "conditions": [leaf(), leaf(id="bad", capability="missing")],
            },
        )
    assert (
        evaluate(
            catalog,
            leaf("equals", path="/properties/count", value=0),
            snap=snapshot(catalog, properties={}),
        ).payload["verdict"]
        == "indeterminate"
    )


@pytest.mark.parametrize(
    "node",
    [
        leaf("range", path="/properties/count", minimum=4, maximum=3),
        leaf(
            "range",
            path="/properties/count",
            minimum=3,
            maximum=3,
            minimum_inclusive=False,
        ),
        leaf("range", path="/properties/count", minimum=0, step=0, origin=0),
        leaf("range", path="/properties/material", minimum="a"),
        leaf("contains_all", path="/properties/count", values=[]),
        leaf("equals", path="/properties/count", value=None),
        leaf(operations=["unlisted"]),
    ],
)
def test_semantically_invalid_requirements_do_not_produce_verdicts(catalog, node):
    with pytest.raises(InvalidDocumentError):
        evaluate(catalog, node)


@pytest.mark.parametrize(
    "updates,code",
    [
        ({"subject_id": "another"}, "subject_mismatch"),
        ({"configuration_revision": "another"}, "configuration_mismatch"),
        ({"as_of": "2026-09-03T09:59:59Z"}, "future_observation"),
        ({"as_of": "2026-09-03T10:01:01Z", "max_age_seconds": 60}, "stale_observation"),
    ],
)
def test_explicit_context_invalidates_claims(catalog, updates, code):
    result = evaluate(catalog, leaf(), ctx=context(**updates))
    assert result.payload["verdict"] == "indeterminate"
    assert result.payload["findings"][0]["code"] == code


def test_time_boundary_reproducibility_and_availability_are_orthogonal(catalog):
    snap = snapshot(catalog, availability="unavailable", connectivity="offline")
    ctx = context(as_of="2026-09-03T10:01:00Z", max_age_seconds=60)
    first = evaluate(catalog, leaf(), snap=snap, ctx=ctx)
    assert first.payload["verdict"] == "compatible"
    assert evaluate(catalog, leaf(), snap=snap, ctx=ctx) == first
    with pytest.raises(InvalidDocumentError):
        context(max_age_seconds=60)
    with pytest.raises(InvalidDocumentError):
        context(as_of="2026-02-30T10:00:00Z")


def request(*kinds, protocol=2, versions=(1,)):
    return doc(
        "cxp.exchange_request",
        {
            "protocol_version": protocol,
            "formats": [
                {"document_type": kind, "spec_versions": list(versions)}
                for kind in kinds
            ],
        },
    )


def test_negotiation_is_bound_and_never_downgrades(catalog):
    offered = request("cxp.snapshot", "cxp.requirements")
    response = negotiate_exchange(offered)
    agreement = ExchangeAgreement(offered, response)
    snap = snapshot(catalog)
    assert (
        agreement.decode(agreement.encode(snap), expected_type="cxp.snapshot") == snap
    )
    with pytest.raises(UnsupportedContractError, match="not negotiated"):
        agreement.encode(context())
    with pytest.raises(UnsupportedContractError):
        agreement.decode(snap.to_bytes(), expected_type="cxp.requirements")
    for incompatible in [
        request("cxp.snapshot", protocol=1),
        request("cxp.snapshot", versions=(2,)),
        request("cxp.future"),
    ]:
        rejected = negotiate_exchange(incompatible)
        assert rejected.payload["formats"] == []
        with pytest.raises(UnsupportedContractError):
            ExchangeAgreement(incompatible, rejected)
    with pytest.raises(InvalidDocumentError, match="another request"):
        ExchangeAgreement(request("cxp.context"), response)
    with pytest.raises(ValueError, match="unimplemented"):
        negotiate_exchange(offered, supported_formats={"cxp.future": (1,)})


def test_negotiation_rejects_partial_and_forged_acceptance():
    offered = request("cxp.snapshot", "cxp.requirements")
    response = negotiate_exchange(offered).payload
    response["formats"].pop()
    with pytest.raises(InvalidDocumentError, match="dropped"):
        ExchangeAgreement(offered, doc("cxp.exchange_response", response))
    response = negotiate_exchange(offered).payload
    response["formats"][0]["spec_version"] = 2
    with pytest.raises(InvalidDocumentError, match="unoffered"):
        ExchangeAgreement(offered, doc("cxp.exchange_response", response))


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", "invalid\n"),
        ("namespace", "org.exämple"),
        ("version", "1.0.0\n"),
        ("version", "1.0.0-01"),
    ],
)
def test_identity_grammar_is_not_weakened_by_regex_anchors(catalog, field, value):
    payload = catalog.payload
    payload["identity"][field] = value
    with pytest.raises(InvalidDocumentError):
        doc("cxp.catalog", payload)


def test_evaluation_has_no_clock_or_network_dependency(catalog, monkeypatch):
    import socket
    import time

    def forbidden(*args, **kwargs):
        pytest.fail("Pure evaluation attempted clock/network access")

    snap = snapshot(catalog)
    req = requirements(catalog, leaf())
    ctx = context()
    store = CatalogStore([catalog])
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(time, "time", forbidden)
    assert (
        evaluate_requirements(snap, req, ctx, catalogs=store).payload["verdict"]
        == "compatible"
    )


def test_detailed_evaluation_projects_the_exact_existing_document(catalog):
    snap = snapshot(catalog)
    req = requirements(
        catalog,
        leaf("range", path="/properties/count", minimum=4),
    )
    ctx = context()
    store = CatalogStore([catalog])
    previous = evaluate_requirements(snap, req, ctx, catalogs=store)
    detailed = evaluate_requirements_detailed(snap, req, ctx, catalogs=store)
    assert isinstance(detailed, EvaluationResult)
    assert detailed.document.to_bytes() == previous.to_bytes()
    assert detailed.verdict == "incompatible"
    assert detailed.is_compatible is False
    assert detailed.findings[0].code == "property_mismatch"
    assert detailed.findings[0].reason == "below_minimum"
    assert detailed.findings[0].actual_reported is True
    assert [(item.role, item.value) for item in detailed.findings[0].operands] == [
        ("actual", 3),
        ("minimum", 4),
    ]


def test_detailed_evaluation_distinguishes_null_from_absent(catalog):
    node = leaf("equals", path="/properties/material", value=None)
    null_detailed = evaluate_requirements_detailed(
        snapshot(catalog),
        requirements(catalog, node),
        context(),
        catalogs=CatalogStore([catalog]),
    )
    assert null_detailed.findings[0].reason == "requirement_satisfied"
    assert null_detailed.findings[0].actual_reported is True
    assert null_detailed.findings[0].operands[0].value is None
    absent_properties = snapshot(catalog).payload["capabilities"][0]["properties"]
    absent_properties.pop("material")
    detailed = evaluate_requirements_detailed(
        snapshot(catalog, properties=absent_properties),
        requirements(catalog, node),
        context(),
        catalogs=CatalogStore([catalog]),
    )
    assert detailed.findings[0].reason == "property_unreported"
    assert detailed.findings[0].actual_reported is False
    assert detailed.findings[0].operands == ()


@pytest.mark.parametrize(
    "node,reason",
    [
        (leaf("equals", path="/properties/count", value=4), "value_not_equal"),
        (
            leaf("one_of", path="/properties/count", values=[1, 2]),
            "value_not_in_set",
        ),
        (
            leaf("contains_all", path="/properties/colors", values=["spot"]),
            "missing_set_elements",
        ),
        (
            leaf(
                "range",
                path="/properties/count",
                minimum=3,
                minimum_inclusive=False,
            ),
            "minimum_excluded",
        ),
        (leaf("range", path="/properties/count", maximum=2), "above_maximum"),
        (
            leaf(
                "range",
                path="/properties/count",
                maximum=3,
                maximum_inclusive=False,
            ),
            "maximum_excluded",
        ),
        (
            leaf(
                "range",
                path="/properties/count",
                minimum=0,
                step=2,
                origin=0,
            ),
            "step_mismatch",
        ),
    ],
)
def test_detailed_evaluation_has_stable_comparison_reasons(catalog, node, reason):
    result = evaluate_requirements_detailed(
        snapshot(catalog),
        requirements(catalog, node),
        context(),
        catalogs=CatalogStore([catalog]),
    )
    assert result.verdict == "incompatible"
    assert result.findings[0].code == "property_mismatch"
    assert result.findings[0].reason == reason


def test_detailed_range_reports_an_explicit_nullable_value(catalog):
    catalog_data = catalog.payload
    quality = catalog_data["capabilities"][0]["properties"]["quality"]
    quality.update(nullable=True, null_meaning="No quality configured")
    nullable_catalog = doc("cxp.catalog", catalog_data)
    properties = snapshot(nullable_catalog).payload["capabilities"][0]["properties"]
    properties["quality"] = None
    result = evaluate_requirements_detailed(
        snapshot(nullable_catalog, properties=properties),
        requirements(
            nullable_catalog,
            leaf("range", path="/properties/quality", minimum="0"),
        ),
        context(),
        catalogs=CatalogStore([nullable_catalog]),
    )
    assert result.findings[0].reason == "null_not_comparable"
    assert result.findings[0].actual_reported is True
    assert result.findings[0].operands[0].value is None


@pytest.mark.parametrize(
    "number", [9007199254740992, 9007199254740993, -9007199254740993, 10**100]
)
def test_unsafe_integers_have_same_diagnostics_from_mapping_and_bytes(number):
    data = context().as_dict()
    data["extensions"] = {"org.example:number": number}
    results = []
    for value in (data, json.dumps(data)):
        with pytest.raises(InvalidDocumentError) as error:
            if isinstance(value, dict):
                Document(value, expected_type="cxp.context")
            else:
                load_document(value, expected_type="cxp.context")
        results.append([(issue.code, issue.path) for issue in error.value.issues])
    assert (
        results[0]
        == results[1]
        == [("unsafe_integer", "/extensions/org.example:number")]
    )


@pytest.mark.parametrize(
    "node,code,path",
    [
        (
            leaf("range", path="/properties/count", minimum=0, step=1),
            "step_requires_origin",
            "/origin",
        ),
        (
            leaf("range", path="/properties/count", minimum=0, origin=1),
            "origin_requires_step",
            "/step",
        ),
        (
            leaf("contains_all", path="/properties/colors", values=["white", "white"]),
            "duplicate_set_value",
            "/values/1",
        ),
    ],
)
def test_invalid_nested_requirements_have_specific_diagnostics(
    catalog, node, code, path
):
    with pytest.raises(InvalidDocumentError) as error:
        requirements(
            catalog,
            {"id": "root", "operator": "any", "conditions": [leaf(id="valid"), node]},
        )
    assert error.value.issues[0].code == code
    assert error.value.issues[0].path == "/payload/requirement/conditions/1" + path


def test_agreement_checks_actual_document_version():
    offered = request("cxp.context")
    agreement = ExchangeAgreement(offered, negotiate_exchange(offered))

    class FutureDocument:
        document_type = "cxp.context"
        spec_version = 2

        def to_bytes(self):
            pytest.fail("Unnegotiated version must not be encoded")

    with pytest.raises(UnsupportedContractError, match="not negotiated"):
        agreement.encode(FutureDocument())
