""" Backward-compatible re-export of :class:`ButtonLayout`
(now defined at the package root to avoid an import cycle between ``config`` and the ``pages`` package).
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

from ..button_layout import ButtonLayout, Position

__all__ = ["ButtonLayout", "Position"]

