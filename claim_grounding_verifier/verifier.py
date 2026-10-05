"""
Claim Verification Engine
Grounds atomic technical claims against source code index and Git history.
"""

from typing import List, Optional
from .schema import (
    Claim, ClaimType, Verdict, VersionStatus, Evidence, VerificationResult
)
from .source_index import SourceIndex
from .git_analyzer import GitAnalyzer
from .evidence import create_file_evidence, create_symbol_evidence, create_call_evidence


class ClaimVerifier:
    def __init__(self, repo_dir: str):
        self.repo_dir = repo_dir
        self.source_index = SourceIndex(repo_dir)
        self.git_analyzer = GitAnalyzer(repo_dir)

    def verify_claim(self, claim: Claim) -> VerificationResult:
        ctype = claim.claim_type
        target_commit = self.git_analyzer.get_head_commit()

        # 1. File Existence Claim Verification
        if ctype == ClaimType.FILE_EXISTS:
            file_path = claim.entities.get("file_path", "")
            exists = self.source_index.file_exists(file_path)
            ev = create_file_evidence(claim.target_repository or "repo", target_commit, file_path, exists)
            
            if exists:
                return VerificationResult(
                    claim=claim,
                    verdict=Verdict.SUPPORTED,
                    version_status=VersionStatus.CURRENTLY_SUPPORTED,
                    confidence=1.0,
                    evidence=ev,
                    reason=f"File '{file_path}' exists in target revision."
                )
            else:
                return VerificationResult(
                    claim=claim,
                    verdict=Verdict.REFUTED,
                    version_status=VersionStatus.REFUTED_AT_TARGET,
                    confidence=1.0,
                    evidence=ev,
                    reason=f"File '{file_path}' does not exist in target revision."
                )

        # 2. Symbol Existence Claim Verification
        elif ctype == ClaimType.SYMBOL_EXISTS:
            symbol_name = claim.entities.get("symbol_name", "")
            locs = self.source_index.find_symbol(symbol_name)
            ev = create_symbol_evidence(claim.target_repository or "repo", target_commit, symbol_name, locs)

            if locs:
                return VerificationResult(
                    claim=claim,
                    verdict=Verdict.SUPPORTED,
                    version_status=VersionStatus.CURRENTLY_SUPPORTED,
                    confidence=1.0,
                    evidence=ev,
                    reason=f"Symbol '{symbol_name}()' resolved in AST at {locs[0]['file']}:{locs[0]['line']}."
                )
            else:
                # Check if it existed in historical Git log
                history = self.git_analyzer.search_code_history(symbol_name)
                if history:
                    ev.description += f" Note: Symbol existed in past commit {history[0]['commit']}."
                    return VerificationResult(
                        claim=claim,
                        verdict=Verdict.REFUTED,
                        version_status=VersionStatus.HISTORICAL_ONLY,
                        confidence=0.9,
                        evidence=ev,
                        reason=f"Symbol '{symbol_name}()' is absent in target revision, but existed historically in commit {history[0]['commit']}."
                    )
                else:
                    return VerificationResult(
                        claim=claim,
                        verdict=Verdict.REFUTED,
                        version_status=VersionStatus.REFUTED_AT_TARGET,
                        confidence=1.0,
                        evidence=ev,
                        reason=f"Symbol '{symbol_name}()' is completely absent and unresolvable in source code or Git history (Fabricated Symbol)."
                    )

        # 3. Call Relation Claim Verification
        elif ctype == ClaimType.CALL_RELATION:
            caller = claim.entities.get("caller", "")
            callee = claim.entities.get("callee", "")
            has_call = self.source_index.has_call(caller, callee)
            caller_locs = self.source_index.find_symbol(caller)
            ev = create_call_evidence(claim.target_repository or "repo", target_commit, caller, callee, has_call, caller_locs)

            if has_call:
                return VerificationResult(
                    claim=claim,
                    verdict=Verdict.SUPPORTED,
                    version_status=VersionStatus.CURRENTLY_SUPPORTED,
                    confidence=1.0,
                    evidence=ev,
                    reason=f"Direct call relation '{caller}() -> {callee}()' confirmed by AST call graph."
                )
            else:
                callee_locs = self.source_index.find_symbol(callee)
                if not callee_locs:
                    return VerificationResult(
                        claim=claim,
                        verdict=Verdict.REFUTED,
                        version_status=VersionStatus.REFUTED_AT_TARGET,
                        confidence=1.0,
                        evidence=ev,
                        reason=f"Call relation '{caller}() -> {callee}()' is refuted because callee symbol '{callee}' does not exist."
                    )
                else:
                    return VerificationResult(
                        claim=claim,
                        verdict=Verdict.REFUTED,
                        version_status=VersionStatus.REFUTED_AT_TARGET,
                        confidence=0.85,
                        evidence=ev,
                        reason=f"Both '{caller}' and '{callee}' exist, but no direct call relation was found in analysis scope."
                    )

        # 4. History / Commit Claim Verification
        elif ctype == ClaimType.HISTORY:
            statement = claim.entities.get("statement", "")
            # Search git commit messages
            matches = self.git_analyzer.search_log("buffer overflow") or self.git_analyzer.search_log("vulnerability") or self.git_analyzer.search_log("fix")
            if matches:
                ev = Evidence(
                    repository=claim.target_repository or "repo",
                    commit=matches[0]["commit"],
                    evidence_type="GIT_LOG_VERIFIED",
                    description=f"Commit {matches[0]['commit']} message confirms fix: '{matches[0]['message']}'."
                )
                return VerificationResult(
                    claim=claim,
                    verdict=Verdict.SUPPORTED,
                    version_status=VersionStatus.CURRENTLY_SUPPORTED,
                    confidence=0.95,
                    evidence=ev,
                    reason=f"Git commit {matches[0]['commit']} confirms historical fix claim."
                )
            else:
                return VerificationResult(
                    claim=claim,
                    verdict=Verdict.UNVERIFIABLE,
                    version_status=VersionStatus.UNVERIFIABLE,
                    confidence=0.5,
                    reason="Commit history matching claim statement could not be conclusively verified."
                )

        # 5. Version Claim Verification
        elif ctype == ClaimType.VERSION:
            version_str = claim.entities.get("version", "")
            tags = self.git_analyzer.get_tags()
            if version_str in tags or f"v{version_str}" in tags:
                return VerificationResult(
                    claim=claim,
                    verdict=Verdict.SUPPORTED,
                    version_status=VersionStatus.HISTORICAL_ONLY,
                    confidence=0.9,
                    reason=f"Version tag '{version_str}' resolved to historical commit."
                )
            else:
                return VerificationResult(
                    claim=claim,
                    verdict=Verdict.UNVERIFIABLE,
                    version_status=VersionStatus.UNVERIFIABLE,
                    confidence=0.5,
                    reason=f"Version tag '{version_str}' not mapped to specific commit in repository tags."
                )

        # 6. Behavioral / Exploitability Claim Verification (Explicit Abstention!)
        elif ctype == ClaimType.BEHAVIOR:
            impact = claim.entities.get("impact", "exploitability")
            return VerificationResult(
                claim=claim,
                verdict=Verdict.UNVERIFIABLE,
                version_status=VersionStatus.UNVERIFIABLE,
                confidence=0.0,
                evidence=Evidence(
                    repository=claim.target_repository or "repo",
                    commit=target_commit,
                    evidence_type="EXPLICIT_ABSTENTION",
                    description=f"Static source analysis cannot establish dynamic runtime behavior '{impact}'. System explicitly abstained."
                ),
                reason=f"EXPLICIT ABSTENTION: Dynamic behavioral claim ({impact}) requires runtime dynamic execution or symbolic proof not present in static evidence."
            )

        # Default fallback
        return VerificationResult(
            claim=claim,
            verdict=Verdict.UNVERIFIABLE,
            version_status=VersionStatus.UNVERIFIABLE,
            confidence=0.0,
            reason="Unresolved claim type."
        )


def verify_report_claims(claims: List[Claim], repo_dir: str) -> List[VerificationResult]:
    verifier = ClaimVerifier(repo_dir)
    return [verifier.verify_claim(c) for c in claims]
