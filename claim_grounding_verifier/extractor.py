"""
Claim Extraction Engine
Decomposes vulnerability report text into structured atomic claims using heuristic pattern matching.
"""

import re
from typing import List, Dict, Any
from .schema import Claim, ClaimType


class HeuristicClaimExtractor:
    def __init__(self):
        # Regex patterns
        self.file_pattern = re.compile(r'\b([a-zA-Z0-9_/-]+\.(?:c|h|py|js|ts|go|java|cpp|rs|php|rb|pyw))\b')
        self.func_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)')
        self.call_patterns = [
            re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(\))?\s+(?:calls|invokes|delegates data processing to|uses)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(\))?\b', re.IGNORECASE),
            re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)\s+calls\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\)\b', re.IGNORECASE)
        ]
        self.version_pattern = re.compile(r'\b(?:version|v)\s*([0-9]+\.[0-9]+(?:\.[0-9]+)?)\b', re.IGNORECASE)
        self.commit_pattern = re.compile(r'\b(?:commit|sha)\s*(?:message\s*)?[\'"]?([a-f0-9]{7,40}|[a-zA-Z0-9_\s:-]{10,80})[\'"]?', re.IGNORECASE)
        self.behavior_keywords = [
            'remote code execution', 'buffer overflow', 'arbitrary code execution',
            'memory corruption', 'denial of service', 'privilege escalation', 'sql injection'
        ]

    def extract_claims(self, report_text: str, repository: str = "demo_repo", target_commit: str = "HEAD") -> List[Claim]:
        claims: List[Claim] = []
        claim_counter = 1

        seen_files = set()
        seen_symbols = set()
        seen_calls = set()

        # 1. Extract File Existence Claims
        for match in self.file_pattern.finditer(report_text):
            file_path = match.group(1)
            if file_path not in seen_files:
                seen_files.add(file_path)
                claims.append(Claim(
                    claim_id=f"C{claim_counter:02d}",
                    claim_text=f"File '{file_path}' exists in target repository.",
                    claim_type=ClaimType.FILE_EXISTS,
                    entities={"file_path": file_path},
                    target_repository=repository,
                    target_commit=target_commit
                ))
                claim_counter += 1

        # 2. Extract Call Relation Claims
        for pattern in self.call_patterns:
            for match in pattern.finditer(report_text):
                caller, callee = match.group(1), match.group(2)
                call_key = (caller, callee)
                if call_key not in seen_calls:
                    seen_calls.add(call_key)
                    claims.append(Claim(
                        claim_id=f"C{claim_counter:02d}",
                        claim_text=f"Function '{caller}()' calls function '{callee}()'.",
                        claim_type=ClaimType.CALL_RELATION,
                        entities={"caller": caller, "callee": callee},
                        target_repository=repository,
                        target_commit=target_commit
                    ))
                    claim_counter += 1

        # 3. Extract Symbol Existence Claims
        for match in self.func_pattern.finditer(report_text):
            symbol_name = match.group(1)
            if symbol_name not in seen_symbols and symbol_name not in ['if', 'while', 'for', 'switch']:
                seen_symbols.add(symbol_name)
                claims.append(Claim(
                    claim_id=f"C{claim_counter:02d}",
                    claim_text=f"Symbol/Function '{symbol_name}()' exists in source code.",
                    claim_type=ClaimType.SYMBOL_EXISTS,
                    entities={"symbol_name": symbol_name},
                    target_repository=repository,
                    target_commit=target_commit
                ))
                claim_counter += 1

        # 4. Extract History / Commit Claims
        lines = report_text.splitlines()
        for line in lines:
            if 'commit' in line.lower() or 'fixed' in line.lower() or 'addressed' in line.lower():
                claims.append(Claim(
                    claim_id=f"C{claim_counter:02d}",
                    claim_text=f"Historical commit claim: {line.strip()}",
                    claim_type=ClaimType.HISTORY,
                    entities={"statement": line.strip()},
                    target_repository=repository,
                    target_commit=target_commit
                ))
                claim_counter += 1
                break

        # 5. Extract Version Claims
        for match in self.version_pattern.finditer(report_text):
            version_str = match.group(1)
            claims.append(Claim(
                claim_id=f"C{claim_counter:02d}",
                claim_text=f"Vulnerability affects version '{version_str}'.",
                claim_type=ClaimType.VERSION,
                entities={"version": version_str},
                target_repository=repository,
                target_commit=target_commit
            ))
            claim_counter += 1

        # 6. Extract Behavioral / Exploitability Claims
        for kw in self.behavior_keywords:
            if kw in report_text.lower():
                claims.append(Claim(
                    claim_id=f"C{claim_counter:02d}",
                    claim_text=f"Behavioral claim: Vulnerability allows {kw}.",
                    claim_type=ClaimType.BEHAVIOR,
                    entities={"impact": kw},
                    target_repository=repository,
                    target_commit=target_commit
                ))
                claim_counter += 1

        return claims


def extract_claims_from_report(report_text: str, repository: str = "demo_repo", target_commit: str = "HEAD") -> List[Claim]:
        extractor = HeuristicClaimExtractor()
        return extractor.extract_claims(report_text, repository, target_commit)
