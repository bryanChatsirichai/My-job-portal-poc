# Frontend UI/UX Redesign Plan

Step-by-step plan to modernize the job portal frontend **without changing business logic** (API calls, URL-driven filters, `localStorage` tracking, apply flow, routing).

## Design direction

**Harbor Signal** — calm surfaces, dense scannable job data, one bold accent (signal orange), source colors as information. Full rationale: [overview.md](./overview.md).

## Constraints

What must stay unchanged: [constraints.md](./constraints.md).

## Progress

| Step | Document | Status | Finished |
|------|----------|--------|----------|
| 0 | [prep.md](./prep.md) | ✅ Done | 2026-09-11 |
| 1 | [01-foundation.md](./01-foundation.md) | ✅ Done | 2026-09-11 |
| 2 | [02-layout-shell.md](./02-layout-shell.md) | ✅ Done | 2026-09-14 |
| 3 | [03-homepage.md](./03-homepage.md) | ✅ Done | 2026-09-14 |
| 4 | [04-job-detail.md](./04-job-detail.md) | ✅ Done | 2026-09-14 |
| 5 | [05-dashboard.md](./05-dashboard.md) | ✅ Done | 2026-09-14 |
| 6 | [06-polish-accessibility.md](./06-polish-accessibility.md) | ✅ Done | 2026-09-14 |

## Implementation order

Execute steps in sequence. Each step should leave the app buildable and shippable.

| Step | Document | Summary | Depends on |
|------|----------|---------|------------|
| 0 | [prep.md](./prep.md) | Lock decisions, baseline build, progress tracking | — |
| 1 | [01-foundation.md](./01-foundation.md) | Design tokens, fonts, mixins, UI primitives | Step 0 |
| 2 | [02-layout-shell.md](./02-layout-shell.md) | Header, navigation, page shell | Step 1 |
| 3 | [03-homepage.md](./03-homepage.md) | Search hero, filters, job rows, pagination UI | Steps 1–2 |
| 4 | [04-job-detail.md](./04-job-detail.md) | Detail layout, apply sidebar, modal, toast | Steps 1–2 |
| 5 | [05-dashboard.md](./05-dashboard.md) | Stats, status filters, tracked job cards | Steps 1–2 |
| 6 | [06-polish-accessibility.md](./06-polish-accessibility.md) | Motion, focus, contrast, responsive QA | Steps 1–5 |

## Locked decisions

| # | Question | Decision |
|---|----------|----------|
| 1 | Brand name in header | **JobFinder SG** |
| 2 | Job list layout | **List rows** on all breakpoints |
| 3 | Salary filter UI | **Number inputs** in Step 3; optional range slider in Step 6 |
| 4 | Dark mode | **Skip** for POC |

## Success criteria (all steps)

- [x] Same API calls and URL search params as before
- [x] Track / apply / remove applications still work via `localStorage`
- [x] `npm run build` passes with no changes to `api/`, `hooks/`, `services/`, or `types/` (`tsc -b` verified)
- [x] Visually distinct from generic teal SaaS templates
- [x] Keyboard navigable; `prefers-reduced-motion` respected

## File map (presentation layer only)

```
frontend/src/
├── styles/           ← tokens, mixins, global
├── components/ui/    ← Button, Input, Pill, Card, Badge, Select
├── components/       ← Layout, SearchBar, FilterPanel, JobCard, …
└── pages/            ← HomePage, JobDetailPage, DashboardPage
```

## Related docs

- [Product README](../../README.md)
- [Job ingestion architecture](../../docs/architecture/job-ingestion.md)
