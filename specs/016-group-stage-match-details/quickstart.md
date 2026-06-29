# Quickstart: Group Stage Match Details via URL Data Source

**Feature**: 016-group-stage-match-details

---

## Prerequisites

```bash
cd /path/to/football-impl-flet-2026
uv sync
```

No API key is required for this feature. The schedule loads from a public URL or local file.

---

## Run the app

```bash
uv run flet run
```

Or in web mode:

```bash
uv run flet run --web
```

Open the **Schedule** tab. You should see:

1. A notice: "Loaded from openfootball data" (or "Loaded from local file" if offline)
2. Group chips: All, A, B, C, D, E, F, G, H, I, J, K, L
3. All 48 group stage matches displayed with team names, dates, times, groups, and venues

---

## Run tests

```bash
uv run pytest tests/unit/test_worldcup_json_service.py -v
uv run pytest tests/                                       # full suite
```

---

## Manual acceptance tests

### Test 1: Load without API key

1. Ensure `FOOTBALL_DATA_API_KEY` is **not** set in `.env`.
2. Open the Schedule tab.
3. **Expected**: All 48 group stage matches load from the URL. Notice shows "Loaded from openfootball data". Group chips are functional.

### Test 2: Group filtering

1. Click group chip **C**.
2. **Expected**: Only 6 Group C matches visible (Brazil, Haiti, Morocco, Scotland).
3. Click **All**.
4. **Expected**: All 48 matches visible, sorted by date then time.

### Test 3: Match details display

1. View any match row.
2. **Expected**: Shows team1 name, team2 name, date, kick-off time with UTC offset (e.g., "13:00 UTC-6"), group letter, and venue/city name.
3. **Expected**: Score area shows "vs" (no scores in URL data).
4. **Expected**: Status badge shows "Scheduled".

### Test 4: Offline fallback

1. Disconnect from the internet (or block the URL).
2. Restart the app and open the Schedule tab.
3. **Expected**: Notice shows "Loaded from local file". All 48 matches still display.

### Test 5: Venue display

1. Find the Mexico vs South Africa match (Group A).
2. **Expected**: Venue shows "Mexico City".
3. Find a match with parenthetical venue (e.g., Guadalajara (Zapopan)).
4. **Expected**: Full ground string is displayed.

---

## Troubleshooting

### "Failed to load data" error

- Check internet connectivity (URL fetch failed)
- Verify `data/worldcup/2026/worldcup.json` exists (local fallback)
- Check console for detailed error messages

### Matches not loading

- Ensure the app is started from the project root directory
- Verify `data/worldcup/2026/worldcup.json` is present and valid JSON
- Check that the file contains a `matches` array with group stage data

### Group chips not filtering

- Clear browser cache (if running in web mode)
- Restart the app
- Check console for JavaScript errors (web mode only)
