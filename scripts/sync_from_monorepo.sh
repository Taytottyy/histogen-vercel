#!/usr/bin/env bash
# Copy HistoGen UI + demo data from the monorepo into this Vercel deploy bundle.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MONO="$(cd "$ROOT/.." && pwd)"
DEST_DATA="$ROOT/public/data/tcga_lung/representative_patients"

echo "Syncing from $MONO"

mkdir -p "$DEST_DATA"

# Cohort metadata
cp "$MONO/data/tcga_lung/representative_patients/representative_20_patients.json" "$DEST_DATA/"

# Visual report figures for the advisor demo
rsync -a --delete \
  "$MONO/data/tcga_lung/representative_patients/visual_report/" \
  "$DEST_DATA/visual_report/"

# Per-patient PHOENIX + slide assets (omit raw cells + diagnostic PNGs to save size)
mkdir -p "$DEST_DATA/data_package/per_patient"
for case_dir in "$MONO/data/tcga_lung/representative_patients/data_package/per_patient"/TCGA-*; do
  case_id="$(basename "$case_dir")"
  out="$DEST_DATA/data_package/per_patient/$case_id"
  mkdir -p "$out/slide_previews" "$out/phoenix_registration"

  for f in phoenix_summary.json phoenix_gene_summary.csv phoenix_spatial_heatmap.json; do
    [[ -f "$case_dir/$f" ]] && cp "$case_dir/$f" "$out/"
  done

  if [[ -d "$case_dir/slide_previews" ]]; then
    rsync -a "$case_dir/slide_previews/" "$out/slide_previews/"
  fi

  if [[ -f "$case_dir/phoenix_registration/phoenix_cells_registered.csv" ]]; then
    cp "$case_dir/phoenix_registration/phoenix_cells_registered.csv" "$out/phoenix_registration/"
  fi
  if [[ -f "$case_dir/phoenix_registration/registration.json" ]]; then
    cp "$case_dir/phoenix_registration/registration.json" "$out/phoenix_registration/"
  fi
done

# TCGA-05-4410: H&E thumbnail only (no PHOENIX atlas)
case_dir="$MONO/data/tcga_lung/representative_patients/data_package/per_patient/TCGA-05-4410"
if [[ -d "$case_dir/slide_previews" ]]; then
  out="$DEST_DATA/data_package/per_patient/TCGA-05-4410"
  mkdir -p "$out/slide_previews"
  rsync -a "$case_dir/slide_previews/" "$out/slide_previews/"
fi

# UI + API sources
cp "$MONO/ui/index.html" "$ROOT/public/index.html"
cp "$MONO/ui/patient_data.py" "$ROOT/api/patient_data.py"
cp "$MONO/ui/phoenix_data.py" "$ROOT/api/phoenix_data.py"
cp "$MONO/ui/cohort_figures.py" "$ROOT/api/cohort_figures.py"
cp "$MONO/ui/protein_cache.py" "$ROOT/api/protein_cache.py"
rsync -a --delete "$MONO/ui/demo_cache/" "$ROOT/api/demo_cache/"

echo "Re-applying Vercel path patches..."
python3 "$ROOT/scripts/patch_api_paths.py"

python3 "$ROOT/scripts/verify_bundle.py"
echo "Done. Bundle at $ROOT"
