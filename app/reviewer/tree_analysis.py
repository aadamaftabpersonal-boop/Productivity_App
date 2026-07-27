from tree_sitter import Parser, Node
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

    language_pack = tree_sitter_language_pack.get_language(lang_key)
    parser = Parser(language_pack)

    tree = parser.parse(bytes(code, "utf8"))
    root = tree.root_node

    loop_nodes = LOOP_NODES[lang_key]
    func_nodes = FUNC_NODES[lang_key]

    max_loop_depth = _max_nested_depth(root, loop_nodes)
    function_names = _collect_function_names(root, func_nodes, code, lang_key)
    is_recursive = _detect_recursion(root, func_nodes, code, lang_key)
    ds_hints = _detect_data_structures(root, lang_key, code)

    return {
        "max_loop_nesting_depth": max_loop_depth,
        "function_count": len(function_names),
        "function_names": function_names,
        "likely_recursive": is_recursive,
        "data_structure_hints": ds_hints,
        "node_count": root.descendant_count,
        "has_syntax_errors": root.has_error,
    }


def _max_nested_depth(node: Node, target_types: set, current_depth: int = 0) -> int:
    depth_here = current_depth + 1 if node.type in target_types else current_depth
    if not node.children:
        return depth_here
    return max(_max_nested_depth(c, target_types, depth_here) for c in node.children)


def _get_func_name(fn_node: Node, code: str, lang_key: str) -> str | None:
    """Extract declared function/method name identifier node."""
    if lang_key == "python":
        name_node = fn_node.child_by_field_name("name")
        if name_node and name_node.type == "identifier":
            return code[name_node.start_byte:name_node.end_byte]
    elif lang_key == "cpp":
        declarator = fn_node.child_by_field_name("declarator")
        if declarator:
            curr = declarator
            while curr:
                if curr.type in ("identifier", "field_identifier"):
                    return code[curr.start_byte:curr.end_byte]
                child_decl = curr.child_by_field_name("declarator")
                if child_decl:
                    curr = child_decl
                else:
                    id_child = next((c for c in curr.children if c.type in ("identifier", "field_identifier")), None)
                    if id_child:
                        return code[id_child.start_byte:id_child.end_byte]
                    break
    elif lang_key == "java":
        name_node = fn_node.child_by_field_name("name")
        if name_node and name_node.type == "identifier":
            return code[name_node.start_byte:name_node.end_byte]
    return None


def _collect_function_names(node: Node, func_types: set, code: str, lang_key: str) -> list[str]:
    names = []
    if node.type in func_types:
        fn_name = _get_func_name(node, code, lang_key)
        if fn_name:
            names.append(fn_name)
    for child in node.children:
        names.extend(_collect_function_names(child, func_types, code, lang_key))
    return names


def _detect_recursion(root: Node, func_types: set, code: str, lang_key: str) -> bool:
    """Scope-aware AST call-graph recursion detection.
    Finds function definition nodes, extracts their declared name,
    and checks if any call expression inside the function body calls that exact function identifier.
    """
    funcs = []

    def collect_funcs(n: Node):
        if n.type in func_types:
            funcs.append(n)
        for c in n.children:
            collect_funcs(c)

    collect_funcs(root)

    call_node_types = {
        "python": {"call"},
        "cpp": {"call_expression"},
        "java": {"method_invocation"},
    }.get(lang_key, set())

    for fn in funcs:
        fname = _get_func_name(fn, code, lang_key)
        if not fname:
            continue

        body = fn.child_by_field_name("body") or fn
        found_recursive_call = False

        def check_calls(n: Node):
            nonlocal found_recursive_call
            if found_recursive_call:
                return
            if n.type in call_node_types:
                callee_name = None
                if lang_key == "python":
                    fn_child = n.child_by_field_name("function")
                    if fn_child and fn_child.type == "identifier":
                        callee_name = code[fn_child.start_byte:fn_child.end_byte]
                elif lang_key == "cpp":
                    fn_child = n.child_by_field_name("function")
                    if fn_child:
                        if fn_child.type in ("identifier", "field_identifier"):
                            callee_name = code[fn_child.start_byte:fn_child.end_byte]
                        elif fn_child.type == "field_expression":
                            field = fn_child.child_by_field_name("field")
                            if field:
                                callee_name = code[field.start_byte:field.end_byte]
                elif lang_key == "java":
                    name_child = n.child_by_field_name("name")
                    if name_child and name_child.type == "identifier":
                        callee_name = code[name_child.start_byte:name_child.end_byte]

                if callee_name == fname:
                    found_recursive_call = True
                    return

            for c in n.children:
                check_calls(c)

        check_calls(body)
        if found_recursive_call:
            return True

    return False


