"""
Derived Claim-Level Grounding Benchmark Builder
Extracts verifiable technical claims from HackerOne report dataset and builds benchmark annotations.
"""

import os
import sys
import json
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from claim_grounding_verifier.extractor import HeuristicClaimExtractor
from claim_grounding_verifier.schema import Verdict


def build_benchmark_from_parquet():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    val_path = os.path.join(base_dir, "vulneribility_data", "validation-00000-of-00001.parquet")
    out_dir = os.path.join(base_dir, "benchmark")
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(val_path):
        print(f"[-] Dataset file not found: {val_path}")
        return

    df = pd.read_parquet(val_path)
    extractor = HeuristicClaimExtractor()
    annotations = []

    for idx, row in df.head(100).iterrows():
        report_id = str(row.get("id", f"R-{idx}"))
        text = str(row.get("vulnerability_information", ""))
        title = str(row.get("title", ""))
        substate = str(row.get("substate", "unknown"))

        full_text = f"{title}\n{text}"
        claims = extractor.extract_claims(full_text, repository="open-source/repo", target_commit="HEAD")

        # Map substate to gold verdict expectation
        # resolved -> SUPPORTED / UNVERIFIABLE
        # informative/not-applicable/spam -> REFUTED / UNVERIFIABLE
        for c in claims:
            gold = Verdict.SUPPORTED if substate == "resolved" else Verdict.REFUTED
            if c.claim_type.value == "BEHAVIOR":
                gold = Verdict.UNVERIFIABLE

            annotations.append({
                "report_id": report_id,
                "substate": substate,
                "claim_id": c.claim_id,
                "claim_text": c.claim_text,
                "claim_type": c.claim_type.value,
                "gold_verdict": gold.value,
                "entities": json.dumps(c.entities)
            })

    bench_df = pd.DataFrame(annotations)
    out_parquet = os.path.join(out_dir, "claim_annotations.parquet")
    bench_df.to_parquet(out_parquet)

    repos_json = os.path.join(out_dir, "repositories.json")
    with open(repos_json, "w", encoding="utf-8") as f:
        json.dump({
            "demo_repo": {"path": "demo_repo", "target_commit": "HEAD"},
            "hackerone_sample": {"path": "vulneribility_data", "records": len(bench_df)}
        }, f, indent=2)

    print(f"[+] Benchmark Created Successfully at: {out_parquet}")
    print(f"    - Total Claim Annotations: {len(bench_df)}")


if __name__ == "__main__":
    build_benchmark_from_parquet()
