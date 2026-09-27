# Step 4 — Job detail page

**Goal:** Readable job posting layout, prominent apply action, polished modal and toast.

**Status:** ✅ Finished  
**Finished:** 2026-09-14

**Estimated effort:** 1 session  
**Depends on:** [Steps 1–2](./01-foundation.md)  
**Blocks:** Nothing

## Tasks

### 4.1 Page layout

**Files:** `JobDetailPage.tsx`, `JobDetailPage.module.scss`

- Two-column on large screens: main content + sticky sidebar (keep current grid breakpoint)
- Main panel: `Card` or surface with `divider` border
- Header: title (Fraunces), company, `SourceBadge`
- Salary line: visually secondary to title but stronger than other meta

### 4.2 Meta & skills

**Files:** `JobDetailPage.module.scss`

- Meta row: location, posted date, employment type, seniority — separate items (avoid `·` joined strings)
- Optional: small inline SVG icons for location/calendar (no new npm package required)
- Skills: `Pill` or neutral chips on `mist` background

### 4.3 Description

- `max-width: 68ch` for readability
- Keep `white-space: pre-wrap` on description text
- Section heading: “Job description” (sentence case)

### 4.4 Apply sidebar

**Files:** `ApplyButton/ApplyButton.tsx`, `ApplyButton.module.scss`

- Primary `Button` full width: “Apply on {source}”
- Helper note below in `fog` — same copy intent as today
- **Logic unchanged:** `window.open` + `onApply()`

### 4.5 Mobile apply bar

**File:** `JobDetailPage.module.scss`

- Keep fixed bottom sidebar on small viewports
- Ensure sufficient `padding-bottom` on page so content isn’t hidden
- Safe-area aware if targeting notched phones

### 4.6 Track modal

**Files:** `TrackApplicationModal/TrackApplicationModal.tsx`, `.module.scss`

- Centered overlay, focus trap friendly markup
- Primary / secondary `Button`s
- Same props: `open`, `source`, `alreadyTracked`, `onConfirm`, `onClose`

### 4.7 Toast

**File:** `JobDetailPage.module.scss`

- Position bottom-right; `signal` or `ink` background
- Auto-dismiss can remain in page logic or add simple `useEffect` timeout if not present — **must not change save behavior**

### 4.8 Loading & error states

- Style `.state` blocks consistently with HomePage empty/error patterns
- Same loading and error strings

## Do not do in this step

- Do not alter `fetchJobById` or tracking `save` payload
- Do not add “similar jobs” (needs new API)

## Acceptance criteria

- [x] Job loads by ID as before
- [x] Apply opens external URL; modal appears; track writes to dashboard
- [x] Sidebar sticky on desktop, fixed bottom on mobile
- [x] Description readable long-form
- [x] `npm run build` passes

## Files touched

```
frontend/src/pages/JobDetailPage.tsx          (markup/classes only)
frontend/src/pages/JobDetailPage.module.scss
frontend/src/components/ApplyButton/*
frontend/src/components/TrackApplicationModal/*
frontend/src/components/SourceBadge/SourceBadge.module.scss
```
