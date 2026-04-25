# Fashion.io

A **Generative AI–powered fashion product search and recommendation platform** built with a Vue 3 SPA frontend and a Python Flask REST API backend. Natural-language queries are semantically ranked against a live product catalogue by Google Gemini (`gemini-flash-2.0`), returning a relevance-ordered list of matching garments.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Tech Stack](#tech-stack)
3. [Repository Layout](#repository-layout)
4. [Data & Request Flow](#data--request-flow)
5. [API Reference](#api-reference)
6. [AI / LLM Pipeline](#ai--llm-pipeline)
7. [Environment Variables](#environment-variables)
8. [Local Development Setup](#local-development-setup)
   - [Backend](#backend)
   - [Frontend](#frontend)
9. [Configuration](#configuration)
10. [Known Limitations & Engineering Notes](#known-limitations--engineering-notes)
11. [Security Considerations](#security-considerations)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Browser (Client)                           │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Vue 3 SPA  (App.vue)                      │  │
│  │                                                              │  │
│  │  ┌────────────────┐   axios POST /api/search   ┌──────────┐ │  │
│  │  │  Search Input  │ ─────────────────────────► │  Flask   │ │  │
│  │  │  (v-model)     │ ◄───────────────────────── │  :5000   │ │  │
│  │  └────────────────┘   JSON { products: [...] } └────┬─────┘ │  │
│  │                                                      │       │  │
│  │  ┌──────────────────────────────────┐                │       │  │
│  │  │  Product Grid (CSS Grid layout)  │                │       │  │
│  │  │  Card × N  (image, name, price,  │                │       │  │
│  │  │  description, CTA button)        │                │       │  │
│  │  └──────────────────────────────────┘                │       │  │
│  └──────────────────────────────────────────────────────┼───────┘  │
└─────────────────────────────────────────────────────────┼───────────┘
                                                          │
                              ┌───────────────────────────┘
                              │
               ┌──────────────▼──────────────┐
               │        Flask Backend         │
               │                             │
               │  1. GET products from        │
               │     Fake Store API  ──────►  │  https://fakestoreapi.com
               │                             │
               │  2. Build Gemini prompt with │
               │     product list + user      │
               │     query                    │
               │                     ──────► │  Google Gemini API
               │  3. Parse ranked product IDs │  (gemini-flash-2.0)
               │     from LLM response        │
               │                             │
               │  4. Filter & transform       │
               │     product objects          │
               │                             │
               │  5. Return JSON response     │
               └─────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Frontend framework | Vue 3 | `^3.2.26` |
| HTTP client | Axios | `^0.24.0` |
| Frontend router | Vue Router | `^4.0.12` |
| Frontend toolchain | @vue/cli-service | `~4.5.15` |
| Linter | ESLint + eslint-plugin-vue | `^7.32.0` / `^8.0.3` |
| Backend framework | Flask | `2.0.1` |
| Cross-origin requests | flask-cors | `3.0.10` |
| Outbound HTTP | requests | `2.26.0` |
| Environment config | python-dotenv | `0.19.0` |
| Generative AI SDK | google-generativeai | `0.3.1` |
| LLM model | Gemini flash 2.0 | `gemini-flash-2.0` |
| Product data source | Fake Store API | public REST API |

---

## Repository Layout

```
Fashion.io/
├── index.html          # HTML shell – mounts the Vue app on <div id="app">
├── vue.js              # Vue app entry point (createApp + mount)
├── App.vue             # Single-file component: template + script + scoped CSS
├── backend.py          # Flask application – all REST endpoints + Gemini logic
├── package.json        # Node dependencies and npm scripts
├── requirements.txt    # Python dependencies
└── .gitignore
```

The project is intentionally minimal: a single-page Vue 3 app with no build-step separation between `src/` and `public/`. The `index.html` loads `vue.js` directly, which in turn imports and mounts `App.vue`.

---

## Data & Request Flow

### Search flow (`POST /api/search`)

```
User types query  →  keyup.enter OR click "Search"
        │
        ▼
App.vue: searchProducts()
  - sets loading = true
  - axios.post('http://localhost:5000/api/search', { query })
        │
        ▼
backend.py: search_products()
  ├─ 1. requests.GET https://fakestoreapi.com/products/category/clothing
  │       → JSON array of product objects
  │
  ├─ 2. Build Gemini prompt:
  │       "Here are products: [...]. Query: '<user query>'.
  │        Return JSON array of relevant product IDs ranked by relevance."
  │
  ├─ 3. model.generate_content(prompt)
  │       → LLM response text  (expected: "[1, 4, 7, ...]")
  │
  ├─ 4. eval(result.text)  →  Python list of IDs
  │
  ├─ 5. Filter original product list to matching IDs
  │
  └─ 6. Transform each product:
          { id, name (← title), price (float), image, description }
        → jsonify({ products: [...] })
        │
        ▼
App.vue receives products array
  - renders into CSS Grid of <ProductCard> divs
  - loading = false
```

### Product detail flow (`GET /api/product/<id>`)

```
Client  →  GET /api/product/{id}
              │
              ▼
        requests.GET https://fakestoreapi.com/products/{id}
              │
              ▼
        Transform: { id, name, price, image, description, category }
              │
              ▼
        jsonify({ product: {...} })
```

> **Note:** The frontend `View Details` button does not yet call this endpoint — it is scaffolded for future use.

---

## API Reference

### `POST /api/search`

Performs an AI-ranked semantic search over the clothing catalogue.

**Request body** (`application/json`)

```json
{
  "query": "casual summer dress with floral pattern"
}
```

**Response** `200 OK`

```json
{
  "products": [
    {
      "id": 15,
      "name": "MBJ Womens Solid Short Sleeve Boat Neck V ...",
      "price": 9.85,
      "image": "https://fakestoreapi.com/img/...",
      "description": "95% RAYON 5% SPANDEX ..."
    }
  ]
}
```

**Error response** `500`

```json
{ "error": "<exception message>" }
```

---

### `GET /api/product/<int:product_id>`

Fetches a single product by its catalogue ID.

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `product_id` | integer | Fake Store API product ID |

**Response** `200 OK`

```json
{
  "product": {
    "id": 15,
    "name": "MBJ Womens Solid Short Sleeve Boat Neck V ...",
    "price": 9.85,
    "image": "https://fakestoreapi.com/img/...",
    "description": "95% RAYON 5% SPANDEX ...",
    "category": "women's clothing"
  }
}
```

**Error response** `404`

```json
{ "error": "Product not found" }
```

---

## AI / LLM Pipeline

The semantic search relies entirely on Google Gemini acting as a **zero-shot ranker**.

1. **Catalogue fetch** — The full clothing category (`/products/category/clothing`) is fetched fresh on every request. There is no caching layer.

2. **Prompt construction** — A single-turn prompt is built that includes:
   - The raw product JSON array (id, title, price, image, description, category).
   - The user's free-text query.
   - An instruction to return *only* a JSON array of ranked product IDs.

3. **Structured output parsing** — The model's text response is parsed with Python's built-in `eval()`. The backend expects a valid Python list literal (e.g., `[3, 7, 2]`).

4. **Post-filtering** — The original product list is filtered to the IDs returned by Gemini, preserving the LLM's ranking order.

**Model:** `gemini-flash-2.0`  
**SDK:** `google-generativeai==0.3.1`  
**Call type:** `model.generate_content(prompt)` (synchronous, single-turn)

---

## Environment Variables

Create a `.env` file in the project root (alongside `backend.py`):

```dotenv
# Required – Google Gemini API key
GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here

# Optional – Bearer token for the fashion product API
# Leave unset when using the public Fake Store API (no auth required)
FASHION_API_KEY=
```

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_GEMINI_API_KEY` | **Yes** | Authenticates calls to the Google Generative AI API |
| `FASHION_API_KEY` | No | Bearer token injected into the `Authorization` header of product catalogue requests |

> The backend uses `python-dotenv` to load these at startup via `load_dotenv()`.

---

## Local Development Setup

### Prerequisites

- Python ≥ 3.9
- Node.js ≥ 16 and npm ≥ 8
- A Google Cloud project with the Generative Language API enabled and a valid API key

---

### Backend

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env             # or create .env manually (see above)
# → set GOOGLE_GEMINI_API_KEY

# 4. Start the development server
python backend.py
# Flask runs on http://localhost:5000 with debug=True
```

---

### Frontend

```bash
# 1. Install Node dependencies
npm install

# 2. Start the Vue dev server (hot-reload enabled)
npm run serve
# Served on http://localhost:8080 by default

# Build for production
npm run build

# Lint source files
npm run lint
```

> The frontend hardcodes the backend origin as `http://localhost:5000`. Update `App.vue` line 58 when deploying to non-local environments.

---

## Configuration

| Setting | Location | Default | Notes |
|---|---|---|---|
| Backend host / port | `backend.py` line 95 | `localhost:5000` | `app.run(debug=True)` |
| Backend API origin (frontend) | `App.vue` line 58 | `http://localhost:5000` | Hard-coded Axios base URL |
| Product catalogue URL | `backend.py` line 19 | `https://fakestoreapi.com/products/category/clothing` | Replace with a real fashion API |
| Gemini model | `backend.py` line 16 | `gemini-flash-2.0` | Swap for `gemini-pro` or other variants |
| CORS policy | `backend.py` line 11 | Allow all origins (`*`) | Restrict in production |

---

## Known Limitations & Engineering Notes

| # | Issue | Impact | Notes |
|---|---|---|---|
| 1 | `eval()` used on LLM output | **High** – arbitrary code execution risk | Replace with `json.loads()` and add a regex guard to strip markdown fences before parsing |
| 2 | No response caching | Medium – full catalogue fetch + Gemini call on every search | Add Redis or in-process TTL cache for the product catalogue |
| 3 | `FASHION_API_KEY` injected even when `None` | Low – sends `Authorization: Bearer None` header to Fake Store API | Guard with `if FASHION_API_KEY` before setting the header |
| 4 | Frontend API origin is hard-coded | Medium – breaks in any non-localhost deployment | Externalise to `VUE_APP_API_BASE_URL` environment variable |
| 5 | No input validation on `query` | Low – empty strings propagate to Gemini | Already short-circuited in `App.vue` but not validated on the server side |
| 6 | `debug=True` in production | High – exposes interactive debugger | Gate on `FLASK_ENV` / `FLASK_DEBUG` env var |
| 7 | Fake Store API as product source | Medium – limited catalogue, no real fashion data | Intended as a drop-in placeholder; replace `FASHION_API_URL` with a real provider |
| 8 | Synchronous Gemini call blocks the Flask thread | Medium – poor throughput under concurrent load | Use `asyncio` + `async def` routes, or run behind a WSGI server (Gunicorn + gevent) |

---

## Security Considerations

- **`eval()` on LLM output** is the most critical issue. Even with a well-crafted prompt, a model can return unexpected text. Migrate to:
  ```python
  import json, re
  raw = result.text.strip().strip("```json").strip("```")
  relevant_product_ids = json.loads(raw)
  ```
- **API keys** must never be committed to source control. Verify `.env` is listed in `.gitignore`.
- **CORS** is currently open to all origins. In production, restrict to the specific frontend domain:
  ```python
  CORS(app, resources={r"/api/*": {"origins": "https://your-domain.com"}})
  ```
- **Flask debug mode** must be disabled in production to prevent the Werkzeug interactive debugger from being exposed.
