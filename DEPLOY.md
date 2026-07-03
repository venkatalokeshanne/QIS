# Deploying (free tier: Render backend + Vercel frontend + Neon Postgres)

This gets you a live, publicly-reachable app entirely on free tiers.
Render's free web services have **ephemeral disk** (anything written
to the container's filesystem is wiped on restart/redeploy/idle
spin-down), so the backend's data layer is configured to use a
free-tier hosted **Postgres** instead of local SQLite + local CSV
files — nothing is ever written to Render's own disk, so your data
survives regardless of what Render's container does.

**Local development is unaffected.** Leave `DATABASE_URL` unset on
your own machine and everything keeps working exactly as it has all
along (SQLite + local CSV files, same as every test in this repo).
`DATABASE_URL` only needs to be set in Render's environment.

**Important**: free-tier limits and signup terms change over time.
Verify Render's, Neon's, and Vercel's current free-tier terms when you
sign up — the steps below are the mechanics, not a pricing guarantee.

Everything in this file is something *you* run — account creation,
signups, and pushing code to a remote host aren't things I do on your
behalf.

---

## 0. Push this repo to GitHub

Render and Vercel both deploy most smoothly from a Git repo.

```bash
cd quant-platform-full
git init
git add -A
git commit -m "Initial commit"
```

Create an empty repo on [github.com/new](https://github.com/new)
(don't initialize it with a README), then:

```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

---

## 1. Create a free Postgres database (Neon)

1. Sign up at [neon.tech](https://neon.tech) (or [supabase.com](https://supabase.com) if you'd
   rather — either works, Neon is the more minimal "just a Postgres" option).
2. Create a project. Copy the connection string it gives you — it
   looks like `postgresql://user:password@host/dbname?sslmode=require`.
3. Keep this string handy for step 2 — treat it like a password, don't
   paste it anywhere public (not into a GitHub file, not into a chat).

---

## 2. Backend → Render

1. Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**,
   and point it at your GitHub repo. Render will detect `render.yaml`
   at the repo root (already written for you) and use it to configure
   the service automatically.
   - If you'd rather set it up by hand instead of via the blueprint:
     **New → Web Service** → your repo → set **Root Directory** to
     `backend`, **Runtime** to `Python 3`, **Build Command** to
     `pip install -r requirements.txt`, **Start Command** to
     `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, **Plan** to
     **Free**.
2. When it asks for the environment variables `render.yaml` declares
   (`TWELVEDATA_API_KEY`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`), fill in:
   - `TWELVEDATA_API_KEY` — your real key (same one from `backend/.env` locally)
   - `DATABASE_URL` — the Neon connection string from step 1
   - `CORS_ALLOWED_ORIGINS` — leave a placeholder like `["http://localhost:5173"]`
     for now; you'll update this in step 4 once you know your Vercel URL.
3. Deploy. Render gives you a URL like `https://quant-platform-backend.onrender.com`.

**Verify it's up:**

```bash
curl https://quant-platform-backend.onrender.com/api/health
# -> {"status":"ok"}
```

(Swap in your actual service name if Render assigned a different one —
free-tier service names must be globally unique on Render too.)

---

## 3. Frontend → Vercel

You mentioned you'll drive this part yourself — quick reference:

1. [vercel.com/new](https://vercel.com/new) → import the GitHub repo.
2. Set **Root Directory** to `frontend`.
3. Framework preset should auto-detect as **Vite**. Deploy.

`frontend/vercel.json` (already written) rewrites the frontend's
existing `/api/...` calls to your Render backend — no frontend code
changes needed. **One thing to check**: it currently points at
`https://quant-platform-backend.onrender.com`. If Render gave your
service a different name in step 2, edit the `destination` in
`frontend/vercel.json` to match, then redeploy on Vercel.

---

## 4. Close the loop: tell the backend about the frontend's URL

Once Vercel gives you your live frontend URL (something like
`https://your-app.vercel.app`), go back to the Render dashboard →
your service → **Environment** → update:

```
CORS_ALLOWED_ORIGINS = ["https://your-app.vercel.app"]
```

(Exact JSON-array syntax — quotes and brackets — matters here.) Saving
this triggers an automatic redeploy.

---

## 5. Verify end-to-end

1. Open your Vercel URL in a browser.
2. Daily Levels → Live tab → fetch a symbol (e.g. `AAPL`) — round-trips
   through Vercel's rewrite to Render to TwelveData and back.
3. Upload a dataset via the Upload page, then check it's still there
   a bit later (Render's free tier spins idle services down after
   inactivity) — this confirms Postgres is actually holding your data,
   not Render's ephemeral disk.

---

## Ongoing costs / limits to know about

- **Render free tier**: spins down after ~15 minutes of inactivity and
  cold-starts on the next request (a delay of maybe 30-60 seconds) —
  this is what keeps it free. Verify Render's current free-tier
  compute-hours allowance hasn't changed since you're reading this.
- **Neon/Supabase free tier**: both have generous permanent free
  allowances for a database this size, but do have storage/compute
  caps — check current numbers on their pricing pages.
- **Vercel's free tier** for static/SPA frontends is generally
  generous and unlikely to be the constraint here.
- **TwelveData's own API plan** still applies — this deployment
  doesn't change your API credit limits.
