# Vizzy Backend API

FastAPI backend for the Vizzy data visualization application.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY if desired
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /api/upload` — Upload CSV/Excel file
- `GET /api/session/{id}` — Get session info
- `DELETE /api/session/{id}` — Delete session
- `GET /api/analyze/{id}/overview` — Quality + column stats
- `GET /api/analyze/{id}/nulls` — Null analysis
- `GET /api/analyze/{id}/distributions` — Histograms + boxplots
- `GET /api/analyze/{id}/correlations` — Correlation matrix
- `GET /api/analyze/{id}/categories` — Value counts
- `GET /api/analyze/{id}/timeseries` — Time series data
- `GET /api/analyze/{id}/preprocessing` — Preprocessing suggestions
- `GET /api/insights/{id}` — Stream AI insights (SSE)
- `POST /api/query/{id}` — Ask a question about the data
- `GET /api/export/{id}/pdf` — Download PDF report
- `GET /health` — Health check

## Tests

```bash
python -m pytest tests/ -v
```
