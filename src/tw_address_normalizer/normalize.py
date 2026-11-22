"""Rules that bring Taiwanese addresses to one consistent written form.

The target follows Chunghwa Post's conventions:

* 臺 rather than 台 in county and city names
* counties that became special municipalities use their current names
  (臺北縣板橋市 -> 新北市板橋區)
* road sections in Chinese numerals (二段); lanes, alleys, numbers and
  floors in Arabic numerals (13巷5弄7號3樓)
* 之 rather than a hyphen, 樓 rather than F, B2 for basement floors
"""

from __future__ import annotations

import re
import unicodedata

from . import numerals

_NUM = f"[{numerals.CHARS}]+"
_ROAD = "(?:大道|路|街)"

# Counties merged into special municipalities (2010 and 2014). All of their
# townships (鄉, 鎮, 縣轄市) became districts (區).
_MERGED_COUNTIES = {
    "臺北縣": "新北市",
    "桃園縣": "桃園市",
    "臺中縣": "臺中市",
    "臺南縣": "臺南市",
    "高雄縣": "高雄市",
}

_TYPOS = str.maketrans({
    "巿": "市",  # U+5DFF, looks like 市
    "鎭": "鎮",
    "内": "內",  # U+5185, the simplified-style form
})

_DASHES = re.compile("[-‐‑‒–—―−]")


def to_halfwidth(text: str) -> str:
    """Convert full-width ASCII (１２３ＡＢＣ－) and ideographic spaces to half-width."""
    out = []
    for ch in text:
        code = ord(ch)
        if code == 0x3000:
            out.append(" ")
        elif 0xFF01 <= code <= 0xFF5E:
            out.append(chr(code - 0xFEE0))
        else:
            out.append(ch)
    return "".join(out)


def _sub_number(pattern: str, text: str) -> str:
    """Replace the Chinese numeral captured as group 'n' with Arabic digits."""

    def repl(m: re.Match) -> str:
        start, end = m.span("n")
        start -= m.start()
        end -= m.start()
        whole = m.group(0)
        return whole[:start] + str(numerals.to_int(m.group("n"))) + whole[end:]

    return re.sub(pattern, repl, text)


def normalize_city(address: str) -> str:
    """Fix the county/city prefix: 台 -> 臺 and pre-merger county names."""
    m = re.match(r"(\d{3,6})?(?:中華民國|[臺台]灣省?)*", address)
    postcode = m.group(1) or ""
    rest = address[m.end():]

    rest = re.sub(r"^台(?=[北中南東][市縣])", "臺", rest)

    for old, new in _MERGED_COUNTIES.items():
        if rest.startswith(old):
            rest = rest[len(old):]
            rest = re.sub(r"^([^\d\s]{1,3}?)[鄉鎮市]", r"\1區", rest, count=1)
            rest = new + rest
            break

    return postcode + rest


def normalize(address: str) -> str:
    """Return address in a consistent form. Unrecognised parts are left alone.

    >>> normalize("台北縣板橋市文化路１段１００巷五弄十三-一號三F")
    '新北市板橋區文化路一段100巷5弄13之1號3樓'
    """
    s = to_halfwidth(unicodedata.normalize("NFC", address))
    s = re.sub(r"\s+", "", s)
    s = s.translate(_TYPOS)
    s = _DASHES.sub("之", s)
    s = normalize_city(s)

    # Road sections use Chinese numerals: 2段 -> 二段
    s = re.sub(
        rf"({_ROAD})(\d+)段",
        lambda m: m.group(1) + numerals.from_int(int(m.group(2))) + "段",
        s,
    )

    # Lanes, alleys and house numbers use Arabic numerals. Each needs the unit
    # before it, so names such as 五權新一巷 are not touched.
    s = _sub_number(rf"(?:{_ROAD}|段)(?P<n>{_NUM})巷", s)
    s = _sub_number(rf"巷(?P<n>{_NUM})[弄衖]", s)
    s = _sub_number(rf"(?:{_ROAD}|段|巷|弄|衖)(?P<n>{_NUM})(?=(?:之\w+?)?號)", s)

    # Floors, only after the house number so place names are safe.
    if "號" in s:
        head, _, tail = s.partition("號")
        tail = _sub_number(rf"(?P<n>{_NUM})(?=[FfＦ樓層])", tail)
        tail = re.sub(r"(?<![A-Za-z])[Bb](\d+)[Ff]", r"B\1", tail)
        tail = re.sub(r"(\d+)[Ff](?![A-Za-z])", r"\1樓", tail)
        tail = re.sub(r"地下(\d+)[樓層]", r"B\1", tail)
        s = head + "號" + tail

    # 之 numbers (5之一號, 3樓之二) last, once floors are written as 樓.
    # Repeat because chains such as 5之三之一 overlap.
    while True:
        t = _sub_number(rf"(?:\d|巷|弄|衖|號|樓)之(?P<n>{_NUM})", s)
        if t == s:
            return s
        s = t
