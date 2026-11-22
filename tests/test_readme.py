"""Keep the examples table in README.md in sync with the code."""

import re
from pathlib import Path

import pytest

from tw_address_normalizer import normalize

README = Path(__file__).resolve().parent.parent / "README.md"
ROWS = re.findall(r"^\| `([^`]*)` \| `([^`]*)` \| [^|]+ \|$", README.read_text("utf-8"), re.M)


def test_table_found():
    assert len(ROWS) >= 10


@pytest.mark.parametrize("raw, want", ROWS)
def test_readme_example(raw, want):
    assert normalize(raw) == want
