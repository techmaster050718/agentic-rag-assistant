# Deployment Guide: Render + Vercel

This guide covers deploying the **Agentic RAG Assistant** with:
- **Supabase** — PostgreSQL + pgvector (vector store)
- **Render** — FastAPI backend
- **Vercel** — Next.js frontend

---

## Step 1: Supabase Setup

1. Go to [https://supabase.com](https://supabase.com) and create a new project.
2. In the Supabase Dashboard, navigate to **Database → Extensions** and enable `vector`.
3. Go to **SQL Editor** and run the migration script:

```bash
# Copy and paste the contents of:
backend/migrations/supabase_vector_setup.sql
```

4. After running, collect these credentials from **Project Settings → API**:
   - **Project URL** → `SUPABASE_URL`
   - **service_role key** → `SUPABASE_SERVICE_KEY`

5. Collect the **Direct Database URL** from **Project Settings → Database**:
   - Format: `postgresql+asyncpg://postgres:[password]@db.[ref].supabase.co:5432/postgres`
   - This is your `DATABASE_URL`

---

## Step 2: Render Backend Deployment

1. Go to [https://render.com](https://render.com) and connect your GitHub repo.
2. Create a new **Web Service** with these settings:

| Setting | Value |
|---|---|
| Runtime | Python |
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/api/v1/health` |

3. **Alternatively**, a `render.yaml` is already present at the root of the repo. Render will auto-detect it.

4. Add the following **Environment Variables** in the Render dashboard:

| Variable | Value |
|---|---|
| `DATABASE_URL` | Your Supabase direct DB URL |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Your Supabase service role key |
| `GOOGLE_API_KEY` | Your Google/Gemini API key |
| `ALLOWED_ORIGINS` | `https://your-app.vercel.app` |
| `SECRET_KEY` | A long random string |

5. Deploy. Note the Render URL (e.g. `https://agentic-rag-backend.onrender.com`).

---

## Step 3: Vercel Frontend Deployment

1. Go to [https://vercel.com](https://vercel.com) and import your GitHub repo.
2. Set **Root Directory** to `frontend`.
3. Add the following **Environment Variable**:

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | Your Render backend URL (e.g. `https://agentic-rag-backend.onrender.com`) |

4. Deploy.

---

## Step 4: Post-Deployment Verification

```bash
# Check backend health
curl https://your-render-url.onrender.com/api/v1/health

# Check documents list
curl https://your-render-url.onrender.com/api/v1/documents
```

---

## Notes

- Render's **free tier** spins down after inactivity. Expect a ~30s cold start.
- The Supabase free tier provides **500 MB** of database storage.
- Embeddings use **768 dimensions** (Gemini `gemini-embedding-001`).
- The `ivfflat` index requires at least **~1000 vectors** before it outperforms a full scan; `lists = 100` is appropriate for up to ~1M rows.