def _detect_data_structures(root: Node, lang_key: str, code: str) -> list[str]:
    """Inspect AST type declarations, template types, constructor calls, and literals,
    ignoring simple decoy variable identifiers like `mapValue`."""
    hints = set()

    def walk(node: Node):
        ntype = node.type
        text = code[node.start_byte:node.end_byte]

        if lang_key == "python":
            if ntype == "dictionary":
                hints.add("hash_map")
            elif ntype == "set":
                hints.add("set")
            elif ntype == "list":
                hints.add("vector_array_list")
            elif ntype == "call":
                fn_child = node.child_by_field_name("function")
                if fn_child:
                    call_name = code[fn_child.start_byte:fn_child.end_byte]
                    if call_name in ("dict", "defaultdict", "Counter"):
                        hints.add("hash_map")
                    elif call_name == "set":
                        hints.add("set")
                    elif call_name == "list":
                        hints.add("vector_array_list")
                    elif call_name == "deque":
                        hints.add("queue")
                    elif "heapq" in call_name:
                        hints.add("heap_priority_queue")
            elif ntype == "type":
                if "dict" in text.lower():
                    hints.add("hash_map")
                elif "set" in text.lower():
                    hints.add("set")
                elif "list" in text.lower():
                    hints.add("vector_array_list")

        elif lang_key == "cpp":
            if ntype in ("template_type", "type_identifier", "scoped_identifier", "namespace_identifier"):
                text_clean = text.replace("std::", "").strip()
                if text_clean.startswith("unordered_map") or text_clean.startswith("map"):
                    hints.add("hash_map")
                elif text_clean.startswith("unordered_set") or text_clean.startswith("set"):
                    hints.add("set")
                elif text_clean.startswith("stack"):
                    hints.add("stack")
                elif text_clean.startswith("queue") or text_clean.startswith("deque"):
                    hints.add("queue")
                elif text_clean.startswith("priority_queue"):
                    hints.add("heap_priority_queue")
                elif text_clean.startswith("vector"):
                    hints.add("vector_array_list")

        elif lang_key == "java":
            if ntype in ("generic_type", "type_identifier", "scoped_type_identifier"):
                if any(k in text for k in ("HashMap", "Map", "TreeMap", "LinkedHashMap")):
                    hints.add("hash_map")
                elif any(k in text for k in ("HashSet", "Set", "TreeSet")):
                    hints.add("set")
                elif any(k in text for k in ("Stack",)):
                    hints.add("stack")
                elif any(k in text for k in ("Queue", "ArrayDeque", "LinkedList")):
                    hints.add("queue")
                elif any(k in text for k in ("PriorityQueue",)):
                    hints.add("heap_priority_queue")
                elif any(k in text for k in ("ArrayList", "List", "Vector")):
                    hints.add("vector_array_list")

        if ntype in ("class_definition", "class_specifier", "struct_specifier", "class_declaration"):
            text_lower = text.lower()
            if "treenode" in text_lower or "tree_node" in text_lower:
                hints.add("tree")
            if "graph" in text_lower or "adj" in text_lower:
                hints.add("graph")

        for child in node.children:
            walk(child)

    walk(root)
    return sorted(hints)