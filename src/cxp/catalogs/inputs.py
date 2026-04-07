from __future__ import annotations

from typing import Any
import msgspec

# --- Shared Technical Request Patterns ---

class HttpDispatch(msgspec.Struct, frozen=True):
    """Technical definition of an HTTP request at the transport layer."""
    method: str
    url: str
    headers: dict[str, str] = msgspec.field(default_factory=dict)
    body: bytes | None = None
    timeout_ms: int = 30000

class DbQueryInput(msgspec.Struct, frozen=True):
    """Standard envelope for data queries."""
    statement: str
    params: dict[str, Any] = msgspec.field(default_factory=dict)
