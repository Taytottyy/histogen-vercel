# Deploy without Vercel (free)

The bundle is ~241 MB with PHOENIX CSVs — too heavy for some free static hosts and near Vercel’s hobby limit. **Render free tier** is the easiest fit: one Python web service serves the UI, API, and `/data` files.

## Recommended: Render (free)

1. Create account at [render.com](https://render.com) (GitHub login is fine).
2. **New → Blueprint**
3. Connect repo: **Taytottyy/histogen-vercel**
4. Render reads `render.yaml` and creates the **histogen** web service (free plan).
5. Click **Deploy** — first build takes a few minutes (large repo).
6. Open the URL Render gives you (e.g. `https://histogen.onrender.com`).

**Free tier behavior:** the app sleeps after ~15 minutes idle; first load after sleep takes ~30–60 s. Fine for demos and sharing a link.

Optional env in Render dashboard:

| Variable | Purpose |
|----------|---------|
| `BIOHUB_API_KEY` | Live protein structures (optional; demo cache works without it) |

## Manual Render setup (no Blueprint)

- **New → Web Service** → connect **Taytottyy/histogen-vercel**
- Runtime: **Python 3**
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app:app --app-dir api --host 0.0.0.0 --port $PORT`
- Env: `SERVE_STATIC=1`, `USE_PROTEIN_CACHE=1`
- Plan: **Free**

## Run locally (same as Render)

```bash
pip install -r requirements.txt
SERVE_STATIC=1 uvicorn app:app --app-dir api --host 127.0.0.1 --port 8080
```

Open http://127.0.0.1:8080

## Other free options

| Option | Pros | Cons |
|--------|------|------|
| **Render** (above) | Matches current FastAPI app; no refactor | Cold starts on free tier |
| **Fly.io** | Always-on possible on small VM | More setup (Docker/fly.toml) |
| **Oracle Cloud free VM** | Always on, full control | You manage Linux + systemd |
| **Cloudflare Tunnel** | Free public URL to laptop | Not “hosted”; machine must stay on |
| **GitHub Pages** | Free static | No Python API; major refactor |

## Not on free tiers

- **Vercel Hobby** — ~250 MB deploy cap; you’re at ~241 MB and may hit limits.
- **Railway** — very limited free credits now.
