# analyzer.py
# Code Lantern – Architecture Diagram Analyzer (Enhanced)
# --------------------------------------------------------
# Uses Tree-sitter for accurate AST-based code analysis.
# Extracts:
# - files in repo
# - imports (JS/Python/Java/C++/Rust)
# - function names, parameters, return types
# - cyclomatic complexity (AST-based)
# - function code blocks

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from tree_sitter import Parser, Node, Language
import tree_sitter_javascript
import tree_sitter_python
import tree_sitter_java
import tree_sitter_cpp
import tree_sitter_rust

# Set up parser globally
parser = Parser()

# Directories to ignore during analysis
IGNORED_DIRECTORIES = {
    '.git', '.svn', '.hg',
    'node_modules', 'bower_components', '.npm', '.yarn',
    'venv', '.venv', 'env', '.env', 'virtualenv',
    '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    'site-packages', '.eggs',
    'dist', 'build', 'out', 'output', 'target', 'bin', 'obj',
    '.next', '.nuxt', '.output', '.cache', '.parcel-cache',
    '.vscode', '.idea', '.vs', '.eclipse',
    'vendor', 'packages', 'libs', 'lib', 'third_party', 'external',
    'coverage', '.coverage', 'htmlcov', '.tox',
    'tmp', 'temp', 'logs',
    'assets', 'static', 'public', 'media', 'uploads',
}

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.jsx': 'javascript',
    '.java': 'java',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.h': 'cpp',
    '.hpp': 'cpp',
    '.rs': 'rust'
}

# Control flow node types that increase cyclomatic complexity
COMPLEXITY_NODE_TYPES = {
    # Python
    'if_statement', 'elif_clause', 'for_statement', 'while_statement',
    'try_statement', 'except_clause', 'with_statement',
    'conditional_expression',  # ternary
    'boolean_operator',  # and/or
    'list_comprehension', 'dictionary_comprehension', 'set_comprehension',
    'generator_expression',
    # JavaScript/TypeScript
    'if_statement', 'for_statement', 'for_in_statement', 'while_statement',
    'do_statement', 'switch_case', 'catch_clause', 'ternary_expression',
    'binary_expression',  # will filter for && and ||
    # Java
    'if_statement', 'for_statement', 'enhanced_for_statement', 'while_statement',
    'do_statement', 'catch_clause', 'switch_expression',
    # C++
    'if_statement', 'for_statement', 'while_statement', 'do_statement',
    'catch_clause', 'case_statement',
    # Rust
    'if_expression', 'for_expression', 'while_expression', 'loop_expression',
    'match_arm',
}


# -------------------------------
# Utils
# -------------------------------

def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except:
        return ""


def detect_language(path: str) -> Optional[str]:
    ext = os.path.splitext(path)[1].lower()
    if ext in [".js", ".jsx", ".ts", ".tsx"]:
        return "js"
    if ext in [".py"]:
        return "py"
    if ext in [".java"]:
        return "java"
    if ext in [".cpp", ".cc", ".cxx", ".h", ".hpp"]:
        return "cpp"
    if ext in [".rs"]:
        return "rust"
    return None


def get_language_for_parser(lang: str):
    """Get the tree-sitter Language object using the new v0.25 API"""
    lang_capsules = {
        "js": tree_sitter_javascript.language(),
        "py": tree_sitter_python.language(),
        "java": tree_sitter_java.language(),
        "cpp": tree_sitter_cpp.language(),
        "rust": tree_sitter_rust.language(),
    }
    capsule = lang_capsules.get(lang)
    if capsule:
        return Language(capsule)
    return None


def get_node_text(node: Node, code: str) -> str:
    """Extract text from a tree-sitter node"""
    return code[node.start_byte:node.end_byte]


# -------------------------------
# Cyclomatic Complexity Calculator
# -------------------------------

def calculate_complexity(node: Node, code: str, lang: str) -> int:
    """
    Calculate cyclomatic complexity using AST traversal.
    More accurate than regex as it understands code structure.
    """
    complexity = 1  # Base complexity

    def walk(n: Node):
        nonlocal complexity

        # Check if this node type increases complexity
        if n.type in COMPLEXITY_NODE_TYPES:
            # For binary expressions, only count && and ||
            if n.type == 'binary_expression':
                operator_node = None
                for child in n.children:
                    if child.type in ['&&', '||', 'and', 'or']:
                        complexity += 1
                        break
                    # Also check for operator text
                    text = get_node_text(child, code)
                    if text in ['&&', '||', 'and', 'or']:
                        complexity += 1
                        break
            elif n.type == 'boolean_operator':
                # Python's and/or
                complexity += 1
            else:
                complexity += 1

        for child in n.children:
            walk(child)

    walk(node)
    return complexity


