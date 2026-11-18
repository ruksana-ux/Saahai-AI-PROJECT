# Backend

A read-only FastAPI service that distributes the citation-backed scheme dataset.

It is **not** in the critical path. The Android app ships the dataset and works
offline; this service only refreshes it.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness plus dataset version |
| GET | `/v1/schemes` | Summaries, optional `?category=` |
| GET | `/v1/schemes/{id}` | Full record with source and dates |

No write endpoints. No images. No document text. No accounts.

## Run

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Tests:

```bash
pytest backend/tests
```

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `SAHAAYA_DATASET` | `data/schemes/schemes.json` | Dataset path |
| `SAHAAYA_ALLOWED_ORIGINS` | empty | Comma-separated CORS origins; empty disables CORS |

## Caching

Responses carry an `ETag` derived from the dataset bytes. Clients send
`If-None-Match` and receive `304` when nothing changed.
