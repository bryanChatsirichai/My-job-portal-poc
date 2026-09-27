# Logic constraints — do not change

This redesign is **presentation-only**. Behavior and data flow must remain identical unless explicitly noted (e.g. pagination UI wiring to an existing URL param).

## Untouchable layers

| Layer | Paths | Reason |
|-------|-------|--------|
| API client | `frontend/src/api/jobs.ts` | Fetch contracts |
| Hooks | `frontend/src/hooks/useTrackedApplications.ts` | Tracking state |
| Services | `frontend/src/services/trackingService.ts` | `localStorage` persistence |
| Types | `frontend/src/types/job.ts` | Domain model |
| Formatters | `frontend/src/utils/format.ts` | Display logic (unless purely cosmetic helpers added elsewhere) |
| Backend | `backend/` | Out of scope |

## Preserved behaviors

### HomePage (`pages/HomePage.tsx`)

- `useSearchParams` drives: `q`, `salary_min`, `salary_max`, `location`, `source`, `page`
- `loadJobs` debounced via `useEffect` + 300ms timeout
- `applyFilters` resets page to `1` and writes URL params
- `fetchJobs` arguments unchanged
- Error message semantics unchanged

**Allowed:** Markup structure, CSS classes, pagination controls that read/write existing `page` param, chip remove handlers that only update URL params.

### JobDetailPage (`pages/JobDetailPage.tsx`)

- `fetchJobById(id)` on mount
- `ApplyButton` opens `apply_url` in new tab, then calls `onApply`
- `TrackApplicationModal` + `save(job, 'applied')` flow
- Toast display (styling only)

### DashboardPage (`pages/DashboardPage.tsx`)

- `useTrackedApplications` for `items`, `stats`, `updateStatus`, `updateNotes`, `removeItem`
- Client-side filter by `ApplicationStatus | 'all'`

### Routing (`App.tsx`)

- Routes: `/`, `/jobs/:id`, `/dashboard`
- No new routes required for this plan

## Allowed changes in `.tsx` files

- `className` and wrapper elements
- `aria-*` attributes
- Replacing native elements with UI primitives that forward the same events/props
- Presentational children (icons, layout divs)
- Pagination UI (uses existing `page` search param)

## Not allowed without a separate task

- New API endpoints or query parameters
- Changing `localStorage` schema
- New global state libraries
- Kanban drag-and-drop (needs new interaction logic)
- `/discover` or other new pages with new data requirements

## Verification after each step

```bash
cd frontend
npm run build
```

Manual smoke test:

1. Search with filters → results update, URL reflects params
2. Open job detail → apply opens external URL, track saves to dashboard
3. Dashboard → change status, edit notes, remove item
