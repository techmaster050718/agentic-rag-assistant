# Deployment Guide: Supabase + Render + Vercel

---

## Step 1 — Supabase Setup

### 1.1 Create Project
1. Go to [https://supabase.com](https://supabase.com) → New Project
2. Note your **Project URL** and **Project Ref** (e.g. `abcdefghijklmnop`)

### 1.2 Enable pgvector
1. Dashboard → **Database → Extensions**
2. Search `vector` → Enable

### 1.3 Run Migration SQL
1. Dashboard → **SQL Editor → New Query**
2. Paste entire contents of `backend/migrations/supabase_vector_setup.sql`
3. Click **Run**

### 1.4 Get Credentials

| What you need | Where to find it |
|---|---|
| `SUPABASE_URL` | Project Settings → API → Project URL |
| `SUPABASE_SERVICE_KEY` | Project Settings → API → **service_role** (secret) key ⚠️ |
| `DATABASE_URL` | Project Settings → Database → Connection String → **URI** (change `postgresql://` → `postgresql+asyncpg://`) |

> **⚠️ CRITICAL**: Use the `service_role` key, NOT the `anon`/`public` key. The anon key will give "Invalid API key" errors for backend operations.

---

## Step 2 — Render Backend Deployment

### 2.1 Connect Repo
1. [https://render.com](https://render.com) → New → Web Service
2. Connect your GitHub repo: `techmaster050718/agentic-rag-assistant`

### 2.2 Service Settings

| Setting | Value |
|---|---|
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Health Check Path** | `/api/v1/health` |

> **Note**: A `render.yaml` is already in the repo root — Render will auto-detect it.

### 2.3 Environment Variables

Set these in Render Dashboard → Environment:

| Variable | Value |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:...@db.xxx.supabase.co:5432/postgres` |
| `SUPABASE_URL` | `https://xxx.supabase.co` |
| `SUPABASE_SERVICE_KEY` | `eyJhbGci...` (service_role key) |
| `GOOGLE_API_KEY` | Your Gemini API key |
| `EMBEDDING_MODEL` | `models/gemini-embedding-001` |
| `LLM_MODEL` | `gemini-1.5-flash` |
| `ALLOWED_ORIGINS` | `https://your-app.vercel.app` |
| `ENVIRONMENT` | `production` |
| `SECRET_KEY` | Long random string |

### 2.4 ⚠️ Clear Build Cache (MANDATORY on first deploy)

Render caches pip installs. If you changed `requirements.txt`, you MUST clear the cache:

1. Render Dashboard → Your Service → **Settings**
2. Scroll to **Build & Deploy** → Click **"Clear build cache & deploy"**

OR: In the Deploy tab, click the three-dot menu → **"Clear build cache"**

### 2.5 Deploy
After setting env vars and clearing cache → **Manual Deploy → Deploy latest commit**

---

## Step 3 — Vercel Frontend Deployment

1. Go to [https://vercel.com](https://vercel.com) → Import Project
2. Select repo → Set **Root Directory** to `frontend`
3. Add Environment Variable:

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | Your Render URL (e.g. `https://agentic-rag-backend.onrender.com`) |

4. Deploy

---

## Step 4 — Verification

```bash
# 1. Backend health check
curl https://your-render-url.onrender.com/api/v1/health

# 2. List documents (should return empty array on fresh deploy)
curl https://your-render-url.onrender.com/api/v1/documents

# 3. Frontend should load and be able to call backend
open https://your-app.vercel.app
```

---

## Troubleshooting

| Error | Fix |
|---|---|
| `Invalid API key` | You used the `anon` key — switch to `service_role` key |
| `ModuleNotFoundError: psycopg2` | Your `DATABASE_URL` is missing `+asyncpg` — check and redeploy |
| `TypeError: proxy` | Old supabase version — requirements.txt is now fixed to `supabase==2.7.4` |
| `ResolutionImpossible` | httpx conflict — now pinned to `httpx==0.27.0`, clear Render build cache |
| Render uses old requirements | Click **"Clear build cache & deploy"** in Render Settings |
| `RuntimeError: Supabase client is not initialized` | `SUPABASE_URL` or `SUPABASE_SERVICE_KEY` env var is missing on Render |
| Cold start slow (~30s) | Normal on Render free tier — first request spins up the instance |

---

## Architecture Overview

```
Vercel (Next.js)
      │ HTTPS
      ▼
Render (FastAPI)  ──── Supabase PostgreSQL (pgvector)
      │                      ├── documents table
      │                      └── document_embeddings table (vector)
      │
      └──── Google Gemini API (LLM + Embeddings)
```
