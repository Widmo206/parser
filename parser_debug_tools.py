"""Basic tools to make working on the parser easier

Created on 2026.04.22
Contributors:
    Widmo
"""


from parser import ProcessNode, ProcessTree


def _sanitize_node(node: ProcessNode) -> str:
    return f"{node.get_type()}, {node._value}"


def _make_process_branch(node: ProcessNode, indent_level: int=0) -> str:
    result = indent_level*"|" + _sanitize_node(node) + "\n"
    for child in node.get_children():
        result += _make_process_branch(child, indent_level+1)
    return result


def make_process_tree(tree: ProcessTree) -> str:
    return _make_process_branch(tree.get_root())
