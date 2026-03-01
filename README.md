# GIS Anomaly Detector

A full-stack geospatial intelligence tool that validates OpenStreetMap (OSM) data by detecting statistically anomalous locations using unsupervised machine learning, then leverages Claude AI to generate human-readable risk assessments for each flagged entry.

**[Live Demo](https://kristianhoward.github.io/GIS-Anomaly-Detector)**

---

## What It Does

Given any city name, the application:

1. Fetches all named amenities and the road network from OpenStreetMap
2. Engineers spatial features for every location (road proximity, isolation, density, building intersections)
3. Runs `IsolationForest` to surface the statistically unusual locations
4. Sends the top anomalies to Claude AI for contextual risk analysis
5. Renders an interactive map with pop-up AI explanations — deployed to GitHub Pages as a zero-backend static site via WebAssembly

The result is a tool that could help a GIS analyst quickly prioritize which locations in a city's dataset warrant a closer look — whether that's a misplaced point, a data entry error, or a genuinely suspicious entity.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | [Marimo](https://marimo.io/) reactive notebook, [Folium](https://python-visualization.github.io/folium/) |
| Backend | [FastAPI](https://fastapi.tiangolo.com/), Python 3.11+ |
| Geospatial | [OSMnx](https://osmnx.readthedocs.io/), [GeoPandas](https://geopandas.org/), [Shapely](https://shapely.readthedocs.io/) |
| ML | [scikit-learn](https://scikit-learn.org/) `IsolationForest`, `StandardScaler` |
| AI | [Anthropic Claude](https://www.anthropic.com/) (`claude-opus-4-6`) |
| Deployment | GitHub Actions, GitHub Pages (WASM export) |

---

## Architecture

The project is split into two independently deployable units — a FastAPI backend and a Marimo WASM frontend — connected by an installable Python client library.

```
GIS-Anomaly-Detector/
│
├── api/                         # Installable client library (pip install .)
│   ├── dataset.py               # AnomalyDetectorConn: HTTP client for all server endpoints
│   └── constants.py             # Shared constants: DATA_HEADERS, COUNTRY_CODES
│
├── server/                      # FastAPI backend (uvicorn, not packaged)
│   ├── main.py                  # Route definitions
│   └── api/
│       ├── anomaly_detection.py # CityData: OSM ingestion, feature engineering, IsolationForest
│       ├── claude_client.py     # ClaudeClient: prompt construction, response parsing
│       ├── utilities.py         # CRS conversion (UTM), geometry helpers
│       └── constants.py         # Server-local tags and column headers
│
├── apps/
│   └── application.py           # Marimo notebook UI → exported as WASM for GitHub Pages
│
├── tests/                       # pytest integration tests (require live server)
└── .github/workflows/
    └── deploy.yml               # CI/CD: export WASM + deploy to GitHub Pages
```

### Data Flow

```
User enters city name
        │
        ▼
FastAPI /anomaly endpoint
        │
        ├─► osmnx.features_from_place()   → named amenities (GeoDataFrame)
        ├─► osmnx.graph_from_place()      → drivable road network (MultiDiGraph)
        │
        ▼
CityData: Feature Engineering (UTM meters)
        │
        ├─► distance to nearest road edge
        ├─► distance to nearest named amenity
        ├─► count of amenities within 500 m
        └─► building footprint intersections
        │
        ▼
IsolationForest (contamination=5%)
        │
        └─► top 5 anomalies by decision score
        │
        ▼
ClaudeClient → claude-opus-4-6
        │
        └─► risk_level, explanation, suggested_check (JSON)
        │
        ▼
GeoDataFrame → WGS84 → GeoJSON response
        │
        ▼
Marimo UI → Folium map with AI pop-ups
```

---

## How the Anomaly Detection Works

Every named location in the city is treated as a data point with four numeric features. These capture the spatial "context" of each place — what makes it fit or stand out relative to its surroundings.

| Feature | Description |
|---|---|
| `road_distance` | Meters to the nearest drivable road edge |
| `nearest_amenity_distance` | Meters to the closest other named location |
| `nearby_count` | Number of named locations within 500 m |
| `building_intersections` | Count of building footprints that contain this point |

All distances are computed in projected UTM coordinates (via `estimate_utm_crs()`) to ensure accurate meter-based measurements regardless of the city's latitude. Results are reprojected to WGS84 (EPSG:4326) for Folium rendering.

Features are normalized with `StandardScaler` before being passed to `IsolationForest`. The model uses 100 estimators with `random_state=42` for reproducibility. Locations with the lowest decision function scores (i.e., the most isolated in feature space) are the flagged anomalies.

---

## AI Explanation Layer

The top 5 anomalies are sent to Claude as a compact JSON array. The system prompt instructs Claude to act as a geospatial data quality assistant and return a structured JSON array with one object per location:

```json
{
  "risk_level": "high",
  "explanation": "Located 800m from any road with no nearby amenities.",
  "suggested_check": "Verify coordinates against satellite imagery."
}
```

Token counts are checked before sending, and the response is parsed directly into the anomaly `GeoDataFrame` and merged with the spatial results before returning the final GeoJSON payload.

---

## API Reference

The FastAPI server exposes the following endpoints:

| Method | Endpoint | Parameters | Description |
|---|---|---|---|
| `GET` | `/` | — | Health check |
| `GET` | `/anomaly` | `city: str` | Full pipeline: fetch → detect → explain. Returns GeoJSON. |
| `GET` | `/osmnx` | `city: str` | Raw OSM amenity GeoJSON for a city |
| `GET` | `/place` | `city: str`, `location: str` | Look up a named location within a city |
| `GET` | `/nearest` | `city: str`, `location: str`, `loc_id: int` | Nearest road, amenity, and building data for a specific location |
| `GET` | `/debug` | `city: str` | Intermediate data dump: dataset, street edges, buildings, amenities |

CORS is configured to allow requests from the GitHub Pages origin (`https://kristianhoward.github.io`).

---

## Technical Highlights

### Dual-Package Design
The project separates concerns between an installable client library (`api/`) and a directly-run server (`server/`). The client library is distributed via `pyproject.toml` with `setuptools`, while the server runs through `uvicorn`. This means the Marimo UI can consume the API either through the client package or directly over HTTP — and the two can evolve independently.

### WASM Deployment Without a Live Backend
The Marimo notebook is exported as a self-contained HTML/WASM file and served as a static GitHub Pages site — no server required in production. `marimo export html-wasm` compiles the notebook and its Python dependencies into WebAssembly via Pyodide, enabling full client-side execution in the browser. The heavy geospatial processing (OSMnx, IsolationForest) still runs server-side; only the rendering layer lives in WASM.

### Unsupervised Anomaly Detection with No Labels
There is no labeled training data — the model learns what "normal" looks like purely from the spatial distribution of every amenity in the queried city. This makes the tool generalizable to any city worldwide without any pre-annotation effort. The contamination parameter is set to 5%, meaning the model expects roughly 1 in 20 locations to be anomalous.

### CRS-Aware Spatial Computation
A common pitfall in geospatial work is computing distances in degrees (WGS84) rather than meters. This project uses `osmnx.projection.estimate_utm_crs()` to dynamically select the correct UTM projection for any city before computing distances — ensuring that "500 meters" means the same thing in Oslo or Singapore.

### Structured AI Output via Prompt Engineering
Rather than asking Claude for a free-form response, the prompt enforces a strict JSON schema. The system prompt defines the exact keys, value enumerations (`"low"`, `"medium"`, `"high"`), and length constraints for each field. This makes Claude's output directly parseable into a pandas `DataFrame` without any post-processing heuristics.

### Automated CI/CD to GitHub Pages
Every push to `main` triggers a GitHub Actions workflow that exports the Marimo notebook to WASM HTML and deploys it to GitHub Pages. The `ANTHROPIC_API_KEY` is injected at build time from GitHub secrets, so sensitive credentials never appear in the repository.

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- `ANTHROPIC_API_KEY` environment variable (required for `/anomaly` and tests)

### 1. Install the client library

```bash
pip install .
```

### 2. Install server dependencies

```bash
pip install -r server/requirements.txt
```

### 3. Start the backend

```bash
uvicorn server.main:app --reload
```

The server runs at `http://127.0.0.1:8000/`.

### 4. Run the UI

```bash
marimo run apps/application.py
```

For interactive editing:

```bash
marimo edit apps/application.py
```

### 5. Run tests

The test suite requires the FastAPI server to be running:

```bash
pytest tests/
pytest tests/test_data.py::test_connection       # single test
pytest tests/test_data.py::TestNearbyElements    # test class
```

---

## Deploying to GitHub Pages

To build and export the notebook manually:

```bash
marimo export html-wasm apps/application.py -o site --mode --
```

This outputs a self-contained `site/` directory ready for static hosting. On `git push` to `main`, the GitHub Actions workflow handles this automatically.

---

## License

MIT — see [LICENSE](LICENSE) for details.
