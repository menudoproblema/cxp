from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityCatalog,
    CapabilityProfile,
    CapabilityRequirement,
    CapabilityTelemetry,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    TelemetryEventSpec,
    TelemetryFieldRequirement,
    TelemetryMetricSpec,
    TelemetrySpanSpec,
    register_catalog,
)
from cxp.catalogs.common import (
    CXP_RESOURCE_KIND,
    CXP_RESOURCE_NAME,
    UNIT_SECONDS,
)
from cxp.catalogs.interfaces.browser.family import BROWSER_AUTOMATION_INTERFACE
from cxp.catalogs.results import ActionResult
from cxp.telemetry import TelemetrySeverity

PLAYWRIGHT_BROWSER_INTERFACE = "browser/playwright"

PLAYWRIGHT_BROWSER_LIFECYCLE = "browser_lifecycle"
PLAYWRIGHT_BROWSER_CONTEXT_MANAGEMENT = "context_management"
PLAYWRIGHT_BROWSER_PAGE_NAVIGATION = "page_navigation"
PLAYWRIGHT_BROWSER_LOCATOR_RESOLUTION = "locator_resolution"
PLAYWRIGHT_BROWSER_DOM_INTERACTION = "dom_interaction"
PLAYWRIGHT_BROWSER_WAIT_CONDITIONS = "wait_conditions"
PLAYWRIGHT_BROWSER_SCRIPT_EVALUATION = "script_evaluation"
PLAYWRIGHT_BROWSER_NETWORK_OBSERVATION = "network_observation"
PLAYWRIGHT_BROWSER_SCREENSHOT_CAPTURE = "screenshot_capture"
PLAYWRIGHT_BROWSER_DIALOG_HANDLING = "dialog_handling"

PLAYWRIGHT_BROWSER_LAUNCH = "browser.launch"
PLAYWRIGHT_BROWSER_CLOSE = "browser.close"
PLAYWRIGHT_BROWSER_CONTEXT_CREATE = "context.create"
PLAYWRIGHT_BROWSER_CONTEXT_CLOSE = "context.close"
PLAYWRIGHT_BROWSER_PAGE_GOTO = "page.goto"
PLAYWRIGHT_BROWSER_PAGE_RELOAD = "page.reload"
PLAYWRIGHT_BROWSER_PAGE_GO_BACK = "page.go_back"
PLAYWRIGHT_BROWSER_LOCATOR_QUERY = "locator.query"
PLAYWRIGHT_BROWSER_LOCATOR_FILTER = "locator.filter"
PLAYWRIGHT_BROWSER_ELEMENT_CLICK = "element.click"
PLAYWRIGHT_BROWSER_ELEMENT_FILL = "element.fill"
PLAYWRIGHT_BROWSER_ELEMENT_PRESS = "element.press"
PLAYWRIGHT_BROWSER_ELEMENT_SELECT_OPTION = "element.select_option"
PLAYWRIGHT_BROWSER_WAIT_FOR_SELECTOR = "wait.for_selector"
PLAYWRIGHT_BROWSER_WAIT_FOR_URL = "wait.for_url"
PLAYWRIGHT_BROWSER_WAIT_FOR_RESPONSE = "wait.for_response"
PLAYWRIGHT_BROWSER_PAGE_EVALUATE = "page.evaluate"
PLAYWRIGHT_BROWSER_ELEMENT_EVALUATE = "element.evaluate"
PLAYWRIGHT_BROWSER_NETWORK_REQUEST_OBSERVE = "network.request.observe"
PLAYWRIGHT_BROWSER_NETWORK_RESPONSE_OBSERVE = "network.response.observe"
PLAYWRIGHT_BROWSER_PAGE_SCREENSHOT = "page.screenshot"
PLAYWRIGHT_BROWSER_ELEMENT_SCREENSHOT = "element.screenshot"
PLAYWRIGHT_BROWSER_DIALOG_ACCEPT = "dialog.accept"
PLAYWRIGHT_BROWSER_DIALOG_DISMISS = "dialog.dismiss"

