"""`wreck guard`: verhindert, dass Herstellermaterial, Schlüssel oder private Daten ins Repo gelangen.

Regeln siehe LEGAL.md. Der Prüfer ist absichtlich streng; berechtigte
Ausnahmen (eigene Testbilder o. Ä.) kommen mit Begründung in `.wreckallow`.
"""
from __future__ import annotations

import fnmatch
import re
import subprocess
from pathlib import Path

BLOCKED_EXT = {
    ".bin": "Firmware/Rohdaten",
    ".ufw": "Update-Container",
    ".img": "Abbild",
    ".hex": "Firmware (Intel-HEX)",
    ".elf": "Programm",
    ".o": "Objektdatei",
    ".a": "Bibliothek",
    ".so": "native Bibliothek",
    ".apk": "Android-App",
    ".xapk": "Android-App",
    ".apks": "Android-App",
    ".dex": "Android-Bytecode",
    ".smali": "dekompilierter Android-Code",
    ".jar": "Java-Archiv",
    ".jks": "Signaturschlüssel",
    ".keystore": "Signaturschlüssel",
    ".p12": "Schlüssel",
    ".pfx": "Schlüssel",
    ".pem": "Schlüssel/Zertifikat",
    ".key": "Schlüssel",
    ".dump": "Speicherabzug",
    ".gzf": "Ghidra-Projekt",
    ".gpr": "Ghidra-Projekt",
    ".rep": "Ghidra-Projekt",
}

CONTENT_RULES = [
    (re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"), "privater Schlüssel"),
    (re.compile(rb"^\.class [^\n]*L[\w/$]+;", re.M), "Smali-Code (dekompiliert)"),
    (re.compile(rb"/\* WARNING: (?:Removing unreachable block|Control flow encountered bad instruction)"), "Ghidra-Decompiler-Ausgabe"),
    (re.compile(rb"Decompiled with CFR|// Decompiled by|jadx(?:-gui)? [0-9.]+ decompiled", re.I), "Java-Decompiler-Ausgabe"),
    (re.compile(rb"Copyright[^\n]{0,40}(?:JIELI|Jieli|JieLi|Realtek|Actions Semiconductor|SiFli|Bluetrum)[^\n]{0,60}All Rights Reserved", re.I), "Hersteller-Quelltext ohne freie Lizenz"),
    (re.compile(rb"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), "Cloud-Zugangsschlüssel"),
    (re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "GitHub-Token"),
    (re.compile(rb"\b(?:[0-9A-F]{2}:){5}[0-9A-F]{2}\b"), "Bluetooth-/MAC-Adresse (persönliches Gerät?)"),
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
        if rel.startswith("tests/fixtures/") and p.suffix == ".py":
            continue
        ext = p.suffix.lower()
        if ext in BLOCKED_EXT:
            findings.append({"file": rel, "rule": "dateityp", "reason": BLOCKED_EXT[ext]})
            continue
        size = p.stat().st_size
        if size > MAX_SIZE:
            findings.append({"file": rel, "rule": "groesse", "reason": f"{size} Byte > {MAX_SIZE}: Rohdaten gehören nach private/"})
            continue
        data = p.read_bytes()[:TEXT_SCAN_LIMIT]
        if rel.endswith(("guard.py", "LEGAL.md")):
            continue  # enthalten die Muster selbst
        for rx, reason in CONTENT_RULES:
            if rx.search(data):
                findings.append({"file": rel, "rule": "inhalt", "reason": reason})
    return findings
