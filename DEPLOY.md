# Deploy without Vercel (free)

The bundle is ~241 MB with PHOENIX CSVs — too heavy for some free static hosts and near Vercel’s hobby limit. **Render free tier** is the easiest fit: one **Python web service** serves the UI, API, and `/data` files.

## ⚠️ “Publish directory build does not exist!”

You created a **Static Site** by mistake. HistoGen is **not** a static export — it needs a **Web Service** (Python + FastAPI).

**Fix:**

1. In [Render Dashboard](https://dashboard.render.com), **delete** the failed Static Site.
2. Do **not** use “Static Site” or set Publish Directory to `build` / `public`.
3. Use one of the options below (**Blueprint** or **Web Service** only).

---

## Recommended: Blueprint → Web Service (free)

1. [render.com](https://render.com) → sign in with GitHub (**Taytottyy**).
2. **New +** → **Blueprint** (not Static Site).
3. Connect **`Taytottyy/histogen-vercel`**.
4. Render reads `render.yaml` and creates a **Web Service** named `histogen` (Free plan).
5. **Apply** → wait for build (several minutes — large repo).
6. Open the `.onrender.com` URL.

---

## Manual: Web Service (if Blueprint fails)

1. **New +** → **Web Service** (not Static Site).
2. Connect **`Taytottyy/histogen-vercel`**, branch `main`.
3. Settings:

| Field | Value |
|-------|--------|
| **Language** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app:app --app-dir api --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

4. **Environment** → add:

| Key | Value |
|-----|--------|
| `SERVE_STATIC` | `1` |
| `USE_PROTEIN_CACHE` | `1` |

5. **Create Web Service** — leave **Publish Directory** blank (that field is Static Site only).

Optional: `BIOHUB_API_KEY` for live protein fetches (demo cache works without it).

**Free tier:** sleeps after ~15 min idle; first wake can take 30–60 s.

---

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
