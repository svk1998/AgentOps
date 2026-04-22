# AgentOps — Theme & Nav Restructure Design

**Date:** 2026-04-22
**Scope:** Frontend base-layer aesthetic overhaul + sidebar nav restructure to match Phase 1 spec

---

## 1. Goal

Replace the current indigo/slate dark theme with the amber/neutral-dark aesthetic from `AgentOps standalone.html`, and restructure the sidebar navigation to match the Phase 1 module layout from `agentops-prompt_updated.md`. No new feature components are built — only the base shell, design tokens, and placeholder views.

---

## 2. Color System

A new `src/assets/theme.css` becomes the single source of truth for all design tokens. `main.css` imports it and drops its own token definitions.

### Palette

| Token | Value | Role |
|---|---|---|
| `--color-bg` | `#0A0B0D` | Page background |
| `--color-surface` | `#111316` | Sidebar, card base |
| `--color-surface-2` | `#16191D` | Hover states, inputs |
| `--color-surface-3` | `#1C2025` | Elevated panels |
| `--color-surface-4` | `#2A3038` | Borders, dividers |
| `--color-border` | `#1F242B` | Default borders |
| `--color-border-strong` | `#2A3038` | Emphasized borders |
| `--color-text` | `#E6E8EB` | Primary text |
| `--color-text-muted` | `#9BA3AE` | Secondary text |
| `--color-text-subtle` | `#6E7685` | Labels, placeholders |
| `--color-primary` | `#F5A524` | Amber accent (brand) |
| `--color-primary-hover` | `#D48E1A` | Amber hover |
| `--color-primary-subtle` | `#3A2A0E` | Amber tinted background |
| `--color-primary-light` | `#FDF0D4` | Amber lightest tint |
| `--color-success` | `#3DD68C` | Green |
| `--color-success-subtle` | `#0F2A1F` | Green tinted background |
| `--color-success-text` | `#3DD68C` | Green text |
| `--color-danger` | `#FF6A6A` | Red |
| `--color-danger-subtle` | `#2F1618` | Red tinted background |
| `--color-danger-text` | `#FF6A6A` | Red text |
| `--color-danger-hover` | `#E05555` | Red hover |
| `--color-warning` | `#F5A524` | Warning (same as primary) |
| `--color-warning-subtle` | `#3A2A0E` | Warning tinted background |
| `--color-warning-text` | `#FDF0D4` | Warning text |
| `--color-info` | `#6AA8FF` | Blue |
| `--color-info-subtle` | `#10223B` | Blue tinted background |
| `--color-running` | `#6AA8FF` | Run status: running |
| `--color-running-subtle` | `#10223B` | Run status bg |
| `--color-pending` | `#9BA3AE` | Run status: pending |
| `--color-completed` | `#3DD68C` | Run status: completed |
| `--color-failed` | `#FF6A6A` | Run status: failed |
| `--color-cancelled` | `#6E7685` | Run status: cancelled |

All layout, radius, shadow, typography, and transition tokens are carried over unchanged from the current `main.css`.

### PrimeVue Preset

The `AgentOpsPreset` in `main.js` switches from the indigo palette to a custom amber palette. Since PrimeVue has no built-in amber palette, the shades are specified explicitly:

| Shade | Value |
|---|---|
| 50 | `#FFFBEB` |
| 100 | `#FEF3C7` |
| 200 | `#FDE68A` |
| 300 | `#FCD34D` |
| 400 | `#FBBF24` |
| 500 | `#F5A524` |
| 600 | `#D97706` |
| 700 | `#B45309` |
| 800 | `#92400E` |
| 900 | `#78350F` |
| 950 | `#3A2A0E` |

Surface overrides in dark mode switch from the blue-tinted slate values to the neutral dark values above (`#111316` → `#2A3038`).

---

## 3. Navigation Structure

`DefaultLayout.vue` is updated with the following sections. The old sections (Orchestration, AI, Admin) are replaced entirely.

```
Overview
  └─ Dashboard          /dashboard

Registry
  └─ Agents             /registry/agents

Evaluate
  ├─ Datasets           /evaluate/datasets
  ├─ Eval Runs          /evaluate/runs
  └─ Playground         /evaluate/playground

Observe
  └─ Analytics          /analytics

Admin  (superuser only)
  ├─ Users              /users
  └─ Settings           /settings
```

Old nav items (Runs, Workflows, Prompt Optimizer, Tools, Models) are removed from the nav. Their existing module folders are **not deleted** — they remain as dead code until the new modules absorb their functionality.

---

## 4. File Changes

### New files
- `src/assets/theme.css` — all design tokens
- `src/modules/registry/` — **new folder**, separate from the existing `src/modules/agents/` which stays untouched
- `src/modules/registry/views/AgentsView.vue` — shell
- `src/modules/evaluate/views/DatasetsView.vue` — shell
- `src/modules/evaluate/views/EvalRunsView.vue` — shell
- `src/modules/evaluate/views/PlaygroundView.vue` — shell
- `src/modules/analytics/views/AnalyticsView.vue` — shell
- `src/modules/settings/views/SettingsView.vue` — shell

### Modified files
- `src/assets/main.css` — import `theme.css`, remove duplicate token block
- `src/main.js` — update PrimeVue preset to amber palette + neutral dark surfaces
- `src/layouts/DefaultLayout.vue` — new nav sections, amber active-item color
- `src/router/routes.js` — new route tree matching nav above

### Untouched
- All existing module folders (`agents/`, `runs/`, `tools/`, `models/`, `prompt-optimizer/`, `workflows/`)
- `src/stores/`, `src/services/`, `src/composables/`
- Backend

---

## 5. Placeholder Shell View Pattern

Each new view follows the same minimal pattern:

```vue
<template>
  <div class="page-shell">
    <div class="page-header">
      <h1 class="page-title">{{ title }}</h1>
      <p class="page-desc">{{ description }}</p>
    </div>
    <div class="shell-empty">
      <i class="pi pi-wrench shell-icon" />
      <p>Under construction</p>
    </div>
  </div>
</template>
```

Styled with scoped CSS using `--color-*` tokens — no hardcoded color values in views.

---

## 6. Out of Scope

- Building actual feature UI for any new module
- Migrating or deleting old module views
- Backend changes
- Authentication flow changes
- Any Phase 2 features
