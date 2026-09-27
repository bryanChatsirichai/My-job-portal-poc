# Design overview — Harbor Signal

## Product context

| Dimension | Definition |
|-----------|------------|
| **Product** | Singapore job aggregator (MyCareersFuture, Adzuna, Jobicy, LinkedIn) |
| **Audience** | Active job seekers comparing many listings |
| **Primary job** | Find relevant roles quickly, then track applications |
| **Differentiator** | Multi-source search + in-browser application pipeline (POC) |

## Color tokens

| Token | Hex | Role |
|-------|-----|------|
| `ink` | `#1A2332` | Primary text |
| `mist` | `#F4F6F9` | Page background |
| `surface` | `#FFFFFF` | Cards, panels |
| `signal` | `#E85A3C` | Primary CTA, active nav, focus ring |
| `harbor` | `#3D5A80` | Secondary links, filter accents |
| `fog` | `#8B9AAB` | Muted meta (location, dates) |
| `divider` | `#DDE3EA` | Borders (prefer over heavy shadows) |

### Source colors (semantic, extend existing badges)

| Source | Hex |
|--------|-----|
| MyCareersFuture | `#006B5E` |
| LinkedIn | `#0A66C2` |
| Adzuna | `#279B37` |
| Jobicy | `#6B4FBB` |

### Application status (keep semantic meaning, tune saturation if needed)

Reuse existing status tokens from `_variables.scss` (`applied`, `interview`, `rejected`, `accepted`, `saved`).

## Typography

| Role | Family | Weights |
|------|--------|---------|
| Display | [Fraunces](https://fonts.google.com/specimen/Fraunces) | 600–700 |
| UI / body | [DM Sans](https://fonts.google.com/specimen/DM+Sans) | 400, 500, 600 |

### Scale

- Display: `2rem` / `1.5rem`
- Body: `1rem`, line-height `1.55`
- Meta: `0.875rem`, line-height `1.45`
- Max line length: ~68ch on job descriptions

## Layout principles

1. **Search is the hero** — full-width search bar, not a gradient marketing box.
2. **List rows over card grid** — faster scanning for job comparison.
3. **Left-aligned content**, max-width `1120px`.
4. **Quiet chrome, loud data** — title and salary carry visual weight.
5. **Source is information** — consistent source color across badge, row accent, detail header.

## Radius hierarchy

| Element | Radius |
|---------|--------|
| Inputs, cards | `8px` |
| Chips, pills | `4px` (pill: `999px`) |
| Modals | `12px` |

## Motion

- **One orchestrated moment:** subtle search bar focus treatment on first HomePage visit (optional).
- **Interaction feedback:** hover background on job rows, modal open/close.
- **Avoid:** staggered fade-in on every card, universal hover lift on all cards.

## Copy tone

- Sentence case, plain verbs, active voice.
- CTAs name the action: “Search”, “Apply filters”, “Track application”.
- Empty and error states explain what to do next — no apologies.

## Patterns to avoid

- Warm cream + terracotta “AI default” palette
- Teal-on-slate generic SaaS (current look)
- Accent word in headline, ALL-CAPS labels, eyebrow text above headings
- Middle-dot meta strings (`A · B · C`)
- Arrow suffix on every link (`→`)
- Identical soft shadows on every surface

## Wireframe — HomePage (target)

```
┌─────────────────────────────────────────────────────────────┐
│  JobFinder SG          Search    My Applications            │
├─────────────────────────────────────────────────────────────┤
│  Find your next role in Singapore                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Search jobs by title, company, or keyword  [Search]│    │
│  └─────────────────────────────────────────────────────┘    │
│  847 roles · "engineer" · Min $5k              [Clear all]  │
├──────────┬──────────────────────────────────────────────────┤
│ Filters  │  Senior Engineer              $8k–$12k/mo  MCF  │
│ (sticky) │  Grab · CBD · 2d ago                           │
│          │  ─────────────────────────────────────────────── │
│ Source   │  Product Designer             $6k–$9k/mo  LI   │
│ Salary   │  ...                                             │
│ Location │  [ Prev ]  Page 1 of 43  [ Next ]               │
└──────────┴──────────────────────────────────────────────────┘
```
