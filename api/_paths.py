"""Filesystem roots for the Vercel deploy bundle."""

from __future__ import annotations

from pathlib import Path

DEPLOY_ROOT = Path(__file__).resolve().parent.parent
API_DIR = DEPLOY_ROOT / "api"
PUBLIC_DIR = DEPLOY_ROOT / "public"
DATA_DIR = PUBLIC_DIR / "data"

PATIENTS_JSON = DATA_DIR / "tcga_lung/representative_patients/representative_20_patients.json"
PHOENIX_BUNDLE_ROOT = DATA_DIR / "tcga_lung/representative_patients/data_package/per_patient"
VISUAL_REPORT = DATA_DIR / "tcga_lung/representative_patients/visual_report"
CACHE_DIR = API_DIR / "demo_cache" / "gigatime_structures"
