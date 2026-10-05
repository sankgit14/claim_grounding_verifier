"""
Evidence Model & Provenance Module
Formats grounded evidence objects with file, symbol, line range, and git commit details.
"""

from typing import Optional
from .schema import Evidence


def create_file_evidence(repository: str, commit: str, file_path: str, exists: bool) -> Evidence:
    if exists:
        return Evidence(
            repository=repository,
            commit=commit,
            file_path=file_path,
            evidence_type="FILE_EXISTS_VERIFIED",
            description=f"File '{file_path}' confirmed present in target repository tree at revision {commit}."
        )
    else:
        return Evidence(
            repository=repository,
            commit=commit,
            file_path=file_path,
            evidence_type="FILE_ABSENT",
            description=f"File '{file_path}' definitively absent from repository snapshot at revision {commit}."
        )


def create_symbol_evidence(repository: str, commit: str, symbol_name: str, locations: list) -> Evidence:
    if locations:
        loc = locations[0]
        file_path = loc.get("file", "")
        line_num = loc.get("line", "")
        return Evidence(
            repository=repository,
            commit=commit,
            file_path=file_path,
            symbol_name=symbol_name,
            line_range=line_num,
            evidence_type="SYMBOL_AST_VERIFIED",
            description=f"Symbol '{symbol_name}' found in AST at {file_path}:{line_num} at revision {commit}."
        )
    else:
        return Evidence(
            repository=repository,
            commit=commit,
            symbol_name=symbol_name,
            evidence_type="SYMBOL_ABSENT",
            description=f"Symbol '{symbol_name}' not resolved in AST or symbol index for revision {commit}."
        )


def create_call_evidence(repository: str, commit: str, caller: str, callee: str, is_direct_call: bool, caller_locations: list) -> Evidence:
    file_path = caller_locations[0].get("file", "") if caller_locations else None
    line_num = caller_locations[0].get("line", "") if caller_locations else None
    
    if is_direct_call:
        return Evidence(
            repository=repository,
            commit=commit,
            file_path=file_path,
            symbol_name=caller,
            line_range=line_num,
            evidence_type="DIRECT_CALL_GRAPH_VERIFIED",
            description=f"Direct call relation '{caller}() -> {callee}()' confirmed in AST call graph at {file_path}:{line_num}."
        )
    else:
        return Evidence(
            repository=repository,
            commit=commit,
            file_path=file_path,
            symbol_name=caller,
            evidence_type="CALL_RELATION_UNRESOLVED",
            description=f"Direct call relation '{caller}() -> {callee}()' absent in AST analysis scope."
        )
