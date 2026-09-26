from __future__ import annotations

import msgspec

from cxp._legacy import warn_legacy_import

warn_legacy_import(__name__)


type Version = str
type Interface = str
type Provider = str


class ComponentIdentity(msgspec.Struct, frozen=True):
    interface: Interface
    provider: Provider
    version: Version
