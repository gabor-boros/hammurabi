import random
import re

from hypothesis import given
from hypothesis import strategies as st

from hammurabi.helpers import full_strip

WHITESPACE_PATTERN = re.compile(r"\s+.*(\s+)?")


def get_whitespace():
    return random.choice(["", " ", "\t", "\n", "\n\t"])

@given(st.text())
def test_full_strip_one_line(value):
    test_input = f"{get_whitespace()}{value}{get_whitespace()}"

    result = full_strip(test_input)

    assert not WHITESPACE_PATTERN.match(result)

@given(st.lists(st.text()))
def test_full_strip_multiple_lines(value):
    test_input = "\n".join([
        f"{get_whitespace()}{''.join(value)}{get_whitespace()}",
        f"{get_whitespace()}{''.join(value)}{get_whitespace()}",
        f"{get_whitespace()}{''.join(value)}{get_whitespace()}",
        f"{get_whitespace()}{''.join(value)}{get_whitespace()}"
    ])

    result = full_strip(test_input)

    assert not WHITESPACE_PATTERN.match(result)
