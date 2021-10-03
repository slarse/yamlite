import pathlib
from typing import List

import pytest
import yaml

import yamliny

from yamliny._yamliny import _COMMENT_CHAR

RESOURCES = pathlib.Path(__file__).parent / "resources"
VALID_INPUTS = RESOURCES / "valid"
INVALID_INPUTS = RESOURCES / "invalid"
ENCODING = "utf8"


def _find_valid_inputs():
    return [
        file
        for file in VALID_INPUTS.iterdir()
        if file.is_file() and file.suffix == ".yml"
    ]


def _get_file_ids(files):
    return [file.name for file in files]


@pytest.mark.parametrize(
    "input_file", _find_valid_inputs(), ids=_get_file_ids(_find_valid_inputs())
)
def test_parses_valid_input_like_pyyaml(input_file: pathlib.Path):
    raw = input_file.read_text(encoding=ENCODING)

    yamlined = yamliny.loads(raw)
    pyyamled = yaml.load(raw, Loader=yaml.SafeLoader)

    assert yamlined == pyyamled


def _find_invalid_inputs():
    return [
        file
        for file in INVALID_INPUTS.iterdir()
        if file.is_file() and file.suffix == ".yml"
    ]

@pytest.mark.parametrize(
    "input_file", _find_valid_inputs(), ids=_get_file_ids(_find_valid_inputs())
)
def test_loads_dumps_roundtrip_for_valid_input(input_file):
    raw = input_file.read_text(encoding=ENCODING)

    yamlined = yamliny.loads(raw)
    dumped = yamliny.dumps(yamlined)
    yamlined_again = yamliny.loads(dumped)

    assert yamlined == yamlined_again

@pytest.mark.parametrize(
    "input_file", _find_invalid_inputs(), ids=_get_file_ids(_find_invalid_inputs())
)
def test_raises_on_invalid_input(input_file: pathlib.Path):
    raw = input_file.read_text(encoding=ENCODING)
    first_line, *_ = raw.split("\n")
    expected_error_msg = _parse_expected_error_message(first_line)

    with pytest.raises(yamliny.YamlinyError) as exc_info:
        yamliny.loads(raw)

    assert expected_error_msg in str(exc_info.value)


def _parse_expected_error_message(line: str) -> str:
    return line[line.index(_COMMENT_CHAR) + 1 :].strip()