PLAYWRIGHT_BROWSER_CORE_TIER = "core"
PLAYWRIGHT_BROWSER_OBSERVABLE_TIER = "observable"
PLAYWRIGHT_BROWSER_CORE_PROFILE_NAME = "playwright-core"
PLAYWRIGHT_BROWSER_OBSERVABLE_PROFILE_NAME = "playwright-observable"

_BROWSER_ENGINE_FIELD = TelemetryFieldRequirement(name="browser.engine")
_BROWSER_HEADLESS_FIELD = TelemetryFieldRequirement(name="browser.headless")
_BROWSER_CONTEXT_ID_FIELD = TelemetryFieldRequirement(name="browser.context.id")
_BROWSER_PAGE_ID_FIELD = TelemetryFieldRequirement(name="browser.page.id")
_BROWSER_OUTCOME_FIELD = TelemetryFieldRequirement(name="browser.outcome")
_BROWSER_ACTION_NAME_FIELD = TelemetryFieldRequirement(name="browser.action.name")
_BROWSER_URL_HOST_FIELD = TelemetryFieldRequirement(name="browser.url.host")
_BROWSER_URL_PATH_TEMPLATE_FIELD = TelemetryFieldRequirement(
    name="browser.url.path_template"
)
_BROWSER_LOCATOR_KIND_FIELD = TelemetryFieldRequirement(name="browser.locator.kind")
_BROWSER_WAIT_CONDITION_FIELD = TelemetryFieldRequirement(name="browser.wait.condition")
_BROWSER_SCRIPT_KIND_FIELD = TelemetryFieldRequirement(name="browser.script.kind")
_BROWSER_NETWORK_PHASE_FIELD = TelemetryFieldRequirement(name="browser.network.phase")
_BROWSER_REQUEST_URL_HOST_FIELD = TelemetryFieldRequirement(
    name="browser.request.url.host"
)
_BROWSER_SCREENSHOT_TARGET_FIELD = TelemetryFieldRequirement(
    name="browser.screenshot.target"
)
_BROWSER_DIALOG_TYPE_FIELD = TelemetryFieldRequirement(name="browser.dialog.type")


def _telemetry_fields(
    *groups: tuple[TelemetryFieldRequirement, ...],
) -> tuple[TelemetryFieldRequirement, ...]:
    ordered: list[TelemetryFieldRequirement] = []
    seen: set[str] = set()

    for group in groups:
        for field in group:
            if field.name in seen:
                continue
            seen.add(field.name)
            ordered.append(field)

    return tuple(ordered)


def _browser_telemetry(
    *,
    span_name: str,
    span_attributes: tuple[TelemetryFieldRequirement, ...],
    metric_name: str,
    metric_labels: tuple[TelemetryFieldRequirement, ...],
    event_type: str,
    event_payload_keys: tuple[TelemetryFieldRequirement, ...],
    description: str,
    metric_unit: str | None = "s",
    event_severity: TelemetrySeverity | None = None,
) -> CapabilityTelemetry:
    return CapabilityTelemetry(
        spans=(
            TelemetrySpanSpec(
                name=span_name,
                required_attributes=_telemetry_fields(
                    (CXP_RESOURCE_NAME, CXP_RESOURCE_KIND, _BROWSER_ENGINE_FIELD),
                    span_attributes,
                ),
                description=description,
            ),
        ),
        metrics=(
            TelemetryMetricSpec(
                name=metric_name,
                unit=metric_unit,
                required_labels=_telemetry_fields(
                    (CXP_RESOURCE_NAME, CXP_RESOURCE_KIND, _BROWSER_ENGINE_FIELD),
                    metric_labels,
                ),
                description=f"{description} metric.",
            ),
        ),
        events=(
            TelemetryEventSpec(
                event_type=event_type,
                severity=event_severity,
                required_payload_keys=_telemetry_fields(
                    (CXP_RESOURCE_NAME, CXP_RESOURCE_KIND, _BROWSER_ENGINE_FIELD),
                    event_payload_keys,
                ),
                description=f"{description} event.",
            ),
        ),
    )


