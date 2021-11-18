import contextlib
import re

import dataclasses

from typing import Any, Union, List, cast, Iterable

__all__ = ["YamlinyError", "loads", "dumps"]

_LINE_PATTERN = re.compile(r"^[-_\w]+:")
_KEY_DELIMITER = ":"

_COMMENT_CHAR = "#"


_TerminalValue = Union[str, List[str]]
_Value = Union[List["_Node"], _TerminalValue]


@dataclasses.dataclass(frozen=True)
class _Line:
    line_nr: int
    indent: int
    content: str


@dataclasses.dataclass(frozen=True)
class _Root:
    value: List["_Node"]

    @property
    def is_terminal(self):
        return False


@dataclasses.dataclass(frozen=True)
class _Node:
    key: str
    parent: Union["_Node", _Root]
    value: _Value
    is_terminal: bool
    line: _Line


class YamlinyError(RuntimeError):
    pass


def loads(text: str) -> dict:
    """Parse a string of YAMLiny into a dictionary.

    Args:
        text: A string of YAMLiny.
    Returns:
        A dictionary with the parsed content of the input.
    """
    root = _Root(value=[])
    node: Union[_Node, _Root] = root

    for line in _get_processed_lines(text):
        with _insert_line_number_in_error(line.line_nr):
            node = _line_to_node(line, prev_node=node)

    return _to_dict(root)


def _get_processed_lines(text: str) -> Iterable[_Line]:
    for line_nr, raw_line in enumerate(text.strip().split("\n"), start=1):
        commentless_line = _remove_comments(raw_line)
        if commentless_line == "":
            continue

        indent = _count_indent(commentless_line)
        line = commentless_line.strip()

        if not re.match(_LINE_PATTERN, line):
            raise YamlinyError(f"Line {line_nr}: expected line to start with '<key>:'")

        yield _Line(line_nr=line_nr, indent=indent, content=line)


def _line_to_node(line: _Line, prev_node: Union[_Node, _Root]) -> _Node:
    parent = _search_for_closest_parent_with_lesser_indentation(
        prev_node, target_indent=line.indent
    )
    key, rest = line.content.split(_KEY_DELIMITER)
    value = [] if not rest else _parse_terminal_value(rest)

    node = _Node(key, parent, value, bool(rest), line)
    cast(List[_Node], parent.value).append(node)

    return node


def _search_for_closest_parent_with_lesser_indentation(
    node: Union[_Node, _Root], target_indent: int
) -> Union[_Node, _Root]:
    while not isinstance(node, _Root) and node.line.indent >= target_indent:
        node = node.parent

    if node.is_terminal:
        raise YamlinyError("bad indentation")

    return node


@contextlib.contextmanager
def _insert_line_number_in_error(line_nr: int):
    try:
        yield
    except Exception as exc:
        raise YamlinyError(f"Line {line_nr}: {str(exc)}") from exc


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
    else:  # is List[_Node]
        value = cast(List[_Node], node.value)
        _check_consistent_indent(value)
        return {child.key: _children_to_dict(child) for child in value}


def _check_consistent_indent(value: List[_Node]) -> None:
    if not value:
        return

    nodes: List[_Node] = value

    expected_indent = nodes[0].line.indent
    for node in nodes[1:]:
        if node.line.indent != expected_indent:
            raise YamlinyError(
                f"Line {node.line.line_nr}: bad indentation, "
                f"expected {expected_indent} but was {node.line.indent}"
            )


def _count_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def dumps(obj: dict) -> str:
    """Produce YAMLiny from a dictionary.

    Keys must be strings, but values can be arbitrary objects. Some types are
    treated specially.

    1. Dictionaries can be arbitrarily nested to create nesting in the YAMLiny
    output
    2. Lists are printed as arrays
    3. None is not printed at all

    Args:
        obj: A dictionary to convert to YAMLiny
    Returns:
        A YAMLiny-formatted string
    """
    return "\n".join(_dumps(obj))


def _dumps(obj: dict, indent_level: int = 0) -> List[str]:
    content = []
    indent = " " * indent_level * 2

    for key, value in obj.items():
        if isinstance(value, dict):
            sub_content = _dumps(value, indent_level + 1)
            content.append(f"{indent}{key}:")
            content.extend(sub_content)
        else:
            content.append(f"{indent}{key}: {_value_to_str(value)}")

    return content


def _value_to_str(value: Any) -> str:
    if value is None:
        return ""
    elif isinstance(value, list):
        values = map(_value_to_str, value)
        return f"[{', '.join(values)}]"
    else:
        return str(value)
