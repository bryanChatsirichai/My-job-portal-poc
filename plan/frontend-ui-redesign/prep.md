# Step 0 — Preparation

**Goal:** Lock design decisions, verify baseline build, and enable progress tracking before code changes.

**Status:** ✅ Finished  
**Finished:** 2026-09-11

## Locked decisions

| # | Question | Decision |
|---|----------|----------|
| 1 | Brand name in header | **JobFinder SG** |
| 2 | Job list layout | **List rows** on all breakpoints |
| 3 | Salary filter UI | **Number inputs** in Step 3; optional range slider in Step 6 |
| 4 | Dark mode | **Skip** for POC |

## Baseline verification

- [x] `frontend` dependencies installed
- [x] `npm run build` passes before UI token changes
- [x] Routes confirmed: `/`, `/jobs/:id`, `/dashboard`
- [x] Logic boundary documented in [constraints.md](./constraints.md)

## Step isolation rule

Each step must leave the running app functional and must not apply visual changes reserved for later steps. Step 1 adds tokens and UI primitives only — pages keep their pre-redesign look until Step 2+.

## Acceptance criteria

- [x] Open decisions recorded (not left ambiguous)
- [x] Progress tracking added to [README.md](./README.md)
- [x] Baseline build green
