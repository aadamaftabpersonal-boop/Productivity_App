from tree_sitter import Parser
import tree_sitter_language_pack

LANG_MAP = {
    "python": "python",
    "cpp": "cpp",
    "c++": "cpp",
    "java": "java",
}

LOOP_NODES = {
    "python": {"for_statement", "while_statement"},
    "cpp": {"for_statement", "while_statement", "do_statement"},
    "java": {"for_statement", "while_statement", "do_statement"},
}

FUNC_NODES = {
    "python": {"function_definition"},
    "cpp": {"function_definition"},
    "java": {"method_declaration"},
}


def analyze_structure(code: str, language: str) -> dict:
    lang_key = LANG_MAP.get(language.lower())
    if lang_key is None:
        raise ValueError(f"Unsupported language: {language}")

    # --- MODERN API UPDATE START ---
    # Fetch the compiled language pack object
    language_pack = tree_sitter_language_pack.get_language(lang_key)
    # Correctly initialize the modern Parser passing 1 argument
    parser = Parser(language_pack)
    # --- MODERN API UPDATE END ---

    tree = parser.parse(bytes(code, "utf8"))
    root = tree.root_node

    loop_nodes = LOOP_NODES[lang_key]
    func_nodes = FUNC_NODES[lang_key]

    max_loop_depth = _max_nested_depth(root, loop_nodes)
    function_names = _collect_function_names(root, func_nodes, code)
    is_recursive = _detect_recursion(root, func_nodes, code)
    identifiers = _collect_identifiers(root, code)
    ds_hints = _detect_data_structures(identifiers, language)

    return {
        "max_loop_nesting_depth": max_loop_depth,
        "function_count": len(function_names),
        "function_names": function_names,
        "likely_recursive": is_recursive,
        "data_structure_hints": ds_hints,
        "node_count": root.descendant_count,
        "has_syntax_errors": root.has_error,
    }


def _max_nested_depth(node, target_types: set, current_depth: int = 0) -> int:
    depth_here = current_depth + 1 if node.type in target_types else current_depth
    if not node.children:
        return depth_here
    return max(_max_nested_depth(c, target_types, depth_here) for c in node.children)


def _collect_function_names(node, func_types: set, code: str) -> list[str]:
    names = []
    if node.type in func_types:
        for child in node.children:
            if child.type in ("identifier",):
                names.append(code[child.start_byte:child.end_byte])
                break
    for child in node.children:
        names.extend(_collect_function_names(child, func_types, code))
    return names


def _detect_recursion(node, func_types: set, code: str) -> bool:
    """Naive but effective: for each function, check if its own name appears
    as a call inside its body."""
    funcs = []

    def collect(n):
        if n.type in func_types:
            funcs.append(n)
        for c in n.children:
            collect(c)

    collect(node)

    for fn in funcs:
        name_node = next((c for c in fn.children if c.type == "identifier"), None)
        if not name_node:
            continue
        fname = code[name_node.start_byte:name_node.end_byte]
        body_text = code[fn.start_byte:fn.end_byte]
        # crude but reliable enough: name appears more than once (decl + call)
        if body_text.count(fname) > 1:
            return True
    return False


def _collect_identifiers(node, code: str) -> list[str]:
    ids = []
    if node.type == "identifier":
        ids.append(code[node.start_byte:node.end_byte])
    for c in node.children:
        ids.extend(_collect_identifiers(c, code))
    return ids


def _detect_data_structures(identifiers: list[str], language: str) -> list[str]:
    hints = set()
    lower_ids = [i.lower() for i in identifiers]
    joined = " ".join(lower_ids)

    patterns = {
        "hash_map": ["map", "unordered_map", "dict", "hashmap"],
        "set": ["set", "unordered_set", "hashset"],
        "stack": ["stack"],
        "queue": ["queue", "deque"],
        "heap_priority_queue": ["priority_queue", "heapq", "heap"],
        "vector_array_list": ["vector", "arraylist", "list"],
        "graph": ["graph", "adjacency", "adj"],
        "tree": ["treenode", "node", "root"],
    }
    for label, keywords in patterns.items():
        if any(kw in joined for kw in keywords):
            hints.add(label)
    return sorted(hints)