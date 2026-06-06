"""Load PHOENIX per-patient spatial readout bundles for the RNA viewer."""

from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from _paths import DATA_DIR, DEPLOY_ROOT, PHOENIX_BUNDLE_ROOT as BUNDLE_ROOT

COORD_SKIP = {
    "cell_id",
    "x",
    "y",
    "phoenix_x",
    "phoenix_y",
    "thumb_x_affine",
    "thumb_y_affine",
    "thumb_x",
    "thumb_y",
    "slide_x_l0",
    "slide_y_l0",
}


def bundle_dir(case_id: str) -> Path:
    return BUNDLE_ROOT / case_id


def has_phoenix_bundle(case_id: str) -> bool:
    return (bundle_dir(case_id) / "phoenix_summary.json").is_file()


@lru_cache(maxsize=8)
def load_summary(case_id: str) -> dict[str, Any]:
    path = bundle_dir(case_id) / "phoenix_summary.json"
    if not path.is_file():
        raise FileNotFoundError(f"No PHOENIX bundle for {case_id!r}")
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_gene_summary_row(row: dict[str, str]) -> dict[str, Any]:
    mean_raw = row.get("mean") or row.get("mean_readout")
    if mean_raw in (None, ""):
        raise KeyError(f"gene summary row for {row.get('gene')!r} missing mean/mean_readout")
    mean = float(mean_raw)
    nonzero_raw = row.get("nonzero_fraction") or row.get("nonzeroFraction") or "0"
    max_raw = row.get("max") or row.get("max_readout") or mean_raw
    return {
        "gene": row["gene"],
        "mean": mean,
        "nonzeroFraction": float(nonzero_raw),
        "max": float(max_raw),
    }


@lru_cache(maxsize=8)
def load_gene_summary(case_id: str) -> list[dict[str, Any]]:
    path = bundle_dir(case_id) / "phoenix_gene_summary.csv"
    if not path.is_file():
        raise FileNotFoundError(f"No gene summary for {case_id!r}")
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append(_parse_gene_summary_row(row))
    rows.sort(key=lambda item: item["mean"], reverse=True)
    return rows


def _preview_path(case_id: str, kind: str) -> Path | None:
    previews = bundle_dir(case_id) / "slide_previews"
    if not previews.is_dir():
        return None
    matches = sorted(previews.glob(f"{case_id}*.{kind}.png"))
    return matches[0] if matches else None


@lru_cache(maxsize=8)
def thumbnail_size(case_id: str) -> tuple[int, int]:
    for kind in ("thumbnail", "tissue_crop"):
        path = _preview_path(case_id, kind)
        if path and path.is_file():
            from PIL import Image

            with Image.open(path) as image:
                return image.size
    return (1536, 1334)


def _registered_cells_path(case_id: str) -> Path | None:
    path = bundle_dir(case_id) / "phoenix_registration" / "phoenix_cells_registered.csv"
    return path if path.is_file() else None


def _coordinate_source(case_id: str) -> tuple[Path, str, str, str]:
    registered = _registered_cells_path(case_id)
    if registered:
        return registered, "thumb_x", "thumb_y", "registered"
    return bundle_dir(case_id) / "phoenix_cells.csv", "x", "y", "phoenix_raw"


def _bounds_for_source(case_id: str, coord_source: str) -> dict[str, float]:
    if coord_source == "registered":
        thumb_w, thumb_h = thumbnail_size(case_id)
        return {"xMin": 0.0, "yMin": 0.0, "xMax": float(thumb_w), "yMax": float(thumb_h)}

    summary = load_summary(case_id)
    extent = summary.get("spatial_extent") or summary.get("spatialBounds") or {}
    return {
        "xMin": float(extent.get("x_min", extent.get("xMin", 0))),
        "yMin": float(extent.get("y_min", extent.get("yMin", 0))),
        "xMax": float(extent.get("x_max", extent.get("xMax", 1))),
        "yMax": float(extent.get("y_max", extent.get("yMax", 1))),
    }


def _available_genes(case_id: str) -> list[str]:
    return [row["gene"] for row in load_gene_summary(case_id)]


def _phoenix_to_thumbnail(x_phx: float, y_phx: float, case_id: str) -> tuple[float, float]:
    raise FileNotFoundError(
        f"Raw PHOENIX affine mapping requires WSI files (not bundled on Vercel) for {case_id!r}. "
        "Use registered phoenix_cells_registered.csv instead."
    )


def get_expression(case_id: str, gene: str) -> dict[str, Any]:
    genes = _available_genes(case_id)
    if gene not in genes:
        raise KeyError(f"Gene {gene!r} not in PHOENIX panel for {case_id}")

    cells_path, x_col, y_col, coord_source = _coordinate_source(case_id)
    bounds = _bounds_for_source(case_id, coord_source)
    xs: list[float] = []
    ys: list[float] = []
    values: list[float] = []

    with cells_path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            x_val = float(row[x_col])
            y_val = float(row[y_col])
            if coord_source == "phoenix_raw":
                x_val, y_val = _phoenix_to_thumbnail(x_val, y_val, case_id)
            xs.append(x_val)
            ys.append(y_val)
            values.append(float(row[gene]))

    return {
        "caseId": case_id,
        "gene": gene,
        "nCells": len(values),
        "bounds": bounds,
        "coordinateSource": coord_source,
        "min": min(values) if values else 0.0,
        "max": max(values) if values else 0.0,
        "mean": sum(values) / len(values) if values else 0.0,
        "x": xs,
        "y": ys,
        "value": values,
    }


def bundle_manifest(case_id: str) -> dict[str, Any]:
    summary = load_summary(case_id)
    genes = load_gene_summary(case_id)
    _, _, _, coord_source = _coordinate_source(case_id)
    bounds = _bounds_for_source(case_id, coord_source)
    thumb_w, thumb_h = thumbnail_size(case_id)
    crop = _preview_path(case_id, "tissue_crop")
    thumb = _preview_path(case_id, "thumbnail")
    registration = summary.get("registration") or {}
    asset_base = f"/data/tcga_lung/representative_patients/data_package/per_patient/{case_id}/slide_previews"

    return {
        "caseId": case_id,
        "study": summary.get("study"),
        "nCells": summary.get("n_cells", summary.get("nCells")),
        "nGenes": summary.get("n_genes", summary.get("nGenes")),
        "bounds": bounds,
        "thumbnailSize": {"width": thumb_w, "height": thumb_h},
        "coordinateSource": coord_source,
        "coordinateSystem": "thumbnail_px" if coord_source == "registered" else summary.get("coordinateSystem", "phoenix_20x"),
        "registration": registration.get("metrics"),
        "genes": [row["gene"] for row in genes],
        "topGenes": genes[:24],
        "assets": {
            "tissueCrop": f"{asset_base}/{crop.name}" if crop else None,
            "thumbnail": f"{asset_base}/{thumb.name}" if thumb else None,
        },
        "source": "PHOENIX TCGA atlas · inferred virtual spatial transcriptomics",
    }
