"""Propiedades algebraicas de las rutas críticas del intercambio."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from cxp.exchange import (
    CatalogStore,
    Document,
    Quantity,
    catalog_reference,
    evaluate_requirements,
    evaluate_requirements_detailed,
    load_document,
    load_reference_catalog,
    normalize_decimal,
    quantity_from_input,
)


def document(document_type: str, payload: dict[str, object]) -> Document:
    return Document(
        {
            "document_type": document_type,
            "spec_version": 1,
            "payload": payload,
        },
        expected_type=document_type,
    )


@given(
    coefficient=st.integers(min_value=-(10**30), max_value=10**30),
    scale=st.integers(min_value=0, max_value=12),
)
def test_convenience_units_are_exact_for_all_generated_decimals(
    coefficient: int, scale: int
):
    sign = "-" if coefficient < 0 else ""
    digits = str(abs(coefficient)).zfill(scale + 1)
    value = f"{sign}{digits[:-scale]}.{digits[-scale:]}" if scale else f"{sign}{digits}"
    normalized = normalize_decimal(value)
    assert normalize_decimal(normalized) == normalized
    assert quantity_from_input(value, "cm").exact_value == (
        Quantity(normalized, "mm").exact_value * 10
    )
    assert quantity_from_input(value, "m").exact_value == (
        Quantity(normalized, "mm").exact_value * 1000
    )


json_scalars = (
    st.none()
    | st.booleans()
    | st.integers(min_value=-(2**31), max_value=2**31 - 1)
    | st.text(alphabet=st.characters(codec="utf-8"), max_size=32)
)
json_values = st.recursive(
    json_scalars,
    lambda children: (
        st.lists(children, max_size=5)
        | st.dictionaries(
            st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=8),
            children,
            max_size=5,
        )
    ),
    max_leaves=20,
)


@given(value=json_values)
@settings(max_examples=75)
def test_canonical_documents_roundtrip_arbitrary_bounded_extensions(value: object):
    context = document(
        "cxp.context",
        {"subject_id": "subject", "configuration_revision": "revision"},
    ).as_dict()
    context["extensions"] = {"org.example:generated": value}
    first = Document(context, expected_type="cxp.context")
    assert load_document(first.to_bytes(), expected_type="cxp.context") == first


@given(
    actual=st.integers(min_value=0, max_value=1000),
    minimum=st.integers(min_value=0, max_value=1000),
)
@settings(max_examples=75)
def test_detailed_and_document_evaluation_are_one_engine(actual: int, minimum: int):
    catalog = load_reference_catalog("physical-printing", version="1.1.0")
    reference = catalog_reference(catalog)
    snapshot = document(
        "cxp.snapshot",
        {
            "provider_id": "generated",
            "subject_id": "surface",
            "catalog": reference,
            "configuration_revision": "configuration",
            "observed_at": "2026-09-04T10:00:00Z",
            "source": {"kind": "declared", "reference": "generated"},
            "capabilities": [
                {
                    "name": "printing.surface",
                    "support": "supported",
                    "properties": {
                        "max_loaded_mass": {
                            "value": str(actual),
                            "unit": "kg",
                        }
                    },
                }
            ],
        },
    )
    requirements = document(
        "cxp.requirements",
        {
            "catalog": reference,
            "requirement": {
                "id": "generated-minimum",
                "operator": "range",
                "capability": "printing.surface",
                "path": "/properties/max_loaded_mass",
                "minimum": {"value": str(minimum), "unit": "kg"},
            },
        },
    )
    context = document(
        "cxp.context",
        {"subject_id": "surface", "configuration_revision": "configuration"},
    )
    store = CatalogStore([catalog])
    projected = evaluate_requirements(snapshot, requirements, context, catalogs=store)
    detailed = evaluate_requirements_detailed(
        snapshot, requirements, context, catalogs=store
    )
    assert detailed.document.to_bytes() == projected.to_bytes()
    assert detailed.is_compatible is (actual >= minimum)
    if actual < minimum:
        assert detailed.findings[0].reason == "below_minimum"
