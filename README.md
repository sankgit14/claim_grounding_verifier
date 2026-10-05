# 🛡️ Claim-Level Grounding Verification of Vulnerability Reports

> **A Research Prototype for Open-Source Maintainer Triage & Source-Grounded Vulnerability Verification**

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Overview

Open-source maintainers and bug-bounty triagers receive large volumes of vulnerability reports. Many sound technically credible but contain fabricated or unverifiable assertions—such as non-existent functions, absent call paths, incorrect version bounds, or vulnerabilities already fixed in earlier commits.

This system decomposes free-form untrusted vulnerability reports into **atomic, checkable technical claims** and grounds each claim directly against target source-code snapshots, AST symbol tables, and Git commit history.

Primary outcomes:
- **Per-Claim Verdict**: `SUPPORTED`, `REFUTED`, or `UNVERIFIABLE`.
- **Version Awareness**: Distinguishes `CURRENTLY_SUPPORTED`, `HISTORICAL_ONLY`, and `REFUTED_AT_TARGET`.
- **Explicit Abstention**: Abstains (`UNVERIFIABLE`) when static evidence is insufficient to prove dynamic runtime behavior.
- **Evidence Provenance**: Attaches precise source file locations, line ranges, and Git commit hashes to every verdict.
- **Calibrated Triage Score**: Prioritizes genuine grounded reports while penalizing fabricated technical claims.

---

## 🏗️ System Architecture

```text
                 Vulnerability Report + Repository + Commit
                                      |
                                      v
                        +---------------------------+
                        |   Heuristic/LLM Claim     |
                        |     Extraction Engine     |
                        +-------------+-------------+
                                      |
                                      v
                        +---------------------------+
                        |    Atomic Claim Schema    |
                        +-------------+-------------+
                                      |
                 +--------------------+--------------------+
                 |                                         |
                 v                                         v
   +---------------------------+             +---------------------------+
   |    Source AST & Symbol    |             |      Git History &        |
   |      Indexer (files,      |             |      Version Analyzer     |
   |      symbols, calls)      |             |     (commits, tags)       |
   +-------------+-------------+             +-------------+-------------+
                 |                                         |
                 +--------------------+--------------------+
                                      |
                                      v
                        +---------------------------+
                        |      Claim Verifier &     |
                        |     Evidence Resolver     |
                        +-------------+-------------+
                                      |
                 +--------------------+--------------------+
                 |                    |                    |
                 v                    v                    v
             SUPPORTED             REFUTED            UNVERIFIABLE
                 |                    |                    |
                 +--------------------+--------------------+
                                      |
                                      v
                        +---------------------------+
                        |   Triage Score & Provenance|
                        |      Interactive Web UI   |
                        +---------------------------+
```

---

## 📁 Repository Organization

```text
antigravity_proto/
│
├── claim_grounding_verifier/
│   ├── schema.py                 # Atomic claim schema & verdict definitions
│   ├── extractor.py              # Regex/Heuristic claim extraction engine
│   ├── source_index.py           # AST & symbol indexer for files/symbols/calls
│   ├── git_analyzer.py           # Git history, commit diffs & version status
│   ├── verifier.py               # Core claim verifier engine
│   ├── evidence.py               # Evidence & provenance model builder
│   ├── triage.py                 # Heuristic Triage Score calculator (0-100)
│   ├── calibration.py            # ECE & Brier score calibration
│   ├── evaluation.py             # Macro-F1, Precision, Recall & Confusion Matrix
│   ├── make_demo_repo.py         # Controlled test repository generator
│   ├── demo_report.txt           # Sample vulnerability report
│   ├── app.py                    # Streamlit Web Dashboard
│   └── requirements.txt          # Python dependencies
│
├── benchmark/
│   ├── build_benchmark.py        # Benchmark extraction script
│   ├── claim_annotations.parquet # Derived claim-level grounding benchmark
│   └── repositories.json
│
├── vulnerability_papers/         # Core reference research papers (PDFs)
├── experiments/                  # JSON experiment records (EXP-0001.json)
├── test_verifier.py              # End-to-end verification test suite
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ installed
- Git installed

### 2. Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/YOUR_USERNAME/claim_grounding_verifier.git
cd claim_grounding_verifier

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r claim_grounding_verifier/requirements.txt
```

---

## 🧪 Running Tests & Demonstration

### Run Command-Line Verification Test Suite
Executes end-to-end claim extraction, git analysis, symbol resolution, and explicit abstention on a controlled local repository:

```bash
python test_verifier.py
```

### Launch Interactive Web Dashboard
Launches the multi-tab Streamlit web application:

```bash
streamlit run claim_grounding_verifier/app.py
```

Open `http://localhost:8501` in your browser to view:
- 🛡️ **Live Report Verifier**: Paste vulnerability text and view claim grounding table.
- 🚀 **Controlled Mentor Demo**: Pre-configured execution of Checkpoints M1 & M2.
- 📊 **HackerOne Dataset Explorer**: Filter and inspect 9,900+ disclosed bug bounty reports.
- 📈 **Research Metrics Panel**: Inspect Macro-F1, Precision/Recall, and ECE calibration error.

---

## 📚 References & Research Background

This prototype builds upon and extends key insights from:
1. **Zheng et al.**, *"From Reviewers' Lens: Understanding Bug Bounty Report Invalid Reasons with LLMs"*.
2. **Cheng et al.**, *"VERCATION: Precise Vulnerable Open-Source Software Version Identification Based on Static Analysis and LLM"* (IEEE Transactions on Software Engineering 2026).

---

## 📜 License
Licensed under the [MIT License](LICENSE).
