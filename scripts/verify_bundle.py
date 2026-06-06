#!/usr/bin/env python3
"""Validate the Vercel deploy bundle before push."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "public" / "data" / "tcga_lung" / "representative_patients"
MAX_MB = 250


def main() -> int:
    errors: list[str] = []

    required = [
        ROOT / "public" / "index.html",
        ROOT / "api" / "app.py",
        ROOT / "api" / "index.py",
        ROOT / "vercel.json",
        DATA / "representative_20_patients.json",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing file: {path.relative_to(ROOT)}")

    total = sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file())
    total_mb = total / 1024 / 1024
    print(f"bundle size: {total_mb:.1f} MB")

    if total_mb > MAX_MB:
        errors.append(
            f"bundle is {total_mb:.1f} MB — exceeds Vercel hobby limit (~{MAX_MB} MB). "
            "Use Vercel Pro or host public/data on external storage."
        )

    sys.path.insert(0, str(ROOT / "api"))
    from patient_data import load_representative_patients
    from phoenix_data import bundle_manifest, has_phoenix_bundle

    cohort = load_representative_patients()
    print(f"patients: {cohort['count']} · phoenix: {cohort['phoenixCount']}")

    for patient in cohort["patients"]:
        if not patient.get("phoenixAvailable"):
            continue
        cid = patient["caseId"]
        try:
            bundle_manifest(cid)
        except Exception as exc:
            errors.append(f"{cid}: {exc}")

    if errors:
        print("verification failed:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
