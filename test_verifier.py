"""
Unit Test Suite for Claim Grounding Verifier
"""

import os
import json
from claim_grounding_verifier.make_demo_repo import create_demo_repository
from claim_grounding_verifier.extractor import extract_claims_from_report
from claim_grounding_verifier.verifier import verify_report_claims, ClaimVerifier
from claim_grounding_verifier.triage import calculate_triage_score
from claim_grounding_verifier.schema import Verdict, VersionStatus, ClaimType


def test_full_verification_flow():
    # 1. Setup Demo Repo
    repo_info = create_demo_repository()
    repo_dir = repo_info["repo_dir"]

    # 2. Load Demo Report
    report_file = os.path.join(os.path.dirname(__file__), "claim_grounding_verifier", "demo_report.txt")
    with open(report_file, "r", encoding="utf-8") as f:
        report_text = f.read()

    # 3. Extract Claims
    claims = extract_claims_from_report(report_text, repository="demo_repo", target_commit=repo_info["head_commit"])
    assert len(claims) > 0, "Failed to extract claims from demo report"

    # 4. Verify Claims
    results = verify_report_claims(claims, repo_dir)
    assert len(results) == len(claims)

    verdicts = {r.claim.claim_id: r.verdict for r in results}
    types = {r.claim.claim_id: r.claim.claim_type for r in results}

    print("\n[+] Verification Test Results:")
    for r in results:
        ev_str = f" ({r.evidence.evidence_type})" if r.evidence else ""
        print(f"    - [{r.verdict.value}] {r.claim.claim_text}{ev_str}")

    # Check Checkpoint M1 & M2 Requirements
    supported_count = sum(1 for r in results if r.verdict == Verdict.SUPPORTED)
    refuted_count = sum(1 for r in results if r.verdict == Verdict.REFUTED)
    unverifiable_count = sum(1 for r in results if r.verdict == Verdict.UNVERIFIABLE)

    assert supported_count > 0, "Expected at least one SUPPORTED claim"
    assert refuted_count > 0, "Expected at least one REFUTED claim (fake_decoder)"
    assert unverifiable_count > 0, "Expected at least one UNVERIFIABLE claim (behavioral abstention)"

    # 5. Triage Score & Experiment Record
    triage = calculate_triage_score("DEMO-REPORT-001", "demo_repo", repo_info["head_commit"], results)
    triage_dict = triage.to_dict()

    print(f"\n[+] Triage Score: {triage_dict['triage_score']:.1f}/100 ({triage_dict['triage_label']})")
    print(f"    - Supported: {triage_dict['supported_claims']} | Refuted: {triage_dict['refuted_claims']} | Unverifiable: {triage_dict['unverifiable_claims']}")

    # Save Experiment Record JSON (conforming to Section 16/28 format)
    exp_dir = os.path.join(os.path.dirname(__file__), "experiments")
    os.makedirs(exp_dir, exist_ok=True)
    exp_file = os.path.join(exp_dir, "EXP-0001.json")
    with open(exp_file, "w", encoding="utf-8") as f:
        json.dump(triage_dict, f, indent=2)

    print(f"[+] Saved Experiment Record to: {exp_file}")
    print("\n[OK] ALL VERIFICATION UNIT TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    test_full_verification_flow()

