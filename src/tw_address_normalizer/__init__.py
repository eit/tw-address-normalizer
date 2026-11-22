"""Normalize Taiwanese postal addresses to one consistent written form."""

from .normalize import normalize, normalize_city, to_halfwidth
from .numerals import from_int, to_int

__all__ = ["normalize", "normalize_city", "to_halfwidth", "to_int", "from_int"]
__version__ = "0.1.0"
