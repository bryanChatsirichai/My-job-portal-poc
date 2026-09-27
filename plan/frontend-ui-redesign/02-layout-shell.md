# Step 2 — Layout shell (header & navigation)

**Goal:** Apply the new brand to the app chrome — sticky header, navigation, main content area.

**Status:** ✅ Finished  
**Finished:** 2026-09-14

**Estimated effort:** 0.5–1 session  
**Depends on:** [Step 1](./01-foundation.md)  
**Blocks:** Steps 3–5 (recommended order)

## Tasks

### 2.1 Header redesign

**Files:** `frontend/src/components/Layout/Layout.tsx`, `Layout.module.scss`

- Background: `mist` / `surface` with subtle `backdrop-filter` (retain sticky behavior)
- Logo: Fraunces, `ink` color (optionally small `signal` mark)
- Nav links: DM Sans medium; inactive = `fog`, active = `ink` + `signal` underline indicator
- Max-width container: `1120px` (update from `1200px` if desired)
- Touch-friendly tap targets (min 44px height on mobile nav)

### 2.2 Main content area

**File:** `Layout.module.scss`

- Consistent horizontal padding (`$space-4` mobile, `$space-5` desktop)
- Optional: slightly more top padding on routes that need breathing room

### 2.3 SearchBar early pass (optional)

**Files:** `SearchBar/SearchBar.tsx`, `SearchBar.module.scss`

- Use `Input` + `Button` primitives from Step 1
- Full-width on mobile; comfortable height for primary action
- Can fully polish in Step 3; here ensure it doesn’t break existing form submit

## Do not do in this step

- Do not add new routes or nav items
- Do not change `Link` / `NavLink` `to` paths

## Acceptance criteria

- [x] Header sticky, readable on scroll
- [x] Active route visually distinct (not color-only)
- [x] Keyboard: Tab through logo → nav links → main content
- [x] `npm run build` passes
- [x] All three routes render inside layout without layout shift

## Files touched

```
frontend/src/components/Layout/Layout.tsx
frontend/src/components/Layout/Layout.module.scss
frontend/src/components/SearchBar/SearchBar.tsx      (optional)
frontend/src/components/SearchBar/SearchBar.module.scss (optional)
```
