# Quickstart: Knockout Stage Results & Live Scores

**Feature**: 017-knockout-stage-results

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

1. A notice: "104 matches loaded from openfootball data (URL)" (or local file if offline)
2. Stage chips: All, Group Stage, R32, R16, QF, SF, Final
3. Group chips (visible only when "Group Stage" is selected): All, A–L
4. All 104 tournament matches with scores for completed matches

---

## Run tests

```bash
uv run pytest tests/unit/test_stage_chips.py -v
uv run pytest tests/unit/test_match_row_columns.py -v
uv run pytest tests/unit/test_worldcup_json_service.py -v
uv run pytest tests/                                       # full suite
```

---

## Manual acceptance tests

### Test 1: Group stage scores

1. Open the Schedule tab.
2. Select "Group Stage" chip.
3. **Expected**: 72 group stage matches displayed. Completed matches show actual scores (e.g., "2–0") in the Score column. Status badge shows "FT" for finished matches.

### Test 2: Knockout stage matches

1. Select "R32" chip.
2. **Expected**: 16 Round of 32 matches displayed. The Group column shows "R32" instead of a group letter. Completed matches show scores.
3. Select "QF" chip.
4. **Expected**: 4 Quarter-final matches displayed. Group column shows "QF".
5. Select "Final" chip.
6. **Expected**: 2 matches (Final + third-place match). Group column shows "F" and "3rd" respectively.

### Test 3: Stage filtering

1. Select "All" chip.
2. **Expected**: All 104 matches displayed. Group chips are hidden.
3. Select "Group Stage" chip.
4. **Expected**: 72 matches displayed. Group chips (A–L) become visible.
5. Select group chip "C".
6. **Expected**: Only Group C matches displayed (6 matches).
7. Select "SF" chip.
8. **Expected**: 2 Semi-final matches displayed. Group chips are hidden again.

### Test 4: Knockout placeholder team names

1. Find an upcoming knockout match (one without a score).
2. **Expected**: Team columns show placeholder text (e.g., "1A", "2B", "3A/B/C/D/F") as provided by the data source.

### Test 5: Offline fallback with scores

1. Disconnect from the internet.
2. Restart the app and open the Schedule tab.
3. **Expected**: Notice shows "Loaded from local file". Matches display scores if the local file has been updated with current data.

---

## Troubleshooting

### Knockout matches not showing

- Verify the URL data contains knockout matches (check `round` field values)
- Ensure `get_all_matches()` is being called (not `get_group_matches()`)

### Scores showing "vs" for completed matches

- Check that the URL data contains `score.ft` for the match
- Verify `transform_match()` is correctly converting `score.ft` to `score.fullTime`

### Stage chips not filtering

- Clear browser cache (if running in web mode)
- Restart the app
- Check that `_state["active_stage"]` is being updated on chip selection
