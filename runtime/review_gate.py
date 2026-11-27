#!/usr/bin/env python3
"""Painel determinístico de revisão do VACINA 01.

Ele produz recomendação técnica auditável. Não publica, não faz merge e não
concede aprovação clínica, estética ou editorial.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "AGENTS.md",
    "config/decisao_atual.json",
    "docs/ORQ_00_CONTRATO_OPERACIONAL.md",
    "runtime/orq_v2.py",
    "src/orq.py",
    "tests",
    "jobs/R05_MAVIE_REBOOT.json",
    ".github/workflows/qa-motor.yml",
]
MEDIA_SUFFIXES = {".mp4", ".mov", ".mkv", ".avi", ".mp3", ".wav", ".m4a", ".aac", ".png", ".jpg", ".jpeg", ".webp"}
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?:ghp|github_pat|xox[baprs])-[-A-Za-z0-9_]{12,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
]


def command(label: str, args: list[str]) -> dict:
    started = time.monotonic()
    try:
        proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=180)
        output = (proc.stdout + proc.stderr).strip()
        return {
            "label": label,
            "command": " ".join(args),
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "returncode": proc.returncode,
            "duration_seconds": round(time.monotonic() - started, 3),
            "output_tail": output[-1800:],
        }
    except Exception as exc:  # pragma: no cover - defensive CI reporting
        return {
            "label": label,
            "command": " ".join(args),
            "status": "FAIL",
            "returncode": None,
            "duration_seconds": round(time.monotonic() - started, 3),
            "output_tail": f"{type(exc).__name__}: {exc}",
        }


def changed_files() -> tuple[list[str], str]:
    base = os.environ.get("GITHUB_BASE_SHA")
    head = os.environ.get("GITHUB_SHA", "HEAD")
    candidates = []
    if base:
        candidates.append(["git", "diff", "--name-only", "--diff-filter=ACMRT", base, head])
    candidates.append(["git", "diff", "--name-only", "--diff-filter=ACMRT", "HEAD^", head])
    for args in candidates:
        proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
        if proc.returncode == 0:
            return [x for x in proc.stdout.splitlines() if x], " ".join(args)
    return [], "unavailable"


def security_scan(files: list[str]) -> dict:
    findings: list[str] = []
    for rel in files:
        path = ROOT / rel
        if path.suffix.lower() in MEDIA_SUFFIXES:
            findings.append(f"arquivo de mídia no diff: {rel}")
            continue
        if any(part.lower() in {".env", "secrets", "credentials", "prontuario"} for part in path.parts):
            findings.append(f"caminho sensível no diff: {rel}")
            continue
        if not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"padrão potencialmente sensível em: {rel}")
                break
    return {"status": "PASS" if not findings else "FAIL", "findings": findings}


def markdown(report: dict) -> str:
    verdict = report["verdict"]
    lines = [
        "# VACINA 01 — Painel de revisão técnica",
        "",
        f"- Veredito: **{verdict}**",
        "- Aprovação humana final: **OBRIGATÓRIA**",
        f"- Commit: `{report['commit']}`",
        "",
        "## Gates",
    ]
    for item in report["commands"]:
        lines.append(f"- `{item['label']}`: **{item['status']}**")
    lines.append(f"- `segurança e privacidade`: **{report['security']['status']}**")
    lines += ["", "## Limites", "- Este painel não aprova clínica, estética, publicação, gasto, contato externo ou merge."]
    if report["blockers"]:
        lines += ["", "## Bloqueios"] + [f"- {x}" for x in report["blockers"]]
    else:
        lines += ["", "## Bloqueios", "- Nenhum bloqueio técnico determinístico encontrado."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="reports/PR_REVIEW_GATES.json")
    args = parser.parse_args()

    missing = [item for item in REQUIRED if not (ROOT / item).exists()]
    files, diff_command = changed_files()
    security = security_scan(files)
    commands = [
        command("testes de gates", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        command("validacao DISCOVERY", [sys.executable, "src/orq.py", "validate", "jobs/R05_MAVIE_REBOOT.json", "DISCOVERY"]),
        command("diagnostico ORQ-00", [sys.executable, "runtime/orq_v2.py", "run", "--stage", "DIAGNOSTICO", "--out", "/tmp/CI_REVIEW_ORQ00.json"]),
    ]
    blockers = [f"arquivo obrigatório ausente: {item}" for item in missing]
    blockers += security["findings"]
    blockers += [f"{item['label']} retornou {item['returncode']}" for item in commands if item["status"] != "PASS"]
    report = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "base_commit": os.environ.get("GITHUB_BASE_SHA"),
        "diff_command": diff_command,
        "changed_files": files,
        "commands": commands,
        "security": security,
        "blockers": blockers,
        "verdict": "TECHNICAL_APPROVAL_CANDIDATE" if not blockers else "BLOCKED",
        "human_approval_required": True,
        "side_effects": {"publish": False, "merge": False, "external_contact": False, "spend": False},
    }
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(markdown(report))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