PLAYWRIGHT_BROWSER_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=PLAYWRIGHT_BROWSER_INTERFACE,
        satisfies_interfaces=(BROWSER_AUTOMATION_INTERFACE,),
        description=(
            "Canonical catalog for Playwright-style browser automation with "
            "navigation, DOM interaction, waiting and observability semantics."
        ),
        capabilities=(
            CatalogCapability(
                name=PLAYWRIGHT_BROWSER_LIFECYCLE,
                description="Launch and close browser sessions.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="browser.launch",
                            required_attributes=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_HEADLESS_FIELD,
                                ),
                            ),
                            description="Browser launch operation.",
                        ),
                        TelemetrySpanSpec(
                            name="browser.close",
                            required_attributes=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                ),
                            ),
                            description="Browser close operation.",
                        ),
                    ),
                    metrics=(
                        TelemetryMetricSpec(
                            name="browser.launch.duration",
                            unit=UNIT_SECONDS,
                            required_labels=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_HEADLESS_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                            description="Browser launch duration metric.",
                        ),
                        TelemetryMetricSpec(
                            name="browser.close.duration",
                            unit=UNIT_SECONDS,
                            required_labels=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                            description="Browser close duration metric.",
                        ),
                    ),
                    events=(
                        TelemetryEventSpec(
                            event_type="browser.session.launched",
                            required_payload_keys=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_HEADLESS_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                        ),
                        TelemetryEventSpec(
                            event_type="browser.session.launch_failed",
                            severity="error",
                            required_payload_keys=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_HEADLESS_FIELD,
                                ),
                            ),
                        ),
                        TelemetryEventSpec(
                            event_type="browser.session.closed",
                            required_payload_keys=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_LAUNCH,
                        result_type="browser.session",
                        description="Launch a browser process.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_CLOSE,
                        result_type="action.result",
                        result_schema=ActionResult,
                        description="Close a browser process.",
                    ),
                ),
            ),
            CatalogCapability(
                name=PLAYWRIGHT_BROWSER_CONTEXT_MANAGEMENT,
                description="Create and dispose browser contexts.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="browser.context.create",
                            required_attributes=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                ),
                            ),
                            description="Browser context creation operation.",
                        ),
                        TelemetrySpanSpec(
                            name="browser.context.close",
                            required_attributes=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_CONTEXT_ID_FIELD,
                                ),
                            ),
                            description="Browser context close operation.",
                        ),
                    ),
                    metrics=(
                        TelemetryMetricSpec(
                            name="browser.context.create.duration",
                            unit=UNIT_SECONDS,
                            required_labels=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                            description="Browser context creation duration metric.",
                        ),
                        TelemetryMetricSpec(
                            name="browser.context.close.duration",
                            unit=UNIT_SECONDS,
                            required_labels=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                            description="Browser context close duration metric.",
                        ),
                    ),
                    events=(
                        TelemetryEventSpec(
                            event_type="browser.context.created",
                            required_payload_keys=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_CONTEXT_ID_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                        ),
                        TelemetryEventSpec(
                            event_type="browser.context.create_failed",
                            severity="error",
                            required_payload_keys=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                ),
                            ),
                        ),
                        TelemetryEventSpec(
                            event_type="browser.context.closed",
                            required_payload_keys=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_CONTEXT_ID_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_CONTEXT_CREATE,
                        result_type="browser.context",
                        description="Create a fresh browser context.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_CONTEXT_CLOSE,
                        result_type="action.result",
                        result_schema=ActionResult,
                        description="Close an existing browser context.",
                    ),
                ),
            ),
            CatalogCapability(
                name=PLAYWRIGHT_BROWSER_PAGE_NAVIGATION,
                description="Navigate pages and move through browser history.",
                telemetry=_browser_telemetry(
                    span_name="browser.page.navigate",
                    span_attributes=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_CONTEXT_ID_FIELD,
                        _BROWSER_PAGE_ID_FIELD,
                        _BROWSER_URL_HOST_FIELD,
                        _BROWSER_URL_PATH_TEMPLATE_FIELD,
                    ),
                    metric_name="browser.navigation.duration",
                    metric_labels=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_URL_HOST_FIELD,
                        _BROWSER_OUTCOME_FIELD,
                    ),
                    event_type="browser.navigation.completed",
                    event_payload_keys=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_PAGE_ID_FIELD,
                        _BROWSER_URL_HOST_FIELD,
                        _BROWSER_OUTCOME_FIELD,
                    ),
                    description="Page navigation activity.",
                ),
                operations=(
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_PAGE_GOTO,
                        result_type="response",
                        description="Navigate the page to a URL.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_PAGE_RELOAD,
                        result_type="response",
                        description="Reload the current page.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_PAGE_GO_BACK,
                        result_type="response",
                        description="Navigate backward in history.",
                    ),
                ),
            ),
            CatalogCapability(
                name=PLAYWRIGHT_BROWSER_LOCATOR_RESOLUTION,
                description="Resolve and refine locators before interactions.",
                telemetry=_browser_telemetry(
                    span_name="browser.locator.resolve",
                    span_attributes=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_PAGE_ID_FIELD,
                        _BROWSER_LOCATOR_KIND_FIELD,
                    ),
                    metric_name="browser.locator.resolve.duration",
                    metric_labels=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_LOCATOR_KIND_FIELD,
                        _BROWSER_OUTCOME_FIELD,
                    ),
                    event_type="browser.locator.resolved",
                    event_payload_keys=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_LOCATOR_KIND_FIELD,
                        _BROWSER_OUTCOME_FIELD,
                    ),
                    description="Locator resolution activity.",
                ),
                operations=(
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_LOCATOR_QUERY,
                        result_type="locator",
                        description="Resolve an initial locator.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_LOCATOR_FILTER,
                        result_type="locator",
                        description="Refine an existing locator.",
                    ),
                ),
            ),
            CatalogCapability(
                name=PLAYWRIGHT_BROWSER_DOM_INTERACTION,
                description="Interact with DOM elements once resolved.",
                telemetry=_browser_telemetry(
                    span_name="browser.action",
                    span_attributes=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_PAGE_ID_FIELD,
                        _BROWSER_ACTION_NAME_FIELD,
                        _BROWSER_LOCATOR_KIND_FIELD,
                    ),
                    metric_name="browser.action.duration",
                    metric_labels=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_ACTION_NAME_FIELD,
                        _BROWSER_OUTCOME_FIELD,
                    ),
                    event_type="browser.action.completed",
                    event_payload_keys=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_PAGE_ID_FIELD,
                        _BROWSER_ACTION_NAME_FIELD,
                        _BROWSER_OUTCOME_FIELD,
                    ),
                    description="DOM interaction activity.",
                ),
                operations=(
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_ELEMENT_CLICK,
                        result_type="action.result",
                        result_schema=ActionResult,
                        description="Click an element.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_ELEMENT_FILL,
                        result_type="action.result",
                        result_schema=ActionResult,
                        description="Fill an input element.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_ELEMENT_PRESS,
                        result_type="action.result",
                        result_schema=ActionResult,
                        description="Press a key on an element.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_ELEMENT_SELECT_OPTION,
                        result_type="action.result",
                        result_schema=ActionResult,
                        description="Select an option on a form control.",
                    ),
                ),
            ),
            CatalogCapability(
                name=PLAYWRIGHT_BROWSER_WAIT_CONDITIONS,
                description="Explicit waiting primitives.",
                telemetry=_browser_telemetry(
                    span_name="browser.wait",
                    span_attributes=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_PAGE_ID_FIELD,
                        _BROWSER_WAIT_CONDITION_FIELD,
                    ),
                    metric_name="browser.wait.duration",
                    metric_labels=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_WAIT_CONDITION_FIELD,
                        _BROWSER_OUTCOME_FIELD,
                    ),
                    event_type="browser.wait.completed",
                    event_payload_keys=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_WAIT_CONDITION_FIELD,
                        _BROWSER_OUTCOME_FIELD,
                    ),
                    description="Wait condition activity.",
                ),
                operations=(
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_WAIT_FOR_SELECTOR,
                        result_type="action.result",
                        result_schema=ActionResult,
                        description="Wait for a selector to satisfy a condition.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_WAIT_FOR_URL,
                        result_type="action.result",
                        result_schema=ActionResult,
                        description="Wait for a URL match.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_WAIT_FOR_RESPONSE,
                        result_type="response",
                        description="Wait for a matching response.",
                    ),
                ),
            ),
            CatalogCapability(
                name=PLAYWRIGHT_BROWSER_SCRIPT_EVALUATION,
                description="Evaluate scripts on pages or elements.",
                telemetry=_browser_telemetry(
                    span_name="browser.script.evaluate",
                    span_attributes=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_PAGE_ID_FIELD,
                        _BROWSER_SCRIPT_KIND_FIELD,
                    ),
                    metric_name="browser.script.evaluate.duration",
                    metric_labels=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_SCRIPT_KIND_FIELD,
                        _BROWSER_OUTCOME_FIELD,
                    ),
                    event_type="browser.script.evaluated",
                    event_payload_keys=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_SCRIPT_KIND_FIELD,
                        _BROWSER_OUTCOME_FIELD,
                    ),
                    description="Script evaluation activity.",
                ),
                operations=(
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_PAGE_EVALUATE,
                        result_type="json",
                        description="Evaluate a script in page context.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_ELEMENT_EVALUATE,
                        result_type="json",
                        description="Evaluate a script against an element.",
                    ),
                ),
            ),
            CatalogCapability(
                name=PLAYWRIGHT_BROWSER_NETWORK_OBSERVATION,
                description="Observe requests and responses triggered by the browser.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="browser.request.observe",
                            required_attributes=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_PAGE_ID_FIELD,
                                    _BROWSER_NETWORK_PHASE_FIELD,
                                    _BROWSER_REQUEST_URL_HOST_FIELD,
                                ),
                            ),
                            description="Network request observation activity.",
                        ),
                        TelemetrySpanSpec(
                            name="browser.response.observe",
                            required_attributes=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_PAGE_ID_FIELD,
                                    _BROWSER_NETWORK_PHASE_FIELD,
                                    _BROWSER_REQUEST_URL_HOST_FIELD,
                                ),
                            ),
                            description="Network response observation activity.",
                        ),
                    ),
                    metrics=(
                        TelemetryMetricSpec(
                            name="browser.request.duration",
                            unit=UNIT_SECONDS,
                            required_labels=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_NETWORK_PHASE_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                            description="Observed request duration metric.",
                        ),
                        TelemetryMetricSpec(
                            name="browser.response.duration",
                            unit=UNIT_SECONDS,
                            required_labels=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_NETWORK_PHASE_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                            description="Observed response duration metric.",
                        ),
                    ),
                    events=(
                        TelemetryEventSpec(
                            event_type="browser.request.observed",
                            required_payload_keys=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_PAGE_ID_FIELD,
                                    _BROWSER_NETWORK_PHASE_FIELD,
                                    _BROWSER_REQUEST_URL_HOST_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                        ),
                        TelemetryEventSpec(
                            event_type="browser.response.observed",
                            required_payload_keys=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_PAGE_ID_FIELD,
                                    _BROWSER_NETWORK_PHASE_FIELD,
                                    _BROWSER_REQUEST_URL_HOST_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                        ),
                        TelemetryEventSpec(
                            event_type="browser.request.failed",
                            severity="error",
                            required_payload_keys=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_PAGE_ID_FIELD,
                                    _BROWSER_NETWORK_PHASE_FIELD,
                                    _BROWSER_REQUEST_URL_HOST_FIELD,
                                ),
                            ),
                        ),
                        TelemetryEventSpec(
                            event_type="browser.response.failed",
                            severity="error",
                            required_payload_keys=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_PAGE_ID_FIELD,
                                    _BROWSER_NETWORK_PHASE_FIELD,
                                    _BROWSER_REQUEST_URL_HOST_FIELD,
                                ),
                            ),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_NETWORK_REQUEST_OBSERVE,
                        result_type="request",
                        description="Observe a browser request.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_NETWORK_RESPONSE_OBSERVE,
                        result_type="response",
                        description="Observe a browser response.",
                    ),
                ),
            ),
            CatalogCapability(
                name=PLAYWRIGHT_BROWSER_SCREENSHOT_CAPTURE,
                description="Capture screenshots of pages or elements.",
                telemetry=_browser_telemetry(
                    span_name="browser.screenshot.capture",
                    span_attributes=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_PAGE_ID_FIELD,
                        _BROWSER_SCREENSHOT_TARGET_FIELD,
                    ),
                    metric_name="browser.screenshot.capture.duration",
                    metric_labels=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_SCREENSHOT_TARGET_FIELD,
                        _BROWSER_OUTCOME_FIELD,
                    ),
                    event_type="browser.screenshot.captured",
                    event_payload_keys=(
                        _BROWSER_ENGINE_FIELD,
                        _BROWSER_SCREENSHOT_TARGET_FIELD,
                        _BROWSER_OUTCOME_FIELD,
                    ),
                    description="Screenshot capture activity.",
                ),
                operations=(
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_PAGE_SCREENSHOT,
                        result_type="artifact",
                        description="Capture a page screenshot.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_ELEMENT_SCREENSHOT,
                        result_type="artifact",
                        description="Capture an element screenshot.",
                    ),
                ),
            ),
            CatalogCapability(
                name=PLAYWRIGHT_BROWSER_DIALOG_HANDLING,
                description="Accept or dismiss browser dialogs.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="browser.dialog.handle",
                            required_attributes=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_PAGE_ID_FIELD,
                                    _BROWSER_DIALOG_TYPE_FIELD,
                                    _BROWSER_ACTION_NAME_FIELD,
                                ),
                            ),
                            description="Dialog handling activity.",
                        ),
                    ),
                    metrics=(
                        TelemetryMetricSpec(
                            name="browser.dialog.duration",
                            unit=UNIT_SECONDS,
                            required_labels=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_DIALOG_TYPE_FIELD,
                                    _BROWSER_ACTION_NAME_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                            description="Dialog handling duration metric.",
                        ),
                    ),
                    events=(
                        TelemetryEventSpec(
                            event_type="browser.dialog.opened",
                            required_payload_keys=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_PAGE_ID_FIELD,
                                    _BROWSER_DIALOG_TYPE_FIELD,
                                ),
                            ),
                        ),
                        TelemetryEventSpec(
                            event_type="browser.dialog.handled",
                            required_payload_keys=_telemetry_fields(
                                (
                                    CXP_RESOURCE_NAME,
                                    CXP_RESOURCE_KIND,
                                    _BROWSER_ENGINE_FIELD,
                                    _BROWSER_PAGE_ID_FIELD,
                                    _BROWSER_DIALOG_TYPE_FIELD,
                                    _BROWSER_ACTION_NAME_FIELD,
                                    _BROWSER_OUTCOME_FIELD,
                                ),
                            ),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_DIALOG_ACCEPT,
                        result_type="action.result",
                        result_schema=ActionResult,
                        description="Accept a dialog.",
                    ),
                    CatalogOperation(
                        name=PLAYWRIGHT_BROWSER_DIALOG_DISMISS,
                        result_type="action.result",
                        result_schema=ActionResult,
                        description="Dismiss a dialog.",
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name=PLAYWRIGHT_BROWSER_CORE_TIER,
                required_capabilities=(
                    PLAYWRIGHT_BROWSER_LIFECYCLE,
                    PLAYWRIGHT_BROWSER_CONTEXT_MANAGEMENT,
                    PLAYWRIGHT_BROWSER_PAGE_NAVIGATION,
                    PLAYWRIGHT_BROWSER_LOCATOR_RESOLUTION,
                    PLAYWRIGHT_BROWSER_DOM_INTERACTION,
                    PLAYWRIGHT_BROWSER_WAIT_CONDITIONS,
                ),
                description="Core Playwright automation surface.",
            ),
            ConformanceTier(
                name=PLAYWRIGHT_BROWSER_OBSERVABLE_TIER,
                required_capabilities=(
                    PLAYWRIGHT_BROWSER_LIFECYCLE,
                    PLAYWRIGHT_BROWSER_CONTEXT_MANAGEMENT,
                    PLAYWRIGHT_BROWSER_PAGE_NAVIGATION,
                    PLAYWRIGHT_BROWSER_LOCATOR_RESOLUTION,
                    PLAYWRIGHT_BROWSER_DOM_INTERACTION,
                    PLAYWRIGHT_BROWSER_WAIT_CONDITIONS,
                    PLAYWRIGHT_BROWSER_SCRIPT_EVALUATION,
                    PLAYWRIGHT_BROWSER_NETWORK_OBSERVATION,
                    PLAYWRIGHT_BROWSER_SCREENSHOT_CAPTURE,
                    PLAYWRIGHT_BROWSER_DIALOG_HANDLING,
                ),
                description="Playwright automation with richer observability helpers.",
            ),
        ),
    )
)

