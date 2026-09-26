"""CXP package identity and neutral validation diagnostics."""

from cxp._version import __version__, version_info
from cxp.validation import ContractValidationError, ValidationIssue

__all__ = (
    "ContractValidationError",
    "ValidationIssue",
    "__version__",
    "version_info",
)
