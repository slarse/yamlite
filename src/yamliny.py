import contextlib
import pathlib
import re
import sys

import dataclasses

from typing import Union, List, Optional, cast

__all__ = ["YamlinyError", "loads"]

_LINE_PATTERN = re.compile(r"^[-_\w]+:")
_KEY_DELIMITER = ":"

_COMMENT_CHAR = "#"


_TerminalValue = Union[str, List[str]]
_Value = Union[List["_Node"], _TerminalValue]


@dataclasses.dataclass(frozen=True)
class _Root:
    value: List["_Node"]

    @property
    def is_terminal(self):
        return False


@dataclasses.dataclass(frozen=True)
class _Node:
    key: str
    indent: int
    parent: Union["_Node", _Root]
    value: _Value
    line_nr: int
    is_terminal: bool


class YamlinyError(RuntimeError):
    pass


def loads(text: str) -> dict:
    root = _Root(value=[])
    parent: Union[_Node, _Root] = root

    for line_nr, raw_line in enumerate(text.strip().split("\n"), start=1):
        with _insert_line_number_in_error(line_nr):
            line = _remove_comments(raw_line)
            if not line:
                continue
            stripped = line.strip()
            _check_line_syntax(stripped)

            indent = _count_indent(line)

            while not isinstance(parent, _Root) and parent.indent >= indent:
                parent = parent.parent

            if parent.is_terminal:
                raise YamlinyError("bad indentation")
            
            key, rest = stripped.split(_KEY_DELIMITER)
            value: _Value = [] if not rest else _parse_terminal_value(rest)
            node = _Node(key, indent, parent, value, line_nr, not not rest)

            assert isinstance(parent.value, list)
            cast(List[_Node], parent.value).append(node)

            parent = node

    return _to_dict(root)


@contextlib.contextmanager
def _insert_line_number_in_error(line_nr: int):
    try:
        yield
    except Exception as exc:
        raise YamlinyError(f"Line {line_nr}: {str(exc)}") from exc


def _check_line_syntax(line: str) -> None:
    if not re.match(_LINE_PATTERN, line):
        raise YamlinyError("expected line to start with '<key>:'")


def _remove_comments(line: str) -> str:
    comment_start_idx = line.find(_COMMENT_CHAR)
    if _is_comment_hash_at(line, comment_start_idx):
        return line[:comment_start_idx].rstrip()
    return line


def _is_comment_hash_at(line: str, idx: int) -> bool:
    return idx == 0 or idx > 0 and line[idx - 1].isspace()


def _parse_terminal_value(raw_value: str) -> Union[str, List[str]]:
    stripped = raw_value.strip()
    return _parse_array(stripped) if stripped.startswith("[") else stripped


def _parse_array(stripped: str) -> List[str]:
    if not stripped.endswith("]"):
        raise YamlinyError(f"array must start and end on same line")
    return [value.strip() for value in stripped[1:-1].split(",")]


def _to_dict(root: _Root) -> dict:
    return {node.key: _children_to_dict(node) for node in root.value}


def _children_to_dict(node: _Node) -> Union[_TerminalValue, dict, None]:
    if not node.value:
        return None

    if node.is_terminal:
        return cast(_TerminalValue, node.value)
    else: # is List[_Node]
        value = cast(List[_Node], node.value)
        _check_consistent_indent(value)
        return {child.key: _children_to_dict(child) for child in value}


def _check_consistent_indent(value: List[_Node]) -> None:
    if not value:
        return

    nodes: List[_Node] = value

    expected_indent = nodes[0].indent
    for node in nodes[1:]:
        if node.indent != expected_indent:
            raise YamlinyError(
                f"Line {node.line_nr}: bad indentation, "
                f"expected {expected_indent} but was {node.indent}"
            )


def _count_indent(line: str) -> int:
    return len(line) - len(line.lstrip())
