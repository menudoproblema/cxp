from __future__ import annotations

import msgspec

type Version = str
type Interface = str
type Provider = str

class ComponentIdentity(msgspec.Struct, frozen=True):
    interface: Interface
    provider: Provider
    version: Version