# -------------------------------
# Function Detail Extractor
# -------------------------------

def extract_function_details(node: Node, code: str, lang: str, file_path: str) -> Dict[str, Any]:
    """
    Extract detailed function information from a function AST node.
    Returns: functionName, parameters, returns, complexity, startLine, endLine, code
    """
    func_name = ""
    parameters = []
    return_type = None
    
    # Extract function name and parameters based on language
    if lang == "py":
        # Python: function_definition -> name, parameters, return_type
        for child in node.children:
            if child.type == "identifier":
                func_name = get_node_text(child, code)
            elif child.type == "parameters":
                # Extract individual parameters
                for param in child.children:
                    if param.type in ["identifier", "typed_parameter", "default_parameter"]:
                        param_text = get_node_text(param, code)
                        # Clean up typed parameters
                        if ":" in param_text:
                            param_name = param_text.split(":")[0].strip()
                            param_type = param_text.split(":")[1].strip().split("=")[0].strip()
                            parameters.append(f"{param_name}: {param_type}")
                        elif "=" in param_text:
                            param_name = param_text.split("=")[0].strip()
                            parameters.append(f"{param_name}=...")
                        else:
                            parameters.append(param_text)
            elif child.type == "type":
                return_type = get_node_text(child, code)
                
    elif lang == "js":
        # JavaScript: function_declaration, arrow_function, etc.
        for child in node.children:
            if child.type == "identifier":
                func_name = get_node_text(child, code)
            elif child.type == "formal_parameters":
                for param in child.children:
                    if param.type in ["identifier", "assignment_pattern", "rest_pattern"]:
                        parameters.append(get_node_text(param, code))
                        
    elif lang == "java":
        # Java: method_declaration
        for child in node.children:
            if child.type == "identifier":
                func_name = get_node_text(child, code)
            elif child.type == "formal_parameters":
                for param in child.children:
                    if param.type == "formal_parameter":
                        parameters.append(get_node_text(param, code))
            elif child.type in ["type_identifier", "generic_type", "void_type"]:
                return_type = get_node_text(child, code)
                
    elif lang == "cpp":
        # C++: function_definition -> function_declarator
        for child in node.children:
            if child.type == "function_declarator":
                for subchild in child.children:
                    if subchild.type == "identifier":
                        func_name = get_node_text(subchild, code)
                    elif subchild.type == "parameter_list":
                        for param in subchild.children:
                            if param.type == "parameter_declaration":
                                parameters.append(get_node_text(param, code))
            elif child.type in ["type_identifier", "primitive_type"]:
                return_type = get_node_text(child, code)
                
    elif lang == "rust":
        # Rust: function_item
        for child in node.children:
            if child.type == "identifier":
                func_name = get_node_text(child, code)
            elif child.type == "parameters":
                for param in child.children:
                    if param.type == "parameter":
                        parameters.append(get_node_text(param, code))
            elif child.type == "type_identifier":
                return_type = get_node_text(child, code)

    # Calculate complexity for this function
    complexity = calculate_complexity(node, code, lang)
    
    # Get line numbers (1-indexed for user display)
    start_line = node.start_point[0] + 1
    end_line = node.end_point[0] + 1
    
    # Get the function's source code
    func_code = get_node_text(node, code)

    # Create unique function name with file path
    unique_name = f"{file_path}-{func_name}"

    return {
        "functionName": unique_name,
        "name": func_name,
        "parameters": parameters,
        "returnType": return_type or "unknown",
        "complexity": complexity,
        "startLine": start_line,
        "endLine": end_line,
        "lines": end_line - start_line + 1,
        "code": func_code,
        "calls": []  # Will be populated separately
    }


# -------------------------------
# Function Call Extractor
# -------------------------------

