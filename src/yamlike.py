import pathlib
import re
import sys

import dataclasses

from typing import Union, List

_LINE_PATTERN = re.compile(r"^\w+:")
_KEY_DELIMITER = ":"


@dataclasses.dataclass(frozen=True)
class Root:
    children: List["Node"]


@dataclasses.dataclass(frozen=True)
class Node:
    key: str
    indent: int
    parent: Union["Node", Root]
    children: List[Union["Node", str]]


def parse(text: str) -> dict:
    root = Root(children=[])
    parent: Union["Node", Root] = root

    for raw_line in text.strip().split("\n"):
        line = _remove_comments(raw_line)
        if not line:
            continue


        indent = count_indent(line)

        while not isinstance(parent, Root) and parent.indent >= indent:
            parent = parent.parent

        key, rest = line.strip().split(_KEY_DELIMITER)
        children = [] if not rest else [rest.strip()]
        node = Node(key, indent, parent, children)
        parent.children.append(node)

        if not children:
            parent = node

    return _to_dict(root)


def _remove_comments(line: str) -> str:
    comment_start_idx = line.find("#")
    if _is_comment_hash_at(line, comment_start_idx):
        return line[:comment_start_idx].rstrip()
    return line

def _is_comment_hash_at(line: str, idx: int) -> bool:
    return idx == 0 or idx > 0 and line[idx - 1].isspace()


def _to_dict(root: Root) -> dict:
    return {node.key: _children_to_dict(node.children) for node in root.children}


def _children_to_dict(children: List[Union[str, Node]]) -> Union[dict, str]:
    first, *_ = children
    if isinstance(first, str):
        return first
    else:
        assert all(isinstance(child, Node) for child in children)
        return {child.key: _children_to_dict(child.children) for child in children}


def count_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


if __name__ == "__main__":
    parse(pathlib.Path("file.yml"))
