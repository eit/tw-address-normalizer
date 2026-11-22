"""Normalize addresses line by line: python -m tw_address_normalizer < in.txt > out.txt"""

import sys

from . import normalize


def main() -> None:
    for line in sys.stdin:
        line = line.rstrip("\n")
        print(normalize(line) if line.strip() else line)


if __name__ == "__main__":
    main()
