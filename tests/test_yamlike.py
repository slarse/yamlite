import pathlib

import pytest
import yaml

import yamlike

RESOURCES = pathlib.Path(__file__).parent / "resources"
VALID_INPUTS = RESOURCES / "valid"
ENCODING = "utf8"


def _find_valid_inputs():
    return [
        file
        for file in VALID_INPUTS.iterdir()
        if file.is_file() and file.suffix == ".yml"
    ]


@pytest.mark.parametrize("input_file", _find_valid_inputs())
def test_parses_valid_input_like_pyyaml(input_file: pathlib.Path):
    raw = input_file.read_text(encoding=ENCODING)

    yamliked = yamlike.parse(raw)
    pyyamled = yaml.load(raw, Loader=yaml.SafeLoader)

    assert yamliked == pyyamled
