"""`wreck guard`: keeps vendor material, keys and private data out of the repo.

Rules: see LEGAL.md. The checker is deliberately strict; justified exceptions
(your own test images etc.) go into `.wreckallow` with a reason.
"""
from __future__ import annotations

import fnmatch
import re
import subprocess
from pathlib import Path

BLOCKED_EXT = {
    ".bin": "firmware/raw data",
    ".ufw": "update container",
    ".img": "image",
    ".hex": "firmware (Intel HEX)",
    ".elf": "program",
    ".o": "object file",
    ".a": "library",
    ".so": "native library",
    ".apk": "Android app",
    ".xapk": "Android app",
    ".apks": "Android app",
    ".dex": "Android bytecode",
    ".smali": "decompiled Android code",
    ".jar": "Java archive",
    ".jks": "signing key",
    ".keystore": "signing key",
    ".p12": "key",
    ".pfx": "key",
    ".pem": "key/certificate",
    ".key": "key",
    ".dump": "memory dump",
    ".gzf": "Ghidra project",
    ".gpr": "Ghidra project",
    ".rep": "Ghidra project",
}

CONTENT_RULES = [
    (re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"), "private key"),
    (re.compile(rb"^\.class [^\n]*L[\w/$]+;", re.M), "Smali code (decompiled)"),
    (re.compile(rb"/\* WARNING: (?:Removing unreachable block|Control flow encountered bad instruction)"), "Ghidra decompiler output"),
    (re.compile(rb"Decompiled with CFR|// Decompiled by|jadx(?:-gui)? [0-9.]+ decompiled", re.I), "Java decompiler output"),
    (re.compile(rb"Copyright[^\n]{0,40}(?:JIELI|Jieli|JieLi|Realtek|Actions Semiconductor|SiFli|Bluetrum)[^\n]{0,60}All Rights Reserved", re.I), "vendor source without a free licence"),
    (re.compile(rb"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), "cloud access key"),
    (re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "GitHub token"),
    (re.compile(rb"\b(?:[0-9A-F]{2}:){5}[0-9A-F]{2}\b"), "Bluetooth/MAC address (personal device?)"),
]

MAX_SIZE = 2 * 1024 * 1024
TEXT_SCAN_LIMIT = 4 * 1024 * 1024
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", "private", ".pytest_cache", "build", "dist"}


def _allow_patterns(root: Path) -> list[str]:
    f = root / ".wreckallow"
    if not f.exists():
        return []
    pats = []
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            pats.append(line)
    return pats


def _git_files(root: Path, staged: bool) -> list[Path]:
    cmd = ["git", "-C", str(root), "diff", "--cached", "--name-only", "--diff-filter=ACMR"] if staged \
        else ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return [root / p for p in out.splitlines() if p]


def _walk(root: Path) -> list[Path]:
    files = []
    for p in root.rglob("*"):
        if p.is_file() and not any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            files.append(p)
    return files


def check(root: Path, staged: bool = False, use_git: bool = True) -> list[dict]:
    root = root.resolve()
    allow = _allow_patterns(root)
    try:
        files = _git_files(root, staged) if use_git else _walk(root)
    except (subprocess.CalledProcessError, FileNotFoundError):
        files = _walk(root)
    findings = []
    for p in files:
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(fnmatch.fnmatch(rel, a) for a in allow):
            continue
        ext = p.suffix.lower()
        if ext in BLOCKED_EXT:
            findings.append({"file": rel, "rule": "file-type", "reason": BLOCKED_EXT[ext]})
            continue
        size = p.stat().st_size
        if size > MAX_SIZE:
            findings.append({"file": rel, "rule": "size", "reason": f"{size} bytes > {MAX_SIZE}: raw data belongs in private/"})
            continue
        if rel.endswith(("guard.py", "LEGAL.md")):
            continue  # these contain the patterns themselves
        data = p.read_bytes()[:TEXT_SCAN_LIMIT]
        for rx, reason in CONTENT_RULES:
            if rx.search(data):
                findings.append({"file": rel, "rule": "content", "reason": reason})
    return findings
