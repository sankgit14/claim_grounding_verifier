"""
Atomic Claim Schema & Verification Data Structures
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import json


class ClaimType(str, Enum):
    FILE_EXISTS = "FILE_EXISTS"
    SYMBOL_EXISTS = "SYMBOL_EXISTS"
    CALL_RELATION = "CALL_RELATION"
    VERSION = "VERSION"
    HISTORY = "HISTORY"
    BEHAVIOR = "BEHAVIOR"


class Verdict(str, Enum):
    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    UNVERIFIABLE = "UNVERIFIABLE"


class VersionStatus(str, Enum):
    CURRENTLY_SUPPORTED = "CURRENTLY_SUPPORTED"
    HISTORICAL_ONLY = "HISTORICAL_ONLY"
    REFUTED_AT_TARGET = "REFUTED_AT_TARGET"
    UNVERIFIABLE = "UNVERIFIABLE"


@dataclass
class Evidence:
    repository: str
    commit: str
    file_path: Optional[str] = None
    symbol_name: Optional[str] = None
    line_range: Optional[str] = None
    evidence_type: str = "STATIC_ANALYSIS"
    snippet: Optional[str] = None
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Claim:
    claim_id: str
    claim_text: str
    claim_type: ClaimType
    entities: Dict[str, Any] = field(default_factory=dict)
    target_repository: Optional[str] = None
    target_commit: Optional[str] = None
    target_version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["claim_type"] = self.claim_type.value
        return d


@dataclass
class VerificationResult:
    claim: Claim
    verdict: Verdict
    version_status: VersionStatus = VersionStatus.CURRENTLY_SUPPORTED
    confidence: float = 1.0
    evidence: Optional[Evidence] = None
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim": self.claim.to_dict(),
            "verdict": self.verdict.value,
            "version_status": self.version_status.value,
            "confidence": self.confidence,
            "evidence": self.evidence.to_dict() if self.evidence else None,
            "reason": self.reason
        }


@dataclass
class TriageResult:
    report_id: str
    repository: str
    target_commit: str
    total_claims: int
    supported_claims: int
    refuted_claims: int
    unverifiable_claims: int
    triage_score: float
    triage_label: str
    results: List[VerificationResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "repository": self.repository,
            "target_commit": self.target_commit,
            "total_claims": self.total_claims,
            "supported_claims": self.supported_claims,
            "refuted_claims": self.refuted_claims,
            "unverifiable_claims": self.unverifiable_claims,
            "triage_score": round(self.triage_score, 2),
            "triage_label": self.triage_label,
            "results": [r.to_dict() for r in self.results]
        }


@dataclass
class ExperimentRecord:
    experiment_id: str
    split: str
    report_id: str
    repository: str
    target_commit: str
    claim_count: int
    supported: int
    refuted: int
    unverifiable: int
    triage_score: float
    evidence_precision: Optional[float] = None
    latency_ms: float = 0.0
    model: str = "heuristic_static"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
