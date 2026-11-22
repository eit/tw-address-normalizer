"""Conversion between Chinese numerals and integers, sized for addresses."""

from __future__ import annotations

DIGITS = {
    "零": 0, "〇": 0, "○": 0,
    "一": 1, "壹": 1,
    "二": 2, "兩": 2, "貳": 2,
    "三": 3, "參": 3,
    "四": 4, "肆": 4,
    "五": 5, "伍": 5,
    "六": 6, "陸": 6,
    "七": 7, "柒": 7,
    "八": 8, "捌": 8,
    "九": 9, "玖": 9,
}
UNITS = {"十": 10, "拾": 10, "百": 100, "佰": 100, "千": 1000, "仟": 1000}

# Characters that can appear in a Chinese number, for use in regexes.
CHARS = "".join(DIGITS) + "".join(UNITS)

_SMALL = "零一二三四五六七八九"


def to_int(text: str) -> int:
    """Parse a Chinese numeral such as 十三, 二十, 一百零五 or 二一三.

    A run with no unit characters is read digit by digit (二一三 -> 213),
    which is how house numbers are often written.
    """
    if not text:
        raise ValueError("empty numeral")
    if any(ch not in DIGITS and ch not in UNITS for ch in text):
        raise ValueError(f"not a Chinese numeral: {text!r}")

    if not any(ch in UNITS for ch in text):
        return int("".join(str(DIGITS[ch]) for ch in text))

    total = 0
    digit = None
    for ch in text:
        if ch in DIGITS:
            digit = DIGITS[ch]
        else:
            total += (1 if digit is None else digit) * UNITS[ch]
            digit = None
    if digit is not None:
        total += digit
    return total


def from_int(n: int) -> str:
    """Write 1-9999 the way road sections are written: 1 -> 一, 12 -> 十二, 20 -> 二十."""
    if not 0 < n < 10000:
        raise ValueError(f"out of range: {n}")

    parts = []
    zero_pending = False
    for value, unit in ((1000, "千"), (100, "百"), (10, "十"), (1, "")):
        d, n = divmod(n, value)
        if d:
            if zero_pending:
                parts.append("零")
                zero_pending = False
            parts.append(_SMALL[d] + unit)
        elif parts:
            zero_pending = True
    text = "".join(parts)
    return text[1:] if text.startswith("一十") else text
