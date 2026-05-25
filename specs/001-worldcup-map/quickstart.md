# Quickstart: World Cup Participating Countries Map

**Feature**: 001-worldcup-map | **Date**: 2026-05-15

## Prerequisites

- Python >= 3.10
- `uv` package manager installed ([install guide](https://docs.astral.sh/uv/))
- Flet >= 0.84 (`uv` will install it from `pyproject.toml`)

---

## 1. Download the GeoJSON Asset

The `countries.geojson` file is NOT committed to the repo — download it once:

```bash
curl -L "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson" \
     -o src/assets/countries.geojson
```

Verify it downloaded:
```bash
python -c "import json; d=json.load(open('src/assets/countries.geojson')); print(len(d['features']), 'countries')"
# Expected: ~250 countries
```

---

## 2. Install Dependencies

```bash
uv sync
```

---

## 3. Run as a Web App

```bash
uv run flet run --web
```

Open `http://localhost:8550` (or the port shown in the terminal) in your browser.

---

## 4. Run as a Desktop App

```bash
uv run flet run
```

---

## 5. Run Tests

```bash
uv run pytest tests/ -v
```

Expected output: all tests in `tests/unit/` and `tests/integration/` pass.

---

## 6. Project Layout Reference

```
src/
├── main.py               Entry point — run this with flet
├── views/map_view.py     Interactive world-map canvas + info panel + group filter
├── services/worldcup_data.py   Loads static JSON / GeoJSON; answers queries
└── shared/
    ├── models.py         ParticipatingCountry, FIFAGroup dataclasses
    └── geo_utils.py      Projection math + point-in-polygon hit testing

src/assets/
├── countries.geojson     Natural Earth 1:110m (download in step 1)
└── worldcup2026.json     Hand-authored 48-team dataset
```

---

## 7. Adding or Updating Team Data

Edit `src/assets/worldcup2026.json`. The array must contain exactly 48 entries.
Each entry:

```json
{
  "iso_a3": "ESP",
  "name": "Spain",
  "group": "C",
  "appearances": 16,
  "flag_emoji": "🇪🇸"
}
```

`iso_a3` must match the `ISO_A3` value in `countries.geojson`. Unknown codes are
silently ignored by the map renderer (country stays grey).

---

## 8. Deploying the Web App

```bash
uv run flet run --web --host 0.0.0.0 --port 8080
```

Or build a self-contained desktop/mobile binary:

```bash
uv run flet build linux   # Linux
uv run flet build apk -v  # Android
```
