"""
Git Analyzer Module
Inspects Git history, resolves commits and tags, and evaluates version-aware claim status.
"""

import os
import subprocess
from typing import Dict, List, Optional, Tuple
from .schema import VersionStatus


class GitAnalyzer:
    def __init__(self, repo_dir: str):
        self.repo_dir = repo_dir
        self.is_git_repo = os.path.exists(os.path.join(repo_dir, ".git"))

    def _run_git(self, args: List[str]) -> Tuple[int, str]:
        if not self.is_git_repo:
            return 1, ""
        try:
            res = subprocess.run(["git"] + args, cwd=self.repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return res.returncode, res.stdout.strip()
        except Exception as e:
            return 1, str(e)

    def get_head_commit(self) -> str:
        code, out = self._run_git(["rev-parse", "HEAD"])
        return out[:7] if code == 0 else "UNKNOWN"

    def get_tags(self) -> Dict[str, str]:
        tags = {}
        code, out = self._run_git(["tag", "-l"])
        if code == 0 and out:
            for tag in out.splitlines():
                c_code, c_out = self._run_git(["rev-parse", tag])
                if c_code == 0:
                    tags[tag] = c_out[:7]
        return tags

    def search_log(self, keyword: str) -> List[Dict[str, str]]:
        matches = []
        code, out = self._run_git(["log", "--grep", keyword, "--oneline"])
        if code == 0 and out:
            for line in out.splitlines():
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    matches.append({"commit": parts[0], "message": parts[1]})
        return matches

    def search_code_history(self, search_term: str) -> List[Dict[str, str]]:
        # git log -S search_term
        code, out = self._run_git(["log", "-S", search_term, "--oneline"])
        history = []
        if code == 0 and out:
            for line in out.splitlines():
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    history.append({"commit": parts[0], "message": parts[1]})
        return history

    def get_commit_diff(self, commit_hash: str) -> str:
        code, out = self._run_git(["show", commit_hash])
        return out if code == 0 else ""
