# Step 6 — Polish & accessibility

**Goal:** Cross-cutting quality — motion, focus, contrast, responsive QA, optional enhancements.

**Status:** ✅ Finished  
**Finished:** 2026-09-14

**Estimated effort:** 0.5–1 session  
**Depends on:** [Steps 1–5](./01-foundation.md)  
**Blocks:** Nothing (final step)

## Tasks

### 6.1 Accessibility audit

- [x] All interactive elements keyboard reachable with visible `focus-ring`
- [x] Modal: focus moves to dialog; Esc closes (`onClose`)
- [x] Filter drawer (mobile): Esc closes, focus return
- [x] `SourceBadge`: `aria-label` includes source name
- [x] Color contrast: `signal` on white ≥ 4.5:1 (darken to `#D14E32` if needed)
- [x] Form inputs have associated `<label>` elements (FilterPanel, Dashboard)

### 6.2 Motion

- Confirm `prefers-reduced-motion` in `global.scss` disables non-essential transitions
- Remove any per-card entrance animations if introduced
- Keep: row hover background, modal fade, toast slide (subtle)

### 6.3 Responsive QA

Test viewports:

| Width | Checks |
|-------|--------|
| 375px | Search full width, filter drawer, bottom apply bar on detail |
| 768px | Filter sidebar or drawer transition |
| 1280px | Two-column home layout, detail sidebar sticky |

### 6.4 Optional enhancements (if time)

- [x] **Salary range slider** in `FilterPanel` — min/max range inputs synced to existing string state
- [x] **Tracked count badge** on “My Applications” nav when `stats.total > 0` (read hook in Layout — display only)
- [x] **Focus search on /** keyboard shortcut — skips when focus is in an input; active on HomePage

### 6.5 Cross-page consistency pass

- Empty / error / loading patterns match across Home, Detail, Dashboard
- Button labels consistent (“Search” vs “Apply filters” vs “Track application”)
- Spacing: no conflicting margins between section classes (watch `.section` + element selector specificity)

### 6.6 Build & smoke test

```bash
cd frontend
npm run build
npm run dev
```

Manual checklist:

1. Home → search → filter → paginate → open job
2. Apply → track → see on dashboard → edit status/notes → remove
3. Refresh page → URL state and `localStorage` persist as before

## Do not do in this step

- Do not introduce dark mode unless explicitly requested
- Do not add E2E test framework unless requested (manual QA sufficient for POC)

## Acceptance criteria

- [x] WCAG 2.1 AA target for text and UI components (pragmatic POC level)
- [x] No logic regressions per [constraints.md](./constraints.md)
- [x] `npm run build` passes
- [x] All success criteria in [README.md](./README.md) checked off

## Files touched

```
frontend/src/styles/global.scss
frontend/src/components/Layout/*
frontend/src/components/FilterPanel/*     (slider optional)
frontend/src/components/TrackApplicationModal/*
Any *.module.scss needing contrast fixes
```
