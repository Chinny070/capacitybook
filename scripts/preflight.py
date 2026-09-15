#!/usr/bin/env python3
from pathlib import Path
import py_compile
import sys

ROOT = Path(__file__).resolve().parents[1]
FAILURES = []


def check(condition: bool, message: str):
    if not condition:
        FAILURES.append(message)


for relative in ("contracts/capacitybook.py", "contracts/capacity_guard.py"):
    try:
        py_compile.compile(str(ROOT / relative), doraise=True)
    except Exception as exc:
        FAILURES.append(f"syntax compile failed for {relative}: {exc}")

files = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts and p.suffix not in {".pyc"}]
corpus = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in files)

check("61999" in corpus, "StudioNet chain ID 61999 is not pinned anywhere")
forbidden_chain = "619" + "97"
check(forbidden_chain not in corpus, "forbidden chain ID is present; this package must target 61999 only")
forbidden_network = "studionet" + "-dev"
check(forbidden_network not in corpus, "forbidden studio dev-network alias is present; this package must target 61999 only")
submission_text = (ROOT / "SUBMISSION.md").read_text(encoding="utf-8")
has_placeholder = "PENDING_OWNER_DEPLOYMENT" in submission_text
has_real_address = "CapacityBook address: `0x" in submission_text
check(
    has_placeholder or has_real_address,
    "SUBMISSION.md must either keep PENDING_OWNER_DEPLOYMENT placeholders or contain real 0x deployment addresses",
)

contract = (ROOT / "contracts/capacitybook.py").read_text(encoding="utf-8")
guard = (ROOT / "contracts/capacity_guard.py").read_text(encoding="utf-8")

for marker in (
    "gl.vm.run_nondet_default",
    "validator_fn",
    "gl.nondet.web.render",
    "gl.nondet.exec_prompt",
    "try_admit",
    "windows_overlap",
    "is_admitted",
):
    check(marker in contract, f"main contract missing required marker: {marker}")

check("capacitybook.view().is_effective" in guard, "consumer IC does not call CapacityBook admission view")
check("action was already executed" in guard, "consumer IC is missing replay protection")

secret_markers = ("PRIVATE" + "_KEY=", "MNEMONIC" + "=", "SEED" + "_PHRASE=", "API" + "_KEY=sk-")
for forbidden in secret_markers:
    check(forbidden not in corpus, f"possible secret marker found: {forbidden}")

if FAILURES:
    print("PREFLIGHT FAILED")
    for failure in FAILURES:
        print(f"- {failure}")
    sys.exit(1)

print("PREFLIGHT PASSED")
print(f"checked_files={len(files)}")
print("network=StudioNet")
print("chain_id=61999")
print("frontend=none")