PLAYWRIGHT_BROWSER_CORE_PROFILE = CapabilityProfile(
    name=PLAYWRIGHT_BROWSER_CORE_PROFILE_NAME,
    interface=PLAYWRIGHT_BROWSER_INTERFACE,
    description="Reusable profile for the core Playwright automation surface.",
    requirements=(
        CapabilityRequirement(
            capability_name=PLAYWRIGHT_BROWSER_LIFECYCLE,
            required_operations=(
                PLAYWRIGHT_BROWSER_LAUNCH,
                PLAYWRIGHT_BROWSER_CLOSE,
            ),
        ),
        CapabilityRequirement(
            capability_name=PLAYWRIGHT_BROWSER_CONTEXT_MANAGEMENT,
            required_operations=(
                PLAYWRIGHT_BROWSER_CONTEXT_CREATE,
                PLAYWRIGHT_BROWSER_CONTEXT_CLOSE,
            ),
        ),
        CapabilityRequirement(
            capability_name=PLAYWRIGHT_BROWSER_PAGE_NAVIGATION,
            required_operations=(
                PLAYWRIGHT_BROWSER_PAGE_GOTO,
                PLAYWRIGHT_BROWSER_PAGE_RELOAD,
                PLAYWRIGHT_BROWSER_PAGE_GO_BACK,
            ),
        ),
        CapabilityRequirement(
            capability_name=PLAYWRIGHT_BROWSER_LOCATOR_RESOLUTION,
            required_operations=(
                PLAYWRIGHT_BROWSER_LOCATOR_QUERY,
                PLAYWRIGHT_BROWSER_LOCATOR_FILTER,
            ),
        ),
        CapabilityRequirement(
            capability_name=PLAYWRIGHT_BROWSER_DOM_INTERACTION,
            required_operations=(
                PLAYWRIGHT_BROWSER_ELEMENT_CLICK,
                PLAYWRIGHT_BROWSER_ELEMENT_FILL,
                PLAYWRIGHT_BROWSER_ELEMENT_PRESS,
                PLAYWRIGHT_BROWSER_ELEMENT_SELECT_OPTION,
            ),
        ),
        CapabilityRequirement(
            capability_name=PLAYWRIGHT_BROWSER_WAIT_CONDITIONS,
            required_operations=(
                PLAYWRIGHT_BROWSER_WAIT_FOR_SELECTOR,
                PLAYWRIGHT_BROWSER_WAIT_FOR_URL,
                PLAYWRIGHT_BROWSER_WAIT_FOR_RESPONSE,
            ),
        ),
    ),
)

