# HistoGen — Vercel deploy

Standalone deploy bundle for the **HistoGen** dashboard (20-patient TCGA lung demo with PHOENIX spatial RNA, protein structures, and cohort advisor figures).

This repo is generated from [PEAT-Nucleate-BIoHack-2026](https://github.com/aonkondey01/PEAT-Nucleate-BIoHack-2026). Re-sync after monorepo UI/data changes:

```bash
bash scripts/sync_from_monorepo.sh
```

## What's included

| Path | Purpose |
|------|---------|
| `public/index.html` | HistoGen single-page UI |
| `public/data/` | 20-patient cohort JSON, H&E thumbnails, PHOENIX registered cells, cohort figures |
| `api/` | FastAPI serverless routes (`/api/patients`, `/api/phoenix`, `/api/protein`, …) |
| `api/demo_cache/` | Offline GigaTIME → ESM structure cache (20 markers) |

**PHOENIX:** 19/20 patients ship registered `thumb_x`/`thumb_y` coordinates. `TCGA-05-4410` has H&E only (absent from PHOENIX atlas).

## Deploy to Vercel

1. Push this folder to its own GitHub repository.
2. Import the repo in [Vercel](https://vercel.com/new).
3. Framework preset: **Other**
4. Add environment variables (optional):
   - `BIOHUB_API_KEY` — live Biohub protein fetches
   - `USE_PROTEIN_CACHE=1` — prefer bundled demo structures (default)
5. Deploy.

Local preview with the Vercel CLI:

```bash
npm i -g vercel
vercel dev
```

Open `http://localhost:3000`.

## Bundle size

The PHOENIX registered-cell CSVs make the bundle ~**240 MB**. That is near the Vercel **Hobby** deployment limit (~250 MB). Use **Vercel Pro** if deployment fails, or host `public/data/` on R2/S3 and update `/data/` URLs.

Verify before push:

```bash
python3 scripts/verify_bundle.py
```

## API routes

- `GET /api/health`
- `GET /api/patients/cohort`
- `GET /api/patients/{caseId}`
- `GET /api/phoenix/{caseId}`
- `GET /api/phoenix/{caseId}/expression?gene=CD8A`
- `GET /api/phoenix/{caseId}/heatmap`
- `GET /api/protein/structure?gene=CD8A`
- `GET /api/agent/cohort-figures`

Static assets are served from `public/` at `/` and `/data/…`.

## Not included

- Full `.svs` whole-slide images (~824 GB cohort)
- PHOENIX atlas `.h5ad` (~23 GB)
- Haiku Patient Explorer Vite app (separate UI under monorepo `ui/haiku-patient-explorer/`)