def extract_function_calls(node: Node, code: str, exclude_names: set) -> List[str]:
    """
    Extract function calls from a function body using AST.
    More accurate than regex as it only detects actual call expressions.
    """
    calls = set()
    
    # Built-in functions to exclude
    builtins = {
        # Python
        'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
        'range', 'open', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr',
        'super', 'map', 'filter', 'zip', 'enumerate', 'sorted', 'reversed',
        'min', 'max', 'sum', 'abs', 'round', 'format', 'input', 'bool', 'bytes',
        # JavaScript
        'console', 'require', 'import', 'export', 'setTimeout', 'setInterval',
        'clearTimeout', 'clearInterval', 'fetch', 'Promise', 'Array', 'Object',
        'String', 'Number', 'Boolean', 'JSON', 'Math', 'Date', 'RegExp', 'Error',
        # Java
        'System', 'println', 'print', 'new', 'toString', 'equals', 'hashCode',
        # C++
        'std', 'cout', 'cin', 'printf', 'scanf', 'sizeof', 'malloc', 'free',
        # Rust
        'println', 'print', 'vec', 'Some', 'None', 'Ok', 'Err', 'Box', 'Rc', 'Arc',
        # Control flow keywords that look like calls
        'if', 'for', 'while', 'switch', 'catch', 'match',
    }
    
    def walk(n: Node):
        if n.type == "call_expression":
            # Get the function being called
            if n.children:
                func_node = n.children[0]
                # Handle direct function calls
                if func_node.type == "identifier":
                    func_name = get_node_text(func_node, code)
                    if func_name not in builtins and func_name not in exclude_names:
                        calls.add(func_name)
                # Handle method calls (obj.method())
                elif func_node.type == "member_expression":
                    # Get the method name
                    for child in func_node.children:
                        if child.type == "property_identifier":
                            method_name = get_node_text(child, code)
                            if method_name not in builtins:
                                calls.add(method_name)
        
        # Python: different node type for calls
        elif n.type == "call":
            if n.children:
                func_node = n.children[0]
                if func_node.type == "identifier":
                    func_name = get_node_text(func_node, code)
                    if func_name not in builtins and func_name not in exclude_names:
                        calls.add(func_name)
                elif func_node.type == "attribute":
                    # Get the attribute name (method being called)
                    for child in func_node.children:
                        if child.type == "identifier":
                            method_name = get_node_text(child, code)
                            if method_name not in builtins:
                                calls.add(method_name)
                                break  # Take the last identifier as the method name
        
        for child in n.children:
            walk(child)
    
    walk(node)
    return list(calls)


# -------------------------------
# Import Extractors (existing, kept for compatibility)
# -------------------------------

def extract_js_imports(tree, code):
    imports = []

    def walk(node):
        if node.type == "import_statement":
            for child in node.children:
                if child.type == "string":
                    module = code[child.start_byte+1 : child.end_byte-1]
                    imports.append(module)

        if node.type == "call_expression":
            if len(node.children) >= 2 and node.children[0].type == "identifier":
                fn = code[node.children[0].start_byte:node.children[0].end_byte]
                if fn == "require":
                    arg = node.children[1]
                    if arg.type == "arguments" and len(arg.children) >= 2:
                        mod_node = arg.children[1]
                        if mod_node.type == "string":
                            module = code[mod_node.start_byte+1 : mod_node.end_byte-1]
                            imports.append(module)

        for c in node.children:
            walk(c)

    walk(tree.root_node)
    return imports


def extract_py_imports(tree, code):
    imports = []

    def walk(node):
        if node.type == "import_statement":
            for child in node.children:
                if child.type == "dotted_name" or child.type == "identifier":
                    module = code[child.start_byte : child.end_byte]
                    imports.append(module)

        if node.type == "import_from_statement":
            if len(node.children) > 1:
                module = code[node.children[1].start_byte : node.children[1].end_byte]
                imports.append(module)

        for c in node.children:
            walk(c)

    walk(tree.root_node)
    return imports


def extract_java_imports(tree, code):
    imports = []

    def walk(node):
        if node.type == "import_declaration":
            for child in node.children:
                if child.type == "scoped_identifier" or child.type == "identifier":
                    module = code[child.start_byte : child.end_byte]
                    imports.append(module)

        for c in node.children:
            walk(c)

    walk(tree.root_node)
    return imports


def extract_cpp_imports(tree, code):
    imports = []

    def walk(node):
        if node.type == "preproc_include":
            for child in node.children:
                if child.type == "string_literal" or child.type == "system_lib_string":
                    header = code[child.start_byte : child.end_byte]
                    header = header.strip('"<>')
                    imports.append(header)

        for c in node.children:
            walk(c)

    walk(tree.root_node)
    return imports


def extract_rust_imports(tree, code):
    imports = []

    def walk(node):
        if node.type == "use_declaration":
            for child in node.children:
                if child.type == "scoped_identifier" or child.type == "identifier":
                    module = code[child.start_byte : child.end_byte]
                    imports.append(module)
                elif child.type == "use_list":
                    module_text = code[child.start_byte : child.end_byte]
                    imports.append(module_text)

        for c in node.children:
            walk(c)

    walk(tree.root_node)
    return imports