PLAYWRIGHT_BROWSER_OBSERVABLE_PROFILE = CapabilityProfile(
    name=PLAYWRIGHT_BROWSER_OBSERVABLE_PROFILE_NAME,
    interface=PLAYWRIGHT_BROWSER_INTERFACE,
    description="Profile with the broader Playwright observability surface.",
    requirements=(
        *PLAYWRIGHT_BROWSER_CORE_PROFILE.requirements,
        CapabilityRequirement(
            capability_name=PLAYWRIGHT_BROWSER_SCRIPT_EVALUATION,
            required_operations=(
                PLAYWRIGHT_BROWSER_PAGE_EVALUATE,
                PLAYWRIGHT_BROWSER_ELEMENT_EVALUATE,
            ),
        ),
        CapabilityRequirement(
            capability_name=PLAYWRIGHT_BROWSER_NETWORK_OBSERVATION,
            required_operations=(
                PLAYWRIGHT_BROWSER_NETWORK_REQUEST_OBSERVE,
                PLAYWRIGHT_BROWSER_NETWORK_RESPONSE_OBSERVE,
            ),
        ),
        CapabilityRequirement(
            capability_name=PLAYWRIGHT_BROWSER_SCREENSHOT_CAPTURE,
            required_operations=(
                PLAYWRIGHT_BROWSER_PAGE_SCREENSHOT,
                PLAYWRIGHT_BROWSER_ELEMENT_SCREENSHOT,
            ),
        ),
        CapabilityRequirement(
            capability_name=PLAYWRIGHT_BROWSER_DIALOG_HANDLING,
            required_operations=(
                PLAYWRIGHT_BROWSER_DIALOG_ACCEPT,
                PLAYWRIGHT_BROWSER_DIALOG_DISMISS,
            ),
        ),
    ),
)

