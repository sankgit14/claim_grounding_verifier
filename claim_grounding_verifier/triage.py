"""
Triage Prioritization Module
Computes Heuristic Triage Score (0-100) based on verified claim evidence and abstentions.
"""

from typing import List
from .schema import VerificationResult, Verdict, TriageResult, ClaimType


def calculate_triage_score(report_id: str, repository: str, target_commit: str, results: List[VerificationResult]) -> TriageResult:
    total_claims = len(results)
    supported = sum(1 for r in results if r.verdict == Verdict.SUPPORTED)
    refuted = sum(1 for r in results if r.verdict == Verdict.REFUTED)
    unverifiable = sum(1 for r in results if r.verdict == Verdict.UNVERIFIABLE)

    if total_claims == 0:
        return TriageResult(
            report_id=report_id,
            repository=repository,
            target_commit=target_commit,
            total_claims=0,
            supported_claims=0,
            refuted_claims=0,
            unverifiable_claims=0,
            triage_score=0.0,
            triage_label="LOW_PRIORITY",
            results=results
        )

    # Base score calculated from ratio of supported to verified claims
    verified_denom = (supported + refuted)
    if verified_denom > 0:
        base_score = (supported / verified_denom) * 100.0
    else:
        base_score = 50.0  # Neutral if all claims are unverifiable

    # Penalty for fabricated symbols or invalid call relations
    fabricated_count = sum(1 for r in results if r.verdict == Verdict.REFUTED and r.claim.claim_type in [ClaimType.SYMBOL_EXISTS, ClaimType.CALL_RELATION])
    penalty = fabricated_count * 25.0

    # Final score
    final_score = max(0.0, min(100.0, base_score - penalty))

    # Triage Priority Label
    if final_score >= 70.0:
        label = "HIGH_PRIORITY (Grounded Report)"
    elif final_score >= 35.0:
        label = "MEDIUM_PRIORITY (Partial/Mixed Evidence)"
    else:
        label = "LOW_PRIORITY (Likely Invalid / Fabricated Claims)"

    return TriageResult(
        report_id=report_id,
        repository=repository,
        target_commit=target_commit,
        total_claims=total_claims,
        supported_claims=supported,
        refuted_claims=refuted,
        unverifiable_claims=unverifiable,
        triage_score=final_score,
        triage_label=label,
        results=results
    )