# -------------------------------
# Enhanced Function Extractor
# -------------------------------

def extract_functions_detailed(tree, code: str, lang: str, file_path: str) -> List[Dict[str, Any]]:
    """
    Extract all functions with detailed metadata using AST.
    Returns list of function details including complexity, parameters, etc.
    """
    functions = []
    
    # Define function node types for each language
    function_types = {
        "py": ["function_definition"],
        "js": ["function_declaration", "arrow_function", "function_expression", "method_definition"],
        "java": ["method_declaration", "constructor_declaration"],
        "cpp": ["function_definition"],
        "rust": ["function_item"],
    }
    
    target_types = function_types.get(lang, [])
    
    def walk(node: Node):
        if node.type in target_types:
            func_details = extract_function_details(node, code, lang, file_path)
            if func_details["name"]:  # Only add if we found a name
                # Extract calls from this function
                func_details["calls"] = extract_function_calls(node, code, {func_details["name"]})
                functions.append(func_details)
        
        for child in node.children:
            walk(child)
    
    walk(tree.root_node)
    return functions


# Backward compatibility wrapper
def extract_functions(tree, code) -> List[str]:
    """Legacy function for backward compatibility - returns just function names"""
    functions = []

    def walk(node):
        if node.type == "function_declaration":
            for child in node.children:
                if child.type == "identifier":
                    fn = code[child.start_byte:child.end_byte]
                    functions.append(fn)

        if node.type == "function_definition":
            for child in node.children:
                if child.type == "identifier":
                    fn = code[child.start_byte:child.end_byte]
                    functions.append(fn)

        if node.type == "method_declaration":
            for child in node.children:
                if child.type == "identifier":
                    fn = code[child.start_byte:child.end_byte]
                    functions.append(fn)

        if node.type == "function_definition":
            for child in node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            fn = code[subchild.start_byte:subchild.end_byte]
                            functions.append(fn)

        if node.type == "function_item":
            for child in node.children:
                if child.type == "identifier":
                    fn = code[child.start_byte:child.end_byte]
                    functions.append(fn)

        for c in node.children:
            walk(c)

    walk(tree.root_node)
    return functions


# -------------------------------
# Single File Analysis (Enhanced)
# -------------------------------

def analyze_file_detailed(path: str, base_path: str = "") -> Optional[Dict[str, Any]]:
    """
    Analyze a single file with full function details.
    Returns structured data with functions, complexity, etc.
    """
    lang = detect_language(path)
    if not lang:
        return None

    code = read_file(path)
    if not code.strip():
        return None

    # Set language for parser
    language = get_language_for_parser(lang)
    if not language:
        return None
    
    parser.language = language
    tree = parser.parse(bytes(code, "utf-8"))

    # Get relative path for display
    if base_path:
        rel_path = os.path.relpath(path, base_path)
    else:
        rel_path = path

    # Extract detailed function information
    functions = extract_functions_detailed(tree, code, lang, rel_path)

    # Extract imports
    if lang == "js":
        imports = extract_js_imports(tree, code)
    elif lang == "py":
        imports = extract_py_imports(tree, code)
    elif lang == "java":
        imports = extract_java_imports(tree, code)
    elif lang == "cpp":
        imports = extract_cpp_imports(tree, code)
    elif lang == "rust":
        imports = extract_rust_imports(tree, code)
    else:
        imports = []

    return {
        "filePath": rel_path,
        "language": SUPPORTED_EXTENSIONS.get(os.path.splitext(path)[1].lower(), "unknown"),
        "imports": imports,
        "listOfFunctions": functions,
        "totalLines": len(code.split('\n')),
        "totalFunctions": len(functions),
    }


def analyze_file(path: str) -> Optional[Dict[str, Any]]:
    """Legacy function for backward compatibility"""
    lang = detect_language(path)
    if not lang:
        return None

    code = read_file(path)
    if not code.strip():
        return None

    language = get_language_for_parser(lang)
    if not language:
        return None
    
    parser.language = language
    tree = parser.parse(bytes(code, "utf-8"))

    # Extract imports
    if lang == "js":
        imports = extract_js_imports(tree, code)
    elif lang == "py":
        imports = extract_py_imports(tree, code)
    elif lang == "java":
        imports = extract_java_imports(tree, code)
    elif lang == "cpp":
        imports = extract_cpp_imports(tree, code)
    elif lang == "rust":
        imports = extract_rust_imports(tree, code)
    else:
        imports = []

    # Extract functions
    functions = extract_functions(tree, code)

    return {
        "file": path,
        "imports": imports,
        "functions": functions
    }


