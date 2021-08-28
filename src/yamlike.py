import pathlib
import re
import sys

import dataclasses

from typing import Union, List, Optional

_LINE_PATTERN = re.compile(r"^\w+:")
_KEY_DELIMITER = ":"

COMMENT_CHAR = "#"


@dataclasses.dataclass(frozen=True)
class Root:
    children: List["Node"]


@dataclasses.dataclass(frozen=True)
class Node:
    key: str
    indent: int
    parent: Union["Node", Root]
    children: List[Union["Node", str]]
    line_nr: int


class YamlikeError(RuntimeError):
    pass


def parse(text: str) -> dict:
    root = Root(children=[])
    parent: Union["Node", Root] = root

    for line_nr, raw_line in enumerate(text.strip().split("\n"), start=1):
        line = _remove_comments(raw_line)
        if not line:
            continue

        indent = count_indent(line)

        while not isinstance(parent, Root) and parent.indent >= indent:
            parent = parent.parent

        key, rest = line.strip().split(_KEY_DELIMITER)
        children = [] if not rest else [rest.strip()]
        node = Node(key, indent, parent, children, line_nr)
        parent.children.append(node)

        if not children:
            parent = node

    return _to_dict(root)


def _remove_comments(line: str) -> str:
    comment_start_idx = line.find(COMMENT_CHAR)
    if _is_comment_hash_at(line, comment_start_idx):
        return line[:comment_start_idx].rstrip()
    return line


def _is_comment_hash_at(line: str, idx: int) -> bool:
    return idx == 0 or idx > 0 and line[idx - 1].isspace()


def _to_dict(root: Root) -> dict:
    return {node.key: _children_to_dict(node.children) for node in root.children}


def _children_to_dict(children: List[Union[str, Node]]) -> Union[dict, str]:
    _check_consistent_indent([child for child in children if isinstance(child, Node)])
    first, *_ = children
    if isinstance(first, str):
        return first
    else:
        assert all(isinstance(child, Node) for child in children)
        return {child.key: _children_to_dict(child.children) for child in children}


def _check_consistent_indent(nodes: List[Node]) -> None:
    if not nodes:
        return

    expected_indent = nodes[0].indent
    for node in nodes[1:]:
        if node.indent != expected_indent:
            raise YamlikeError(
                f"Line {node.line_nr}: bad indentation, "
                f"expected {expected_indent} "
                f"but was {node.indent}"
            )


def count_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


if __name__ == "__main__":
    parse(pathlib.Path("file.yml"))
