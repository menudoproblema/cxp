from __future__ import annotations

from typing import Any

import msgspec

# --- Core Error Pattern ---

class CxpError(msgspec.Struct, frozen=True):
    """Structured error for machine-readable diagnostics."""
    code: str
    message: str
    retryable: bool
    details: dict[str, Any] = msgspec.field(default_factory=dict)

# --- Common Core Result Patterns ---

class AsyncWorkReport(msgspec.Struct, frozen=True):
    """Generic report for any asynchronous or long-running task."""
    work_id: str
    status: str
    created_at: str
    finished_at: str | None = None
    progress_percent: float | None = None
    error: CxpError | None = None
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)

class ActionResult(msgspec.Struct, frozen=True):
    """Acknowledgement envelope for side-effecting operations."""
    success: bool = True
    confirmed_at: str | None = None
    action_id: str | None = None
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)

# --- Aliases for Domain Specificity ---
RunResult = AsyncWorkReport
TaskStatus = AsyncWorkReport
PrintJobStatus = AsyncWorkReport
TranscodingJob = AsyncWorkReport

# --- Domain Specific Results ---

class DbCursor(msgspec.Struct, frozen=True):
    """Database-native cursor for data retrieval."""
    cursor_id: str
    first_batch: tuple[dict[str, Any], ...]
    has_more: bool

class DbWriteResult(msgspec.Struct, frozen=True):
    acknowledged: bool
    inserted_id: str | None = None
    modified_count: int = 0
    deleted_count: int = 0

class HttpResponse(msgspec.Struct, frozen=True):
    status_code: int
    headers: dict[str, str]
    body_preview: bytes | None = None
    version: str = "1.1"


class TlsCertificate(msgspec.Struct, frozen=True):
    subject: str
    issuer: str
    not_before: str
    not_after: str
    sans: tuple[str, ...] = ()


class HttpPushPromise(msgspec.Struct, frozen=True):
    promised_path: str
    headers: dict[str, str] = msgspec.field(default_factory=dict)


class WebSocketMessage(msgspec.Struct, frozen=True):
    message_type: str
    data: bytes | str
    is_final: bool = True

class BlobMetadata(msgspec.Struct, frozen=True):
    key: str
    size_bytes: int
    content_type: str
    etag: str | None = None


class CacheValue(msgspec.Struct, frozen=True):
    key: str
    value: bytes | None = None
    hit: bool = True
    expires_at: str | None = None

class Message(msgspec.Struct, frozen=True):
    subject: str
    data: bytes
    headers: dict[str, str] = msgspec.field(default_factory=dict)

class MessageAck(msgspec.Struct, frozen=True):
    stream: str | None = None
    sequence: int | None = None
    duplicate: bool = False

class PushResult(msgspec.Struct, frozen=True):
    success: bool
    is_expired: bool = False
    error: CxpError | None = None


class AuthClaims(msgspec.Struct, frozen=True):
    subject: str
    issuer: str | None = None
    audience: tuple[str, ...] = ()
    scopes: tuple[str, ...] = ()
    expires_at: str | None = None


class UserProfile(msgspec.Struct, frozen=True):
    user_id: str
    username: str | None = None
    email: str | None = None
    display_name: str | None = None

class BrowserSession(msgspec.Struct, frozen=True):
    session_id: str
    browser_name: str
    browser_version: str

class PageResponse(msgspec.Struct, frozen=True):
    url: str
    status: int
    title: str | None = None


class MediaManifest(msgspec.Struct, frozen=True):
    url: str
    protocol: str
    expires_at: str | None = None


class LabelMetadata(msgspec.Struct, frozen=True):
    width_mm: float
    height_mm: float
    material: str | None = None
    sensor_type: str | None = None


class SecretValue(msgspec.Struct, frozen=True):
    key: str
    value: str


class ResourceReport(msgspec.Struct, frozen=True):
    cpu_percent: float | None = None
    memory_bytes: int | None = None
    disk_bytes: int | None = None
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)


class RuntimeHealthReport(msgspec.Struct, frozen=True):
    status: str
    is_ready: bool
    checked_at: str
    details: dict[str, Any] = msgspec.field(default_factory=dict)

class PrinterStatus(msgspec.Struct, frozen=True):
    is_online: bool
    toner_levels: dict[str, float] = msgspec.field(default_factory=dict)
    current_errors: tuple[CxpError, ...] = ()


__all__ = (
    "AuthClaims",
    "ActionResult",
    "AsyncWorkReport",
    "BlobMetadata",
    "BrowserSession",
    "CacheValue",
    "CxpError",
    "DbCursor",
    "DbWriteResult",
    "HttpPushPromise",
    "HttpResponse",
    "LabelMetadata",
    "MediaManifest",
    "Message",
    "MessageAck",
    "PageResponse",
    "PrintJobStatus",
    "PrinterStatus",
    "PushResult",
    "ResourceReport",
    "RuntimeHealthReport",
    "RunResult",
    "SecretValue",
    "TaskStatus",
    "TlsCertificate",
    "TranscodingJob",
    "UserProfile",
    "WebSocketMessage",
)
