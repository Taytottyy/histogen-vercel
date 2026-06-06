#!/usr/bin/env python3
"""Re-apply Vercel-specific path patches after copying from the monorepo."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "api"


def patch_patient_data(text: str) -> str:
    old = """REPO_ROOT = Path(__file__).resolve().parent.parent
PATIENTS_JSON = REPO_ROOT / "data/tcga_lung/representative_patients/representative_20_patients.json"
PHOENIX_BUNDLE_ROOT = REPO_ROOT / "data/tcga_lung/representative_patients/data_package/per_patient\""""
    new = """from _paths import DEPLOY_ROOT, PATIENTS_JSON, PHOENIX_BUNDLE_ROOT"""
    text = text.replace(old, new)
    return text.replace('relative_to(REPO_ROOT)', 'relative_to(DEPLOY_ROOT)')


def patch_phoenix_data(text: str) -> str:
    old = """REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLE_ROOT = REPO_ROOT / "data/tcga_lung/representative_patients/data_package/per_patient"
PHOENIX_DIR = REPO_ROOT / "data/phoenix\""""
    new = """from _paths import DATA_DIR, DEPLOY_ROOT, PHOENIX_BUNDLE_ROOT as BUNDLE_ROOT"""
    text = text.replace(old, new)
    text = text.replace("import sys\n", "")
    start = text.find("def _phoenix_to_thumbnail")
    end = text.find("\n\n\ndef get_expression")
    if start != -1 and end != -1:
        stub = '''def _phoenix_to_thumbnail(x_phx: float, y_phx: float, case_id: str) -> tuple[float, float]:
    raise FileNotFoundError(
        f"Raw PHOENIX affine mapping requires WSI files (not bundled on Vercel) for {case_id!r}. "
        "Use registered phoenix_cells_registered.csv instead."
    )
'''
        text = text[:start] + stub + text[end + 1 :]
    return text


def patch_cohort_figures(text: str) -> str:
    old = """REPO_ROOT = Path(__file__).resolve().parent.parent
VISUAL_REPORT = REPO_ROOT / "data/tcga_lung/representative_patients/visual_report"
SELECTED_DIR = VISUAL_REPORT / "selected figures"
MANIFEST_PATH = SELECTED_DIR / "manifest.json"
SUMMARY_PATH = VISUAL_REPORT / "cohort_visual_summary.json\""""
    new = """from _paths import DATA_DIR, VISUAL_REPORT, SELECTED_DIR, SUMMARY_PATH

MANIFEST_PATH = SELECTED_DIR / "manifest.json\""""
    return text.replace(old, new)


def patch_protein_cache(text: str) -> str:
    return text.replace(
        """UI_DIR = Path(__file__).resolve().parent
CACHE_DIR = UI_DIR / "demo_cache" / "gigatime_structures\"""",
        "from _paths import CACHE_DIR",
    )


def main() -> int:
    patches = {
        "patient_data.py": patch_patient_data,
        "phoenix_data.py": patch_phoenix_data,
        "cohort_figures.py": patch_cohort_figures,
        "protein_cache.py": patch_protein_cache,
    }
    for name, fn in patches.items():
        path = API / name
        path.write_text(fn(path.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"patched {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