# -------------------------------
# Extract Function Code by Name
# -------------------------------

def get_function_code(file_path: str, function_name: str) -> Optional[str]:
    """
    Get the source code of a specific function by name.
    Uses AST for accurate extraction.
    """
    lang = detect_language(file_path)
    if not lang:
        return None

    code = read_file(file_path)
    if not code.strip():
        return None

    language = get_language_for_parser(lang)
    if not language:
        return None
    
    parser.language = language
    tree = parser.parse(bytes(code, "utf-8"))

    # Define function node types for each language
    function_types = {
        "py": ["function_definition"],
        "js": ["function_declaration", "arrow_function", "function_expression", "method_definition"],
        "java": ["method_declaration", "constructor_declaration"],
        "cpp": ["function_definition"],
        "rust": ["function_item"],
    }
    
    target_types = function_types.get(lang, [])
    
    def find_function(node: Node) -> Optional[str]:
        if node.type in target_types:
            # Check if this is the function we're looking for
            for child in node.children:
                if child.type == "identifier":
                    name = get_node_text(child, code)
                    if name == function_name:
                        return get_node_text(node, code)
                elif child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            name = get_node_text(subchild, code)
                            if name == function_name:
                                return get_node_text(node, code)
        
        for child in node.children:
            result = find_function(child)
            if result:
                return result
        
        return None
    
    return find_function(tree.root_node)


# -------------------------------
# Analyze whole repository (Enhanced)
# -------------------------------

def find_source_files(repo_path: str) -> List[str]:
    """Find all source code files in the repository, respecting ignore rules."""
    source_files = []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip ignored directories (modifies dirs in-place to prevent descending)
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES and not d.startswith('.')]
        
        for f in files:
            if f.startswith('.'):
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                file_path = os.path.join(root, f)
                source_files.append(file_path)
    
    return source_files


def analyze_repo_detailed(repo_path: str) -> Dict[str, Any]:
    """
    Analyze entire repository with detailed function information.
    Returns structured data suitable for frontend visualization.
    """
    # Find all source files
    file_paths = find_source_files(repo_path)
    
    # Analyze each file
    analyzed_files = []
    for f in file_paths:
        result = analyze_file_detailed(f, repo_path)
        if result:
            analyzed_files.append(result)
    
    # Build architecture edges (function calls between files)
    edges = []
    all_functions = {}  # Map function name to file
    
    for file_data in analyzed_files:
        for func in file_data["listOfFunctions"]:
            all_functions[func["name"]] = file_data["filePath"]
    
    for file_data in analyzed_files:
        for func in file_data["listOfFunctions"]:
            for call in func["calls"]:
                if call in all_functions and all_functions[call] != file_data["filePath"]:
                    edges.append({
                        "source": func["functionName"],
                        "target": f"{all_functions[call]}-{call}",
                        "sourceFile": file_data["filePath"],
                        "targetFile": all_functions[call],
                    })

    return {
        "listOfFiles": analyzed_files,
        "edges": edges,
        "totalFiles": len(analyzed_files),
        "totalFunctions": sum(f["totalFunctions"] for f in analyzed_files),
    }


def analyze_repo(repo_path: str) -> Dict[str, Any]:
    """Legacy function for backward compatibility"""
    results = {}
    valid_exts = [".js", ".jsx", ".ts", ".tsx", ".py", ".java", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".rs"]

    file_paths = []
    for root, _, files in os.walk(repo_path):
        for f in files:
            if os.path.splitext(f)[1] in valid_exts:
                file_paths.append(os.path.join(root, f))

    for f in file_paths:
        meta = analyze_file(f)
        if meta:
            results[f] = meta

    edges = []
    for file, meta in results.items():
        for imp in meta["imports"]:
            if imp.startswith("."):
                base_dir = os.path.dirname(file)
                possible = os.path.normpath(os.path.join(base_dir, imp))
                for ext in valid_exts:
                    if os.path.exists(possible + ext):
                        edges.append({"source": file, "target": possible + ext})

    nodes = [{"id": f} for f in results.keys()]

    return {
        "nodes": nodes,
        "edges": edges,
        "metadata": results
    }


# -------------------------------
# Local testing
# -------------------------------
if __name__ == "__main__":
    import sys
    repo = sys.argv[1]
    output = analyze_repo_detailed(repo)
    print(json.dumps(output, indent=2))