__all__ = (
    "PLAYWRIGHT_BROWSER_CATALOG",
    "PLAYWRIGHT_BROWSER_CLOSE",
    "PLAYWRIGHT_BROWSER_CONTEXT_CLOSE",
    "PLAYWRIGHT_BROWSER_CONTEXT_CREATE",
    "PLAYWRIGHT_BROWSER_CONTEXT_MANAGEMENT",
    "PLAYWRIGHT_BROWSER_CORE_PROFILE",
    "PLAYWRIGHT_BROWSER_CORE_PROFILE_NAME",
    "PLAYWRIGHT_BROWSER_CORE_TIER",
    "PLAYWRIGHT_BROWSER_DIALOG_ACCEPT",
    "PLAYWRIGHT_BROWSER_DIALOG_DISMISS",
    "PLAYWRIGHT_BROWSER_DIALOG_HANDLING",
    "PLAYWRIGHT_BROWSER_DOM_INTERACTION",
    "PLAYWRIGHT_BROWSER_ELEMENT_CLICK",
    "PLAYWRIGHT_BROWSER_ELEMENT_EVALUATE",
    "PLAYWRIGHT_BROWSER_ELEMENT_FILL",
    "PLAYWRIGHT_BROWSER_ELEMENT_PRESS",
    "PLAYWRIGHT_BROWSER_ELEMENT_SCREENSHOT",
    "PLAYWRIGHT_BROWSER_ELEMENT_SELECT_OPTION",
    "PLAYWRIGHT_BROWSER_INTERFACE",
    "PLAYWRIGHT_BROWSER_LAUNCH",
    "PLAYWRIGHT_BROWSER_LIFECYCLE",
    "PLAYWRIGHT_BROWSER_LOCATOR_FILTER",
    "PLAYWRIGHT_BROWSER_LOCATOR_QUERY",
    "PLAYWRIGHT_BROWSER_LOCATOR_RESOLUTION",
    "PLAYWRIGHT_BROWSER_NETWORK_OBSERVATION",
    "PLAYWRIGHT_BROWSER_NETWORK_REQUEST_OBSERVE",
    "PLAYWRIGHT_BROWSER_NETWORK_RESPONSE_OBSERVE",
    "PLAYWRIGHT_BROWSER_OBSERVABLE_PROFILE",
    "PLAYWRIGHT_BROWSER_OBSERVABLE_PROFILE_NAME",
    "PLAYWRIGHT_BROWSER_OBSERVABLE_TIER",
    "PLAYWRIGHT_BROWSER_PAGE_EVALUATE",
    "PLAYWRIGHT_BROWSER_PAGE_GO_BACK",
    "PLAYWRIGHT_BROWSER_PAGE_GOTO",
    "PLAYWRIGHT_BROWSER_PAGE_NAVIGATION",
    "PLAYWRIGHT_BROWSER_PAGE_RELOAD",
    "PLAYWRIGHT_BROWSER_PAGE_SCREENSHOT",
    "PLAYWRIGHT_BROWSER_SCREENSHOT_CAPTURE",
    "PLAYWRIGHT_BROWSER_SCRIPT_EVALUATION",
    "PLAYWRIGHT_BROWSER_WAIT_CONDITIONS",
    "PLAYWRIGHT_BROWSER_WAIT_FOR_RESPONSE",
    "PLAYWRIGHT_BROWSER_WAIT_FOR_SELECTOR",
    "PLAYWRIGHT_BROWSER_WAIT_FOR_URL",
)
