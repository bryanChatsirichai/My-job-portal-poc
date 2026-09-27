# Step 5 — Dashboard (application tracking)

**Goal:** Make the tracking pipeline feel intentional — stats at a glance, clear status filtering, cleaner cards.

**Status:** ✅ Finished  
**Finished:** 2026-09-14

**Estimated effort:** 1 session  
**Depends on:** [Steps 1–2](./01-foundation.md)  
**Blocks:** Nothing

## Tasks

### 5.1 Page header

**Files:** `DashboardPage.tsx`, `DashboardPage.module.scss`

- Title: “My Applications” (Fraunces)
- Subtitle: “Saved in this browser” — keep POC honesty
- Stats: convert plain spans to **stat cards** (large number, small label)
  - Use existing `stats.total`, `stats.applied`, `stats.interview`, `stats.accepted`

### 5.2 Status filter bar

**Files:** `DashboardPage.tsx`, `DashboardPage.module.scss`

- Replace raw `<button>` list with `Pill` toggles
- Same `FILTERS` array and `filter` state
- Horizontal scroll on mobile with fade edge optional (CSS only)

### 5.3 Dashboard job cards

**Files:** `DashboardJobCard/DashboardJobCard.tsx`, `.module.scss`

- Use `Card` primitive
- Optional left border color by `ApplicationStatus` (CSS map only)
- `ApplicationStatusBadge` aligned with new `Badge` styles
- Restyle `select` and `textarea` via `Select` / native styling tokens
- Actions row: text links + ghost danger for Remove
- **Logic unchanged:** `onStatusChange`, `onNotesChange`, `onRemove`

### 5.4 Empty state

- Heading + copy unchanged in meaning
- Add `Button` or link to `/` — “Search jobs”

### 5.5 Grid layout

- Single column mobile; two columns `lg+` (keep current breakpoint behavior)
- Consistent gap using spacing tokens

## Do not do in this step

- Do not change `useTrackedApplications` or `trackingService`
- Do not add kanban columns or drag-and-drop (new logic)

## Acceptance criteria

- [x] Filter by status works as before
- [x] Status select, notes textarea, remove, view job, external apply link all work
- [x] Stats reflect live `localStorage` data
- [x] Empty state shows when no items
- [x] `npm run build` passes

## Files touched

```
frontend/src/pages/DashboardPage.tsx          (markup/classes only)
frontend/src/pages/DashboardPage.module.scss
frontend/src/components/DashboardJobCard/*
frontend/src/components/ApplicationStatusBadge/*
```
