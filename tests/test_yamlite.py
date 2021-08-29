import pathlib

import pytest
import yaml

import yamlite

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


@pytest.mark.parametrize("input_file", _find_valid_inputs())
def test_parses_valid_input_like_pyyaml(input_file: pathlib.Path):
    raw = input_file.read_text(encoding=ENCODING)

    yamlited = yamlite.loads(raw)
    pyyamled = yaml.load(raw, Loader=yaml.SafeLoader)

    assert yamlited == pyyamled


def _find_invalid_inputs():
    return [
        file
        for file in INVALID_INPUTS.iterdir()
        if file.is_file() and file.suffix == ".yml"
    ]


@pytest.mark.parametrize("input_file", _find_invalid_inputs())
def test_raises_on_invalid_input(input_file: pathlib.Path):
    raw = input_file.read_text(encoding=ENCODING)
    first_line, *_ = raw.split("\n")
    expected_error_msg = _parse_expected_error_message(first_line)

    with pytest.raises(yamlite.YamliteError) as exc_info:
        yamlite.loads(raw)

    assert expected_error_msg in str(exc_info.value)


def _parse_expected_error_message(line: str) -> str:
    return line[line.index(yamlite._COMMENT_CHAR) + 1 :].strip()
