"""
Source Code Indexing Module
Scans target repository source tree, builds AST/symbol tables, and extracts call graph relationships.
"""

import os
import re
from typing import Dict, List, Set, Tuple, Optional


class SourceIndex:
    def __init__(self, repo_dir: str):
        self.repo_dir = repo_dir
        self.files: Set[str] = set()
        self.symbols: Dict[str, List[Dict[str, str]]] = {}  # symbol_name -> list of {file, line}
        self.calls: Set[Tuple[str, str]] = set()           # (caller, callee)
        self.index_repository()

    def index_repository(self):
        if not os.path.exists(self.repo_dir):
            return

        # Common source extensions
        valid_exts = ('.c', '.h', '.cpp', '.hpp', '.py', '.js', '.ts', '.go', '.java', '.rs')

        for root, dirs, filenames in os.walk(self.repo_dir):
            # Skip .git directory
            if '.git' in root:
                continue

            for fname in filenames:
                if fname.endswith(valid_exts):
                    abs_path = os.path.join(root, fname)
                    rel_path = os.path.relpath(abs_path, self.repo_dir).replace('\\', '/')
                    self.files.add(rel_path)
                    self._parse_file(abs_path, rel_path)

    def _parse_file(self, abs_path: str, rel_path: str):
        try:
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception:
            return

        # Regex for C/C++/Java/Go/Python function definitions
        c_func_def = re.compile(r'^(?:[a-zA-Z_][a-zA-Z0-9_*\s]+)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^;]*\)\s*\{')
        py_func_def = re.compile(r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')

        # Regex for function calls inside body
        call_regex = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')

        current_function: Optional[str] = None

        for line_num, line in enumerate(lines, 1):
            line_str = line.strip()

            # Check function definition
            m_c = c_func_def.match(line_str)
            m_py = py_func_def.match(line_str)
            matched_symbol = None

            if m_c:
                matched_symbol = m_c.group(1)
            elif m_py:
                matched_symbol = m_py.group(1)

            if matched_symbol and matched_symbol not in ['if', 'while', 'for', 'switch', 'return']:
                current_function = matched_symbol
                if matched_symbol not in self.symbols:
                    self.symbols[matched_symbol] = []
                self.symbols[matched_symbol].append({
                    "file": rel_path,
                    "line": str(line_num)
                })

            # Check calls inside current function
            if current_function:
                for match in call_regex.finditer(line_str):
                    callee = match.group(1)
                    if callee != current_function and callee not in ['if', 'while', 'for', 'switch', 'return', 'sizeof', 'sizeof_val']:
                        self.calls.add((current_function, callee))

    def file_exists(self, path: str) -> bool:
        norm_path = path.replace('\\', '/')
        # Check exact or basename match
        if norm_path in self.files:
            return True
        return any(f.endswith(norm_path) for f in self.files)

    def find_symbol(self, symbol_name: str) -> List[Dict[str, str]]:
        return self.symbols.get(symbol_name, [])

    def has_call(self, caller: str, callee: str) -> bool:
        return (caller, callee) in self.calls
