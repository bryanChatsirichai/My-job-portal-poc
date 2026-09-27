# Step 1 — Foundation (tokens, fonts, UI primitives)

**Goal:** Establish the design system so later steps only compose primitives.

**Status:** ✅ Finished  
**Finished:** 2026-09-11

**Estimated effort:** 1–2 sessions  
**Depends on:** [Step 0](./prep.md)  
**Blocks:** Steps 2–6

## Tasks

### 1.1 Expand design tokens

**File:** `frontend/src/styles/_variables.scss`

- Replace teal-centric palette with Harbor Signal tokens (see [overview.md](./overview.md))
- Add type scale variables (`$font-display`, `$font-ui`, sizes, line-heights)
- Add elevation tokens (prefer border-based; minimal shadow)
- Add motion tokens (`$duration-fast`, `$duration-normal`)
- Add z-index scale (`$z-header`, `$z-modal`, `$z-toast`)
- Map source colors to variables for badge reuse



### 1.2 Add mixins

**New file:** `frontend/src/styles/_mixins.scss`

- `focus-ring` — `signal` outline for keyboard users
- `truncate` / `line-clamp` helpers
- Keep existing `respond-md` / `respond-lg`; add `respond-sm` if needed



### 1.3 Global styles

**File:** `frontend/src/styles/global.scss`

- Import mixins
- Set `font-family` on `body` (DM Sans)
- Heading defaults (Fraunces where appropriate at page level, not global `h1` override if too broad)
- Link and selection styles
- Keep `prefers-reduced-motion` block



### 1.4 Load fonts

**Deferred to Step 2** — tokens define `$font-display` / `$font-ui` here; font `<link>` tags apply in layout shell so Step 1 does not change live page typography.

### 1.6 Sass module structure (no circular imports)

```
_tokens.scss   ← variables only
_mixins.scss   ← @use 'tokens'; mixins only
_variables.scss ← @forward 'tokens'; @forward 'mixins'; (barrel for existing @use paths)
```

Legacy `$color-primary` etc. keep **pre-redesign values** until Steps 2+ migrate pages. New Harbor Signal tokens (`$color-signal`, …) are for `components/ui/` only in this step.



### 1.5 UI primitives

**New folder:** `frontend/src/components/ui/`


| Component | File                                 | Variants / notes                                      |
| --------- | ------------------------------------ | ----------------------------------------------------- |
| `Button`  | `Button/Button.tsx` + `.module.scss` | `primary`, `secondary`, `ghost`, `danger`; `disabled` |
| `Input`   | `Input/Input.tsx` + `.module.scss`   | text, number, search; forwards `ref` if needed        |
| `Select`  | `Select/Select.tsx` + `.module.scss` | Styled native `<select>`                              |
| `Pill`    | `Pill/Pill.tsx` + `.module.scss`     | filter chip, optional `onRemove`                      |
| `Card`    | `Card/Card.tsx` + `.module.scss`     | `flat`, `interactive` (for links)                     |
| `Badge`   | `Badge/Badge.tsx` + `.module.scss`   | `source`, `status` variants                           |


**Rules:**

- Primitives accept standard HTML attributes (`className`, `onClick`, `disabled`, etc.)
- No business logic inside UI components
- SCSS modules use tokens from `_variables.scss` only (no hardcoded hex in components)



## Do not do in this step

- Do not refactor pages yet (except `main.tsx` font import)
- Do not change `SourceBadge` / `ApplicationStatusBadge` behavior — optional thin wrappers in Step 2+



## Acceptance criteria

- [x] `_variables.scss` documents all Harbor Signal tokens
- [x] Each UI primitive renders in isolation (Button, Input, Select, Pill, Card, Badge in `components/ui/`)
- [x] `tsc -b` passes (TypeScript compile verified)
- [x] No changes to `api/`, `hooks/`, `services/`, `types/`



## Files touched

```
frontend/src/styles/_variables.scss
frontend/src/styles/_mixins.scss          (new)
frontend/src/styles/global.scss
frontend/src/main.tsx
frontend/src/components/ui/Button/*
frontend/src/components/ui/Input/*
frontend/src/components/ui/Select/*
frontend/src/components/ui/Pill/*
frontend/src/components/ui/Card/*
frontend/src/components/ui/Badge/*
```

