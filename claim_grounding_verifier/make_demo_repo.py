"""
Generator for Controlled Local Demo Repository
Creates git commits, files, symbols, call chains, and patch history.
"""

import os
import subprocess
import shutil

DEMO_REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "demo_repo"))


def run_git(args, cwd):
    res = subprocess.run(["git"] + args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Git command failed: git {' '.join(args)}\nError: {res.stderr}")
    return res.stdout.strip()


def remove_readonly(func, path, exc_info):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def create_demo_repository():
    if os.path.exists(DEMO_REPO_DIR):
        shutil.rmtree(DEMO_REPO_DIR, onerror=remove_readonly)

    
    os.makedirs(os.path.join(DEMO_REPO_DIR, "src"), exist_ok=True)
    
    # Initialize Git Repo
    run_git(["init"], DEMO_REPO_DIR)
    run_git(["config", "user.name", "Security Triager"], DEMO_REPO_DIR)
    run_git(["config", "user.email", "triager@example.com"], DEMO_REPO_DIR)

    # File 1: src/util.c
    util_c = """#include <stdio.h>
#include <string.h>

void copy_payload(char *dest, const char *src, size_t len) {
    if (len > 512) len = 512;
    memcpy(dest, src, len);
}
"""
    with open(os.path.join(DEMO_REPO_DIR, "src", "util.c"), "w", encoding="utf-8") as f:
        f.write(util_c)

    # File 2: src/parser.c (v1.0.0 - with vulnerable_copy)
    parser_c_v1 = """#include <stdio.h>
#include "util.h"

void vulnerable_copy(char *dest, const char *src) {
    // Unsafe copy
    sprintf(dest, "%s", src);
}

int parse_packet(const char *packet_data, size_t size) {
    char buffer[512];
    vulnerable_copy(buffer, packet_data);
    copy_payload(buffer, packet_data, size);
    return 0;
}
"""
    with open(os.path.join(DEMO_REPO_DIR, "src", "parser.c"), "w", encoding="utf-8") as f:
        f.write(parser_c_v1)

    run_git(["add", "."], DEMO_REPO_DIR)
    c1 = run_git(["commit", "-m", "Initial release v1.0.0 with packet parsing"], DEMO_REPO_DIR)
    run_git(["tag", "-a", "v1.0.0", "-m", "Release 1.0.0"], DEMO_REPO_DIR)

    # Commit 2: Fix patch (v1.1.0)
    parser_c_v2 = """#include <stdio.h>
#include "util.h"

int parse_packet(const char *packet_data, size_t size) {
    char buffer[512];
    // Replaced vulnerable_copy with bound-checked copy_payload
    copy_payload(buffer, packet_data, size);
    return 0;
}
"""
    with open(os.path.join(DEMO_REPO_DIR, "src", "parser.c"), "w", encoding="utf-8") as f:
        f.write(parser_c_v2)

    run_git(["add", "."], DEMO_REPO_DIR)
    c2 = run_git(["commit", "-m", "Fix buffer overflow vulnerability: removed vulnerable_copy and added bound checks"], DEMO_REPO_DIR)
    run_git(["tag", "-a", "v1.1.0", "-m", "Release 1.1.0 patched"], DEMO_REPO_DIR)

    head_commit = run_git(["rev-parse", "HEAD"], DEMO_REPO_DIR)
    v1_commit = run_git(["rev-parse", "v1.0.0"], DEMO_REPO_DIR)

    print(f"[+] Demo Repository Created Successfully at: {DEMO_REPO_DIR}")
    print(f"    - v1.0.0 Commit: {v1_commit[:7]}")
    print(f"    - v1.1.0 Commit (HEAD): {head_commit[:7]}")

    return {
        "repo_dir": DEMO_REPO_DIR,
        "v1_commit": v1_commit,
        "head_commit": head_commit
    }


if __name__ == "__main__":
    create_demo_repository()
