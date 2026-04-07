import importlib
from pathlib import Path

from cxp import catalog_satisfies_interface, get_catalog


def test_all_interface_modules_import_cleanly() -> None:
    root = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "cxp"
        / "catalogs"
        / "interfaces"
    )
    failures: list[tuple[str, str, str]] = []

    for path in sorted(root.rglob("*.py")):
        module_name = (
            "cxp."
            + str(path.relative_to(root.parent.parent))
            .replace("/", ".")
            .removesuffix(".py")
        )
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - failure path asserted below
            failures.append((module_name, type(exc).__name__, str(exc)))

    assert failures == []


def test_extended_catalogs_are_registered_on_root_import() -> None:
    expected_interfaces = (
        "cache/key-value",
        "database/common",
        "database/sql",
        "identity/auth-provider",
        "media/video-streaming",
        "messaging/event-bus",
        "notification/common",
        "printing/manager",
        "runtime/environment",
        "storage/blob",
        "transport/http-family",
    )

    for interface in expected_interfaces:
        assert get_catalog(interface) is not None


def test_runtime_environment_exposes_health_and_reload_capabilities() -> None:
    runtime_catalog = get_catalog("runtime/environment")

    assert runtime_catalog is not None
    assert runtime_catalog.has_operation("health", "runtime.health_check") is True
    assert runtime_catalog.has_operation("lifecycle", "runtime.reload") is True

    managed_tier = runtime_catalog.get_tier("managed")
    assert managed_tier is not None
    assert managed_tier.required_capabilities == (
        "configuration",
        "health",
        "lifecycle",
    )


def test_database_concrete_catalogs_satisfy_common_database_family() -> None:
    assert catalog_satisfies_interface("database/mongodb", "database/common")
    assert catalog_satisfies_interface("database/sql", "database/common")


def test_transport_http_catalog_remains_canonical_and_family_is_separate() -> None:
    transport_catalog = get_catalog("transport/http")
    transport_family_catalog = get_catalog("transport/http-family")

    assert transport_catalog is not None
    assert transport_catalog.abstract is False
    assert transport_family_catalog is not None
    assert transport_family_catalog.abstract is True

    request_dispatch = transport_family_catalog.get_capability("request_dispatch")
    assert request_dispatch is not None
    send_operation = request_dispatch.get_operation("http.send")
    assert send_operation is not None
    assert send_operation.idempotent is False


def test_async_domains_propagate_canonical_cancel_operations() -> None:
    from cxp.catalogs.interfaces.execution.plan_run import PLAN_RUN_OP_CANCEL
    from cxp.catalogs.interfaces.media.video_streaming import VIDEO_STREAMING_CATALOG
    from cxp.catalogs.interfaces.queue.task_engine import QUEUE_CATALOG

    assert (
        VIDEO_STREAMING_CATALOG.has_operation("transcoding", PLAN_RUN_OP_CANCEL)
        is True
    )
    assert QUEUE_CATALOG.has_operation("monitoring", "queue.cancel") is True
