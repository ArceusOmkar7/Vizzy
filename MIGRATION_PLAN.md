# Vizzy: Migration Plan — Streamlit → FastAPI + React

> **Status**: Plan only — no code changes. Awaiting approval before implementation.
> 
> This document is the deliverable for [Issue #1](https://github.com/ArceusOmkar7/Vizzy/issues/1).

---

## Table of Contents
1. [Current Architecture Summary](#1-current-architecture-summary)
2. [Migration Architecture](#2-migration-architecture)
3. [Feature Improvements](#3-feature-improvements)
4. [Migration Order (Phased)](#4-migration-order-phased)
5. [What NOT to Change](#5-what-not-to-change)
6. [Open Questions](#6-open-questions)

---

## 1. Current Architecture Summary

### Module Map

| Module | Location | Responsibility |
|--------|----------|----------------|
| **App Entry** | `app.py` | Page config, sidebar layout, 8-tab navigation, metric display, PDF export trigger |
| **File Loader** | `utils/file_loader.py` | CSV/Excel ingestion with `@st.cache_data`, encoding fallback (UTF-8 → Latin-1) |
| **Data Checks** | `utils/data_checks.py` | Column classification (numeric/categorical/datetime/boolean), null analysis, outlier detection (IQR + Z-score), datetime inference |
| **Quality Engine** | `utils/quality_engine.py` | 5-dimension quality scoring (Completeness 25%, Consistency 20%, Accuracy 25%, Uniqueness 15%, Validity 15%), A–F grading |
| **Preprocessing Engine** | `utils/preprocessing_suggestions.py` | 8-category preprocessing recommendations with priority scores and auto-generated Python code snippets |
| **Insights Generator** | `utils/insights_generator.py` | Gemini API integration: builds a structured prompt from extracted data stats, calls `gemini-pro`, returns bullet-point insights |
| **PDF Report** | `utils/pdf_report.py` | Beta ReportLab-based PDF generation |
| **State Management** | `utils/state_management.py` | Session state helpers |
| **Theming** | `style.py` | 13 named color palettes, `apply_global_style()` (Streamlit CSS injection), `apply_chart_theme()`, `get_color_palette()` |
| **Components** (8) | `components/` | One Streamlit tab per file: data_overview, missing_values, distributions, correlations, categorical, time_series, preprocessing, insights, color_settings |
| **Visuals** (7) | `visuals/` | Pure chart factories returning `plt.Figure` or `go.Figure`: categories, correlation, distributions, nulls, preprocessing (Plotly), quality_score (Plotly), summary, time_series |
| **Sample Data** | `sample_data/` | 5 CSV files (sales, student, messy, high-cardinality, time-series) |

### Data Flow (Current)

```
Browser Upload
      │
      ▼
app.py → file_loader.load_data() ─────────────────────────────────────────┐
                    │ @st.cache_data (keyed on file hash)                  │
                    ▼                                                       │
            pd.DataFrame                                                    │
                    │                                                       │
          ┌─────────┴──────────────────────────────────────────────┐       │
          ▼                                                         ▼       │
   components/*.py                                         utils/*.py       │
   (UI + chart calls)                                   (analysis engines) │
          │                                                         │       │
          └────────────────► visuals/*.py ◄───────────────────────┘       │
                             (plt/plotly)                                   │
                                   │                                        │
                                   └──► st.pyplot() / st.plotly_chart() ◄──┘
```

### What Gemini Does Currently

1. `extract_data_insights(df)` builds a rich stats dict (shape, dtypes, null %, quality scores, correlations, recommendations).
2. `create_insights_prompt(df, insights)` assembles a ~2000-token system prompt from that dict.
3. `generate_llm_insights(df)` calls `genai.GenerativeModel("gemini-pro").generate_content(prompt)` — a **single, blocking, non-streamed** call.
4. The response text is split on `\n` and rendered as bullet points.
5. Key limitations: no chat/follow-up, no streaming, no NL query capability, no chart suggestion.

### Current Stack Versions
- `streamlit ≥ 1.46.0`, `pandas ≥ 2.3.0`, `numpy ≥ 2.2.6`
- `plotly ≥ 6.2.0`, `matplotlib ≥ 3.10.0`, `seaborn ≥ 0.13.2`
- `scikit-learn ≥ 1.7.0`, `scipy ≥ 1.11.0`, `statsmodels ≥ 0.14.4`
- `google-generativeai ≥ 0.3.0`, `reportlab ≥ 4.0.0`, `python-dotenv ≥ 1.0.0`

---

## 2. Migration Architecture

### Top-Level Folder Structure

```
Vizzy/
├── backend/                  ← FastAPI application
│   ├── app/
│   │   ├── main.py           ← FastAPI app factory, CORS, routers
│   │   ├── routers/
│   │   │   ├── upload.py     ← POST /api/upload
│   │   │   ├── analyze.py    ← GET  /api/analyze/{session_id}/*
│   │   │   ├── insights.py   ← GET  /api/insights/{session_id} (SSE)
│   │   │   ├── query.py      ← POST /api/query/{session_id}
│   │   │   └── export.py     ← GET  /api/export/{session_id}/pdf
│   │   ├── services/
│   │   │   ├── data_service.py         ← wraps file_loader, data_checks, quality_engine
│   │   │   ├── insights_service.py     ← wraps insights_generator (Gemini)
│   │   │   ├── preprocessing_service.py← wraps preprocessing_suggestions
│   │   │   └── export_service.py       ← wraps pdf_report
│   │   ├── models/
│   │   │   ├── upload.py     ← UploadResponse, SessionInfo
│   │   │   ├── analysis.py   ← QualityReport, ColumnStats, NullReport, etc.
│   │   │   └── insights.py   ← InsightResponse, QueryRequest, QueryResponse
│   │   ├── core/
│   │   │   ├── config.py     ← settings (Pydantic BaseSettings), .env loading
│   │   │   ├── session.py    ← in-memory session store (DataFrame cache)
│   │   │   └── exceptions.py ← custom HTTP exceptions
│   │   └── utils/            ← (migrated from current utils/, no Streamlit deps)
│   │       ├── file_loader.py
│   │       ├── data_checks.py
│   │       ├── quality_engine.py
│   │       ├── preprocessing_suggestions.py
│   │       ├── insights_generator.py
│   │       ├── pdf_report.py
│   │       └── chart_data.py ← NEW: converts DataFrames to JSON-serializable chart data
│   ├── tests/
│   │   ├── test_upload.py
│   │   ├── test_analyze.py
│   │   └── test_insights.py
│   ├── requirements.txt      ← (no streamlit)
│   ├── .env.example
│   └── README.md
│
├── frontend/                 ← React + Tailwind application
│   ├── public/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api/
│   │   │   └── client.js     ← Axios/fetch wrapper, base URL from env
│   │   ├── pages/
│   │   │   ├── HomePage.jsx            ← upload + landing
│   │   │   └── DashboardPage.jsx       ← 8-tab analysis dashboard
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   ├── TopBar.jsx
│   │   │   │   └── TabNav.jsx
│   │   │   ├── upload/
│   │   │   │   ├── FileUploader.jsx
│   │   │   │   └── DatasetMetrics.jsx
│   │   │   ├── tabs/
│   │   │   │   ├── DataOverview.jsx
│   │   │   │   ├── MissingValues.jsx
│   │   │   │   ├── Distributions.jsx
│   │   │   │   ├── Correlations.jsx
│   │   │   │   ├── Categories.jsx
│   │   │   │   ├── TimeSeries.jsx
│   │   │   │   ├── Preprocessing.jsx
│   │   │   │   └── AIInsights.jsx
│   │   │   ├── charts/
│   │   │   │   ├── BarChart.jsx
│   │   │   │   ├── HeatmapChart.jsx
│   │   │   │   ├── HistogramChart.jsx
│   │   │   │   ├── BoxPlot.jsx
│   │   │   │   ├── LineChart.jsx
│   │   │   │   ├── PieChart.jsx
│   │   │   │   ├── GaugeChart.jsx
│   │   │   │   └── NetworkGraph.jsx
│   │   │   ├── shared/
│   │   │   │   ├── QualityBadge.jsx
│   │   │   │   ├── MetricCard.jsx
│   │   │   │   ├── LoadingSpinner.jsx
│   │   │   │   ├── ErrorBoundary.jsx
│   │   │   │   ├── ColorPalettePicker.jsx
│   │   │   │   └── DownloadButton.jsx
│   │   │   └── ai/
│   │   │       ├── InsightStream.jsx   ← SSE streaming display
│   │   │       ├── QueryInput.jsx
│   │   │       └── InsightCard.jsx
│   │   ├── hooks/
│   │   │   ├── useFileUpload.js
│   │   │   ├── useAnalysis.js
│   │   │   ├── useInsightStream.js     ← SSE hook
│   │   │   ├── useColorPalette.js
│   │   │   └── useSessionId.js
│   │   ├── store/
│   │   │   └── sessionStore.js         ← Zustand or Context store
│   │   ├── styles/
│   │   │   └── index.css               ← Tailwind base + custom tokens
│   │   └── utils/
│   │       ├── formatters.js
│   │       └── chartHelpers.js
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── .env.example
│   └── package.json
│
├── sample_data/              ← unchanged
├── .gitignore
└── README.md                 ← updated to describe new architecture
```

### FastAPI Route Layout

| Method | Path | Handler | Migrated from |
|--------|------|---------|---------------|
| `POST` | `/api/upload` | `upload.py` | `file_loader.load_data()` |
| `GET` | `/api/session/{id}` | `upload.py` | `get_file_info()` |
| `GET` | `/api/analyze/{id}/overview` | `analyze.py` | `quality_engine`, `data_checks`, `summary.py` visuals |
| `GET` | `/api/analyze/{id}/nulls` | `analyze.py` | `analyze_null_values()`, `nulls.py` visuals |
| `GET` | `/api/analyze/{id}/distributions` | `analyze.py` | `distributions.py` visuals |
| `GET` | `/api/analyze/{id}/correlations` | `analyze.py` | `correlation.py` visuals |
| `GET` | `/api/analyze/{id}/categories` | `analyze.py` | `categories.py` visuals |
| `GET` | `/api/analyze/{id}/timeseries` | `analyze.py` | `time_series.py` visuals |
| `GET` | `/api/analyze/{id}/preprocessing` | `analyze.py` | `preprocessing_suggestions.py` |
| `GET` | `/api/insights/{id}` | `insights.py` | `insights_generator.py` (SSE stream) |
| `POST` | `/api/query/{id}` | `query.py` | NEW — NL query |
| `GET` | `/api/export/{id}/pdf` | `export.py` | `pdf_report.py` |
| `DELETE` | `/api/session/{id}` | `upload.py` | session cleanup |

#### Session Management
- On upload: server parses file, assigns a `session_id` (UUID), stores the DataFrame in an in-memory dict (or Redis for production).
- All subsequent requests use `session_id` as a path parameter — the DataFrame is never re-uploaded.
- Session TTL: 30 minutes of inactivity (configurable).

### React Component Tree

```
App
├── Router
│   ├── "/" → HomePage
│   │   └── FileUploader
│   │       └── DropZone + progress bar
│   └── "/dashboard/:sessionId" → DashboardPage
│       ├── Sidebar
│       │   ├── DatasetMetrics (rows, cols, memory, nulls)
│       │   ├── ColorPalettePicker
│       │   └── DownloadButton (PDF export)
│       ├── TopBar (file name, quality grade badge)
│       └── TabNav
│           ├── DataOverview     → /api/analyze/{id}/overview
│           ├── MissingValues    → /api/analyze/{id}/nulls
│           ├── Distributions    → /api/analyze/{id}/distributions
│           ├── Correlations     → /api/analyze/{id}/correlations
│           ├── Categories       → /api/analyze/{id}/categories
│           ├── TimeSeries       → /api/analyze/{id}/timeseries
│           ├── Preprocessing    → /api/analyze/{id}/preprocessing
│           └── AIInsights       → /api/insights/{id} (SSE)
```

### File Upload and Data State Flow

```
User selects file
       │
       ▼
FileUploader.jsx → POST /api/upload (multipart/form-data)
       │
       ▼
Backend parses → stores DataFrame → returns { session_id, file_info }
       │
       ▼
Frontend stores session_id in sessionStore (Zustand / Context)
       │
       ▼
Router pushes to /dashboard/:sessionId
       │
       ▼
Each tab component calls its own analysis endpoint using session_id
(lazy-loaded: only fetches when tab is first activated)
```

Key decision: **the DataFrame lives on the server**, not the client. The frontend only stores the `session_id`. This avoids large JSON serialisation overhead and keeps business logic in Python.

### Gemini Streaming (SSE)

```
AIInsights.jsx
    │
    ├── useInsightStream(sessionId)
    │       │
    │       └── EventSource("/api/insights/{sessionId}")
    │                   │
    │                   └── FastAPI StreamingResponse (text/event-stream)
    │                               │
    │                               └── genai.stream_generate_content(prompt)
    │                                   → yields chunks as SSE "data:" lines
    │
    └── Renders incremental text as each chunk arrives
```

This replaces the current blocking `generate_content()` call. The Gemini SDK's streaming API (`stream=True`) will be used to forward chunks directly to the browser via SSE — no polling required.

**Cost note**: Streaming does not increase token cost; it only changes delivery latency.

### Existing Python Logic → New Location

| Current | New |
|---------|-----|
| `utils/file_loader.py` (no Streamlit) | `backend/app/utils/file_loader.py` — remove `@st.cache_data` |
| `utils/data_checks.py` (no Streamlit) | `backend/app/utils/data_checks.py` — unchanged |
| `utils/quality_engine.py` | `backend/app/utils/quality_engine.py` — unchanged |
| `utils/preprocessing_suggestions.py` | `backend/app/utils/preprocessing_suggestions.py` — unchanged |
| `utils/insights_generator.py` | `backend/app/utils/insights_generator.py` — remove all `st.*` calls, add streaming |
| `utils/pdf_report.py` | `backend/app/utils/pdf_report.py` — return `bytes` not Streamlit download |
| `style.py` + `visuals/*.py` | `backend/app/utils/chart_data.py` — **convert** chart figures to JSON-serializable data (Plotly `.to_json()` or raw arrays for Recharts) |
| `components/*.py` | `frontend/src/components/tabs/*.jsx` — full rewrite in React |

---

## 3. Feature Improvements

### 3.1 AI / LLM

- [ ] **[S]** Use `gemini-1.5-flash` instead of `gemini-pro` (cheaper, faster, same quality for this use case)
- [ ] **[S]** Add streaming via SSE (replaces blocking call — better UX at no extra cost)
- [ ] **[M]** Multi-turn chat: persist conversation history in session, allow follow-up questions about the dataset
- [ ] **[M]** NL query interface: "Show top 10 rows by revenue" → backend runs `df.nlargest(10, 'revenue')` and returns table JSON *(increases API calls proportionally to usage)*
- [ ] **[M]** Chart type suggestion: include column dtypes + cardinality in prompt, have Gemini suggest the most appropriate visualization for a selected column
- [ ] **[M]** Smarter prompt: include sample rows (5 rows), correlation pairs, and top outliers — gives Gemini more concrete signals *(slight token increase per request, ~$0.0001–$0.001 more per call)*
- [ ] **[L]** Automated insight refresh: compare current insights against a previous upload of the same schema, highlight differences *(doubles API calls for diffed sessions)*
- [ ] **[L]** Anomaly narration: ask Gemini to describe specific outlier rows in plain English

### 3.2 Visualizations

- [ ] **[S]** Replace Plotly server-side rendering with **Recharts** (React-native, lighter, no server round-trip for each chart interaction)
- [ ] **[S]** Add chart export: PNG/SVG download button on every chart (Recharts `toCanvas` or `svg-to-image`)
- [ ] **[M]** Interactive drilldowns: click a bar → filter the dataset to that category across all other tabs
- [ ] **[M]** Correlation scatter matrix: click a heatmap cell → open scatter plot for that variable pair
- [ ] **[M]** Add a **violin plot** option alongside box plots for richer distribution view
- [ ] **[M]** Time-series zoom/pan with a range slider (Recharts `ReferenceArea` or `Brush` component)
- [ ] **[L]** Animated transitions when color palette changes
- [ ] **[L]** Configurable dashboard layout (drag-and-drop chart panels) — `react-grid-layout`

### 3.3 Data Handling

- [ ] **[S]** Support multi-sheet Excel upload (let user pick which sheet)
- [ ] **[M]** Multi-file upload: join/append two datasets with a column selector
- [ ] **[M]** In-browser column filtering / search: React table with client-side filtering (no server round-trip for each filter)
- [ ] **[M]** Column-level stats side panel: click any column header → slide-out panel with full stats
- [ ] **[M]** Data type override: let user re-cast a column's dtype before analysis (e.g., force "year" from int → category)
- [ ] **[L]** Large file support: server-side chunked reading with progress feedback (>10 MB files)
- [ ] **[L]** On-the-fly sampling toggle: user can switch between full dataset and random sample view

### 3.4 UI / UX

- [ ] **[S]** Dark mode toggle (Tailwind `dark:` classes + `prefers-color-scheme` detection)
- [ ] **[S]** Responsive layout: sidebar collapses to icon rail on narrow screens
- [ ] **[M]** Landing page redesign: hero section explaining features, drag-and-drop upload zone, sample dataset quick-load buttons
- [ ] **[M]** Dashboard header with file name, row/column counts, quality grade badge (coloured A–F), and upload time
- [ ] **[M]** Animated quality score gauge on first load
- [ ] **[M]** Toast notifications (upload success, error, insights ready) using a lightweight library (e.g., `react-hot-toast`)
- [ ] **[L]** Onboarding walkthrough for first-time users (e.g., `react-joyride`)
- [ ] **[L]** Keyboard navigation for tab switching

### 3.5 Code Quality

- [ ] **[S]** Full type hints on all Python functions (Pydantic models for API I/O)
- [ ] **[S]** Remove top-level Streamlit side-effect in `insights_generator.py` (line 17: `st.radio(...)` at module level — this is a bug)
- [ ] **[S]** Centralize all hardcoded values (Gemini model name, max rows, session TTL) into `backend/app/core/config.py` (Pydantic `BaseSettings`)
- [ ] **[M]** React `ErrorBoundary` around every tab component — prevents one tab's chart error from crashing the dashboard
- [ ] **[M]** API error handling: standardised `{ error: string, code: string }` JSON response on all 4xx/5xx
- [ ] **[M]** Input validation: file size limit (configurable, default 50 MB), MIME type check, max columns guard
- [ ] **[L]** PropTypes or TypeScript for all React components (prefer TS if starting fresh)

### 3.6 Developer Experience (DX)

- [ ] **[S]** `backend/.env.example` with all required/optional variables and comments
- [ ] **[S]** `frontend/.env.example` with `VITE_API_BASE_URL`
- [ ] **[S]** Add `pytest` + `pytest-asyncio` for backend; `Vitest` + `@testing-library/react` for frontend
- [ ] **[S]** Pre-commit hooks: `black` + `isort` + `ruff` for backend; `eslint` + `prettier` for frontend
- [ ] **[M]** Write integration tests for every FastAPI route (upload → analyze cycle)
- [ ] **[M]** GitHub Actions CI: lint + test on every PR
- [ ] **[M]** Docker Compose: `backend` + `frontend` (nginx) services for local dev parity
- [ ] **[L]** OpenAPI docs auto-generated by FastAPI — document every endpoint with example responses
- [ ] **[L]** Storybook for React shared components

---

## 4. Migration Order (Phased)

### Phase 1 — Working Skeleton (FE + BE connected, file upload working)

Goal: A user can upload a CSV and see the Data Overview tab rendered in React.

1. Bootstrap `backend/` with FastAPI: `main.py`, CORS config, health check endpoint.
2. Copy `utils/` to `backend/app/utils/`, strip all `import streamlit` and `@st.cache_data` references.
3. Implement `POST /api/upload` — parse file, store DataFrame in session dict, return `session_id` + basic file info.
4. Implement `GET /api/analyze/{id}/overview` — return quality score, column stats as JSON.
5. Bootstrap `frontend/` with Vite + React + Tailwind.
6. Build `FileUploader.jsx` → calls `/api/upload` → stores `session_id`.
7. Build `DataOverview.jsx` → calls `/api/analyze/{id}/overview` → renders metrics and a simple table.
8. Wire up React Router: `HomePage` → `DashboardPage`.
9. End-to-end smoke test: upload `sales_data.csv`, see quality grade in browser.

### Phase 2 — Feature Parity with Current Streamlit App

Goal: All 8 tabs work in React; Gemini insights stream; PDF export works.

1. Implement remaining analysis endpoints:
   - `/api/analyze/{id}/nulls`
   - `/api/analyze/{id}/distributions`
   - `/api/analyze/{id}/correlations`
   - `/api/analyze/{id}/categories`
   - `/api/analyze/{id}/timeseries`
   - `/api/analyze/{id}/preprocessing`
2. Convert `visuals/*.py` chart functions to return JSON-serializable data (Plotly `.to_json()` for initial pass).
3. Build all 7 remaining tab components in React using Recharts (or Plotly.js initially for speed).
4. Implement SSE streaming: `GET /api/insights/{id}` + `useInsightStream` hook + `InsightStream.jsx`.
5. Implement `GET /api/export/{id}/pdf` → return PDF bytes.
6. Add `ColorPalettePicker` with session-scoped palette preference.
7. Add sidebar with `DatasetMetrics` + palette picker + PDF export button.
8. Verify all 5 sample datasets render correctly.

### Phase 3 — New Features Beyond Current State

Goal: Ship improvements that meaningfully exceed the Streamlit version.

1. **Dark mode** (Tailwind dark: classes, toggle in TopBar).
2. **NL query** (`POST /api/query/{id}` + `QueryInput.jsx`).
3. **Multi-turn chat** in AI Insights tab.
4. **Chart type suggestion** from Gemini (S effort once NL query is in place).
5. **Interactive drilldowns** (click a category bar → filter across tabs).
6. **Column-level stats side panel**.
7. **CI/CD pipeline** (GitHub Actions: lint + test + Docker build).
8. **Multi-sheet Excel support**.

---

## 5. What NOT to Change

These patterns work well and should be preserved exactly:

| What | Why |
|------|-----|
| **All analysis algorithms** in `utils/data_checks.py`, `quality_engine.py`, `preprocessing_suggestions.py` | Correct, well-tested, no Streamlit dependency — direct port only |
| **5-dimension quality scoring** weights and A–F grade thresholds | Consistent with user expectations set by current app |
| **IQR + Z-score outlier detection** logic | Statistically sound; configurable threshold |
| **Datetime inference** heuristic (70% confidence threshold) | Works well in practice; worth preserving |
| **Auto window-size selection** for rolling statistics | Good UX default; keep the `[7,30,90]` / `[3,7,14]` thresholds |
| **Color palette system** (13 named palettes, `get_color_palette()`) | Power-user feature; migrate to frontend with same palette definitions |
| **Gemini optional (graceful degradation)** | Critical UX requirement — AI tab must work (with a "configure API key" prompt) when `GEMINI_API_KEY` is absent |
| **5 sample CSV datasets** | Useful for demos and testing; keep in `sample_data/` |
| **File size sampling** (>10k rows → random sample) | Performance guard that matters for large files |

---

## 6. Open Questions

These need a decision from the owner before implementation starts:

| # | Question | Options | Recommendation |
|---|----------|---------|----------------|
| 1 | **Chart library for frontend?** | Recharts, Victory, Plotly.js, Chart.js | **Recharts** — React-native, active community, sufficient for all current chart types |
| 2 | **Session storage backend?** | In-memory dict, Redis, SQLite + file cache | **In-memory for MVP**, Redis for production (add as Phase 3 optional) |
| 3 | **Session TTL?** | 15 min / 30 min / 1 hr | **30 minutes** — matches typical analysis session |
| 4 | **Auth?** | None, API key, OAuth | **None for MVP** — single-user local tool; flag if multi-user is needed |
| 5 | **Deployment target?** | Local only, Docker, cloud (Render/Railway/Fly.io) | Suggest **Docker Compose** for self-hosting; keep options open |
| 6 | **TypeScript for frontend?** | Yes / No | **Yes** — small incremental cost, large long-term benefit; use `vite` with `react-ts` template |
| 7 | **Gemini model version?** | `gemini-pro`, `gemini-1.5-flash`, `gemini-1.5-pro` | **`gemini-1.5-flash`** — fastest, cheapest, adequate quality; make it configurable via env |
| 8 | **File size limit?** | 10 MB / 50 MB / unlimited | **50 MB** configurable via `MAX_UPLOAD_SIZE_MB` env var |
| 9 | **Multi-user support now?** | Yes / No | **No for Phase 1** — session dict is per-process; flag if needed |
| 10 | **PDF export — keep or drop?** | Keep (beta) / Drop / Improve | **Keep in Phase 2** with a "beta" label; improve in Phase 3 with chart images |

---

*Plan prepared after full audit of all source files. No code or files were created beyond this document. Ready for owner review and approval.*
