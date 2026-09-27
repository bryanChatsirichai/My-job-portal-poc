# Step 3 — HomePage (search, filters, results)

**Goal:** Highest-impact screen — integrated search hero, improved filters, scannable job rows, pagination.

**Status:** ✅ Finished  
**Finished:** 2026-09-14

**Estimated effort:** 1–2 sessions  
**Depends on:** [Steps 1–2](./01-foundation.md)  
**Blocks:** Nothing (Step 6 polish comes later)

## Tasks

### 3.1 Hero / search section

**Files:** `HomePage.tsx`, `HomePage.module.scss`, `SearchBar/*`

- Remove cyan gradient hero box; use `mist` page background
- Compact headline (Fraunces) + one-line subcopy
- Full-width `SearchBar` as primary focal point
- Same state: `query`, `applyFilters` on submit

### 3.2 Results summary & filter chips

**Files:** `HomePage.tsx`, `HomePage.module.scss`

- Show count: `Showing X of Y jobs` (unchanged logic)
- Render `activeFilters` as `Pill` components
- **Add:** per-chip remove and “Clear all” — only manipulates `searchParams` (no new fetch logic)
- Optional: `Button` ghost for “Clear all”

### 3.3 Filter panel

**Files:** `FilterPanel/FilterPanel.tsx`, `FilterPanel.module.scss`

- Restyle with `Select`, `Input`, `Button` primitives
- Clear section grouping (Source, Salary, Location)
- **Desktop:** sticky sidebar in two-column layout (keep `280px` or tune)
- **Mobile:** “Filters” button opens drawer/sheet; “Apply filters” closes drawer and calls existing `onApply`
- Salary: keep number inputs for v1 (range slider optional in Step 6)

### 3.4 Job list → rows

**Files:** `JobCard/JobCard.tsx`, `JobCard.module.scss`

- Horizontal row layout:
  - Left: title (semibold), company (`fog`)
  - Right: salary (prominent), `SourceBadge`
  - Bottom meta: location, posted date
- Hover: background tint or left `signal` border — no `translateY` lift
- Keep `Link` to `/jobs/${job.id}` and same props interface `{ job: JobListItem }`

### 3.5 Loading & empty states

**Files:** `HomePage.module.scss`

- Skeleton rows matching row height (not tall cards)
- Empty state: heading + short copy + link/button to clear filters
- Error state: retain message; style with readable error color

### 3.6 Pagination UI

**Files:** `HomePage.tsx`, `HomePage.module.scss`

- Wire to **existing** `page` from `searchParams` and `total` / `limit: 20`
- Prev / Next buttons; disable at boundaries
- Update URL `page` param only (reuse `setSearchParams` pattern from `applyFilters`)
- **No new API parameters**

Example handler pattern (presentation wiring only):

```ts
const setPage = (nextPage: number) => {
  const next = new URLSearchParams(searchParams);
  next.set('page', String(nextPage));
  setSearchParams(next);
};
```

## Do not do in this step

- Do not change `fetchJobs` signature or debounce timing
- Do not switch from 2-column grid without updating `HomePage.module.scss` list section (intentional layout change)

## Acceptance criteria

- [x] Search + filters update URL and results as before
- [x] Job rows readable at a glance (title, company, salary, source)
- [x] Pagination changes page and refetches via existing `loadJobs`
- [x] Mobile: filters usable without horizontal scroll on main content
- [x] `npm run build` passes

## Files touched

```
frontend/src/pages/HomePage.tsx
frontend/src/pages/HomePage.module.scss
frontend/src/components/SearchBar/*
frontend/src/components/FilterPanel/*
frontend/src/components/JobCard/*
frontend/src/components/SourceBadge/SourceBadge.module.scss  (token alignment)
```
