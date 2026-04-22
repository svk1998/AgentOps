# AgentOps Theme & Nav Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the indigo/slate dark theme with an amber/neutral-dark aesthetic from `AgentOps standalone.html` and restructure the sidebar nav to match the Phase 1 spec modules.

**Architecture:** Extract all design tokens into a standalone `theme.css` file, update the PrimeVue preset to amber, create six placeholder shell views for new modules, wire up new nested routes, and update `DefaultLayout.vue` with the restructured nav.

**Tech Stack:** Vue 3, PrimeVue (@primeuix/themes Aura preset), Vite, Vitest (jsdom)

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `src/assets/theme.css` | Create | Single source for all design tokens |
| `src/assets/main.css` | Modify | Import `theme.css`; strip old token block |
| `src/main.js` | Modify | Swap PrimeVue preset to amber palette + neutral surfaces |
| `src/layouts/DefaultLayout.vue` | Modify | New nav sections; amber active styles; breadcrumb labels |
| `src/router/routes.js` | Modify | New route tree matching nav |
| `src/modules/registry/views/AgentsView.vue` | Create | Shell for Agent Registry |
| `src/modules/evaluate/views/DatasetsView.vue` | Create | Shell for Datasets |
| `src/modules/evaluate/views/EvalRunsView.vue` | Create | Shell for Eval Runs |
| `src/modules/evaluate/views/PlaygroundView.vue` | Create | Shell for Playground |
| `src/modules/analytics/views/AnalyticsView.vue` | Create | Shell for Analytics |
| `src/modules/settings/views/SettingsView.vue` | Create | Shell for Settings |
| `tests/views/shell-views.test.js` | Create | Smoke tests for all shell views |

---

## Task 1: Create `src/assets/theme.css`

**Files:**
- Create: `src/assets/theme.css`

- [ ] **Step 1: Create the file with all design tokens**

```css
/* ── AgentOps Design Tokens ─────────────────────────────────────────────────
 * Single source of truth for all color and spacing tokens.
 * All components import these via main.css.
 * Based on the AgentOps standalone.html amber/neutral-dark palette.
 */
:root {
  /* Backgrounds */
  --color-bg:           #0A0B0D;
  --color-surface:      #111316;
  --color-surface-2:    #16191D;
  --color-surface-3:    #1C2025;
  --color-surface-4:    #2A3038;

  /* Borders */
  --color-border:        #1F242B;
  --color-border-strong: #2A3038;

  /* Text */
  --color-text:         #E6E8EB;
  --color-text-muted:   #9BA3AE;
  --color-text-subtle:  #6E7685;

  /* Brand — amber */
  --color-primary:        #F5A524;
  --color-primary-hover:  #D48E1A;
  --color-primary-subtle: #3A2A0E;
  --color-primary-light:  #FDF0D4;

  /* Semantic — success */
  --color-success:        #3DD68C;
  --color-success-subtle: #0F2A1F;
  --color-success-text:   #3DD68C;

  /* Semantic — warning (uses amber, same as primary) */
  --color-warning:        #F5A524;
  --color-warning-subtle: #3A2A0E;
  --color-warning-text:   #FDF0D4;

  /* Semantic — danger */
  --color-danger:         #FF6A6A;
  --color-danger-subtle:  #2F1618;
  --color-danger-text:    #FF6A6A;
  --color-danger-hover:   #E05555;

  /* Semantic — info */
  --color-info:           #6AA8FF;
  --color-info-subtle:    #10223B;

  /* Run statuses */
  --color-pending:        #9BA3AE;
  --color-running:        #6AA8FF;
  --color-running-subtle: #10223B;
  --color-completed:      #3DD68C;
  --color-failed:         #FF6A6A;
  --color-cancelled:      #6E7685;

  /* Layout */
  --sidebar-width:    244px;
  --topbar-height:    56px;

  /* Radius */
  --radius-sm:  0.25rem;
  --radius:     0.5rem;
  --radius-lg:  0.75rem;
  --radius-xl:  1rem;

  /* Shadows */
  --shadow-sm:  0 1px 2px rgba(0,0,0,0.4);
  --shadow:     0 2px 6px rgba(0,0,0,0.4);
  --shadow-md:  0 4px 12px rgba(0,0,0,0.5);
  --shadow-lg:  0 8px 24px rgba(0,0,0,0.6);
  --shadow-xl:  0 16px 40px rgba(0,0,0,0.7);

  /* Typography */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;

  /* Transitions */
  --transition:      0.15s ease;
  --transition-slow: 0.25s ease;
}
```

- [ ] **Step 2: Commit**

```bash
git add src/assets/theme.css
git commit -m "feat: add amber design token file (theme.css)"
```

---

## Task 2: Update `src/assets/main.css`

**Files:**
- Modify: `src/assets/main.css`

Replace the entire `:root { ... }` block (lines 11–82) with a single import of `theme.css`. Everything else in the file stays unchanged.

- [ ] **Step 1: Replace the token block with an import**

Open `src/assets/main.css`. The file currently starts with a reset block and then a large `:root { ... }` token block (from `/* ── Design Tokens ──` through the closing `}` before `/* ── Base ──`).

Replace the entire token section with:

```css
/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Design Tokens ── */
@import './theme.css';

/* ── Base ── */
html { color-scheme: dark; }
```

The rest of `main.css` (Base, Scrollbar, Utility Classes, Animation, PrimeVue integration) stays unchanged.

- [ ] **Step 2: Verify no duplicate token definitions remain**

Open `src/assets/main.css` and confirm there is no remaining `:root { --color-bg` or similar block. The only `:root` block should now come from `theme.css`.

- [ ] **Step 3: Commit**

```bash
git add src/assets/main.css
git commit -m "refactor: consolidate design tokens into theme.css"
```

---

## Task 3: Update PrimeVue Preset in `src/main.js`

**Files:**
- Modify: `src/main.js`

- [ ] **Step 1: Replace the `AgentOpsPreset` definition**

Open `src/main.js`. Find the `const AgentOpsPreset = definePreset(Aura, { ... })` block and replace it entirely with:

```js
const AgentOpsPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50:  '#FFFBEB',
      100: '#FEF3C7',
      200: '#FDE68A',
      300: '#FCD34D',
      400: '#FBBF24',
      500: '#F5A524',
      600: '#D97706',
      700: '#B45309',
      800: '#92400E',
      900: '#78350F',
      950: '#3A2A0E',
    },
    colorScheme: {
      dark: {
        surface: {
          0:   '#ffffff',
          50:  '#E6E8EB',
          100: '#9BA3AE',
          200: '#6E7685',
          300: '#5B6270',
          400: '#2A3038',
          500: '#1C2025',
          600: '#16191D',
          700: '#111316',
          800: '#0F1114',
          900: '#0A0B0D',
          950: '#070809',
        },
      },
    },
  },
})
```

- [ ] **Step 2: Verify the rest of `main.js` is unchanged**

Confirm `app.use(PrimeVue, { theme: { preset: AgentOpsPreset, options: { darkModeSelector: '.app-dark', cssLayer: false } } })` still references `AgentOpsPreset`. No other changes needed.

- [ ] **Step 3: Commit**

```bash
git add src/main.js
git commit -m "feat: switch PrimeVue preset to amber palette"
```

---

## Task 4: Create Shell Views

**Files:**
- Create: `src/modules/registry/views/AgentsView.vue`
- Create: `src/modules/evaluate/views/DatasetsView.vue`
- Create: `src/modules/evaluate/views/EvalRunsView.vue`
- Create: `src/modules/evaluate/views/PlaygroundView.vue`
- Create: `src/modules/analytics/views/AnalyticsView.vue`
- Create: `src/modules/settings/views/SettingsView.vue`
- Create: `tests/views/shell-views.test.js`

Each view follows the same shell pattern. The `src/modules/registry/` and `src/modules/evaluate/` and `src/modules/analytics/` and `src/modules/settings/` directories are **new** — they are separate from the existing modules (`agents/`, `runs/`, etc.) which stay untouched.

- [ ] **Step 1: Write the failing smoke tests**

Create `tests/views/shell-views.test.js`:

```js
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AgentsView from '@/modules/registry/views/AgentsView.vue'
import DatasetsView from '@/modules/evaluate/views/DatasetsView.vue'
import EvalRunsView from '@/modules/evaluate/views/EvalRunsView.vue'
import PlaygroundView from '@/modules/evaluate/views/PlaygroundView.vue'
import AnalyticsView from '@/modules/analytics/views/AnalyticsView.vue'
import SettingsView from '@/modules/settings/views/SettingsView.vue'

const cases = [
  { name: 'AgentsView',    Component: AgentsView,    title: 'Agents' },
  { name: 'DatasetsView',  Component: DatasetsView,  title: 'Datasets' },
  { name: 'EvalRunsView',  Component: EvalRunsView,  title: 'Eval Runs' },
  { name: 'PlaygroundView',Component: PlaygroundView,title: 'Playground' },
  { name: 'AnalyticsView', Component: AnalyticsView, title: 'Analytics' },
  { name: 'SettingsView',  Component: SettingsView,  title: 'Settings' },
]

describe('Shell views', () => {
  it.each(cases)('$name renders page title "$title" and shell-empty', ({ Component, title }) => {
    const wrapper = mount(Component)
    expect(wrapper.find('.page-title').text()).toBe(title)
    expect(wrapper.find('.shell-empty').exists()).toBe(true)
  })
})
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd frontend && npm run test -- tests/views/shell-views.test.js
```

Expected: 6 failures — `Cannot find module '@/modules/registry/views/AgentsView.vue'`

- [ ] **Step 3: Create `src/modules/registry/views/AgentsView.vue`**

```vue
<template>
  <div class="page-shell">
    <div class="page-header">
      <h1 class="page-title">Agents</h1>
      <p class="page-subtitle">Register and manage AI agents across your organization</p>
    </div>
    <div class="shell-empty">
      <i class="pi pi-sparkles shell-icon" />
      <p class="shell-empty-text">Under construction</p>
    </div>
  </div>
</template>

<style scoped>
.page-header { margin-bottom: 2rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text); margin-bottom: 0.25rem; }
.page-subtitle { font-size: 0.875rem; color: var(--color-text-muted); }
.shell-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 4rem;
  border: 1px dashed var(--color-border-strong);
  border-radius: var(--radius-lg);
  color: var(--color-text-subtle);
}
.shell-icon { font-size: 2rem; color: var(--color-primary); }
.shell-empty-text { font-size: 0.875rem; }
</style>
```

- [ ] **Step 4: Create `src/modules/evaluate/views/DatasetsView.vue`**

```vue
<template>
  <div class="page-shell">
    <div class="page-header">
      <h1 class="page-title">Datasets</h1>
      <p class="page-subtitle">Create and manage evaluation datasets for your agents</p>
    </div>
    <div class="shell-empty">
      <i class="pi pi-database shell-icon" />
      <p class="shell-empty-text">Under construction</p>
    </div>
  </div>
</template>

<style scoped>
.page-header { margin-bottom: 2rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text); margin-bottom: 0.25rem; }
.page-subtitle { font-size: 0.875rem; color: var(--color-text-muted); }
.shell-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 4rem;
  border: 1px dashed var(--color-border-strong);
  border-radius: var(--radius-lg);
  color: var(--color-text-subtle);
}
.shell-icon { font-size: 2rem; color: var(--color-primary); }
.shell-empty-text { font-size: 0.875rem; }
</style>
```

- [ ] **Step 5: Create `src/modules/evaluate/views/EvalRunsView.vue`**

```vue
<template>
  <div class="page-shell">
    <div class="page-header">
      <h1 class="page-title">Eval Runs</h1>
      <p class="page-subtitle">Run automated evaluations against your agent datasets</p>
    </div>
    <div class="shell-empty">
      <i class="pi pi-play-circle shell-icon" />
      <p class="shell-empty-text">Under construction</p>
    </div>
  </div>
</template>

<style scoped>
.page-header { margin-bottom: 2rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text); margin-bottom: 0.25rem; }
.page-subtitle { font-size: 0.875rem; color: var(--color-text-muted); }
.shell-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 4rem;
  border: 1px dashed var(--color-border-strong);
  border-radius: var(--radius-lg);
  color: var(--color-text-subtle);
}
.shell-icon { font-size: 2rem; color: var(--color-primary); }
.shell-empty-text { font-size: 0.875rem; }
</style>
```

- [ ] **Step 6: Create `src/modules/evaluate/views/PlaygroundView.vue`**

```vue
<template>
  <div class="page-shell">
    <div class="page-header">
      <h1 class="page-title">Playground</h1>
      <p class="page-subtitle">Human-in-the-loop manual evaluation and review</p>
    </div>
    <div class="shell-empty">
      <i class="pi pi-eye shell-icon" />
      <p class="shell-empty-text">Under construction</p>
    </div>
  </div>
</template>

<style scoped>
.page-header { margin-bottom: 2rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text); margin-bottom: 0.25rem; }
.page-subtitle { font-size: 0.875rem; color: var(--color-text-muted); }
.shell-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 4rem;
  border: 1px dashed var(--color-border-strong);
  border-radius: var(--radius-lg);
  color: var(--color-text-subtle);
}
.shell-icon { font-size: 2rem; color: var(--color-primary); }
.shell-empty-text { font-size: 0.875rem; }
</style>
```

- [ ] **Step 7: Create `src/modules/analytics/views/AnalyticsView.vue`**

```vue
<template>
  <div class="page-shell">
    <div class="page-header">
      <h1 class="page-title">Analytics</h1>
      <p class="page-subtitle">Accuracy trends, latency distributions, and regression detection</p>
    </div>
    <div class="shell-empty">
      <i class="pi pi-chart-line shell-icon" />
      <p class="shell-empty-text">Under construction</p>
    </div>
  </div>
</template>

<style scoped>
.page-header { margin-bottom: 2rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text); margin-bottom: 0.25rem; }
.page-subtitle { font-size: 0.875rem; color: var(--color-text-muted); }
.shell-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 4rem;
  border: 1px dashed var(--color-border-strong);
  border-radius: var(--radius-lg);
  color: var(--color-text-subtle);
}
.shell-icon { font-size: 2rem; color: var(--color-primary); }
.shell-empty-text { font-size: 0.875rem; }
</style>
```

- [ ] **Step 8: Create `src/modules/settings/views/SettingsView.vue`**

```vue
<template>
  <div class="page-shell">
    <div class="page-header">
      <h1 class="page-title">Settings</h1>
      <p class="page-subtitle">Platform configuration and preferences</p>
    </div>
    <div class="shell-empty">
      <i class="pi pi-cog shell-icon" />
      <p class="shell-empty-text">Under construction</p>
    </div>
  </div>
</template>

<style scoped>
.page-header { margin-bottom: 2rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text); margin-bottom: 0.25rem; }
.page-subtitle { font-size: 0.875rem; color: var(--color-text-muted); }
.shell-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 4rem;
  border: 1px dashed var(--color-border-strong);
  border-radius: var(--radius-lg);
  color: var(--color-text-subtle);
}
.shell-icon { font-size: 2rem; color: var(--color-primary); }
.shell-empty-text { font-size: 0.875rem; }
</style>
```

- [ ] **Step 9: Run tests — confirm all 6 pass**

```bash
cd frontend && npm run test -- tests/views/shell-views.test.js
```

Expected output:
```
✓ Shell views > AgentsView renders its page title "Agents"
✓ Shell views > DatasetsView renders its page title "Datasets"
✓ Shell views > EvalRunsView renders its page title "Eval Runs"
✓ Shell views > PlaygroundView renders its page title "Playground"
✓ Shell views > AnalyticsView renders its page title "Analytics"
✓ Shell views > SettingsView renders its page title "Settings"
Test Files  1 passed (1)
Tests  6 passed (6)
```

- [ ] **Step 10: Commit**

```bash
git add src/modules/registry/ src/modules/evaluate/ src/modules/analytics/ src/modules/settings/ tests/views/shell-views.test.js
git commit -m "feat: add shell views for registry, evaluate, analytics, settings modules"
```

---

## Task 5: Update `src/router/routes.js`

**Files:**
- Modify: `src/router/routes.js`

- [ ] **Step 1: Replace the routes array content**

Open `src/router/routes.js` and replace the entire file content with:

```js
export const routes = [
  // ── Auth ──
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/modules/auth/views/LoginView.vue'),
    meta: { guestOnly: true }
  },

  // ── App (DefaultLayout) ──
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      { path: '', redirect: '/dashboard' },

      // Overview
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/modules/dashboard/views/DashboardView.vue'),
        meta: { requiresAuth: true, title: 'Dashboard' }
      },

      // Registry
      {
        path: 'registry/agents',
        name: 'RegistryAgents',
        component: () => import('@/modules/registry/views/AgentsView.vue'),
        meta: { requiresAuth: true, title: 'Agents' }
      },

      // Evaluate
      {
        path: 'evaluate/datasets',
        name: 'Datasets',
        component: () => import('@/modules/evaluate/views/DatasetsView.vue'),
        meta: { requiresAuth: true, title: 'Datasets' }
      },
      {
        path: 'evaluate/runs',
        name: 'EvalRuns',
        component: () => import('@/modules/evaluate/views/EvalRunsView.vue'),
        meta: { requiresAuth: true, title: 'Eval Runs' }
      },
      {
        path: 'evaluate/playground',
        name: 'Playground',
        component: () => import('@/modules/evaluate/views/PlaygroundView.vue'),
        meta: { requiresAuth: true, title: 'Playground' }
      },

      // Observe
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('@/modules/analytics/views/AnalyticsView.vue'),
        meta: { requiresAuth: true, title: 'Analytics' }
      },

      // Admin
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/modules/users/views/UsersView.vue'),
        meta: { requiresAuth: true, requiresRole: 'admin', title: 'Users' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/modules/settings/views/SettingsView.vue'),
        meta: { requiresAuth: true, requiresRole: 'admin', title: 'Settings' }
      },
    ]
  },

  // ── 404 ──
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/components/shared/NotFoundView.vue')
  }
]
```

- [ ] **Step 2: Commit**

```bash
git add src/router/routes.js
git commit -m "feat: restructure routes to match Phase 1 nav (registry, evaluate, analytics)"
```

---

## Task 6: Update `src/layouts/DefaultLayout.vue`

**Files:**
- Modify: `src/layouts/DefaultLayout.vue`

Two changes: (a) update the `navSections` computed and `ROUTE_LABELS` in `<script setup>`, and (b) fix the hardcoded indigo hex fallback in `<style scoped>`.

- [ ] **Step 1: Replace `navSections` computed property**

In `<script setup>`, find the `navSections` computed and replace it:

```js
const navSections = computed(() => [
  {
    label: 'Overview',
    items: [{ to: '/dashboard', icon: 'pi-th-large', label: 'Dashboard' }],
  },
  {
    label: 'Registry',
    items: [
      { to: '/registry/agents', icon: 'pi-sparkles', label: 'Agents' },
    ],
  },
  {
    label: 'Evaluate',
    items: [
      { to: '/evaluate/datasets',  icon: 'pi-database',    label: 'Datasets' },
      { to: '/evaluate/runs',      icon: 'pi-play-circle', label: 'Eval Runs' },
      { to: '/evaluate/playground',icon: 'pi-eye',         label: 'Playground' },
    ],
  },
  {
    label: 'Observe',
    items: [
      { to: '/analytics', icon: 'pi-chart-line', label: 'Analytics' },
    ],
  },
  ...(auth.user?.is_superuser
    ? [{
        label: 'Admin',
        items: [
          { to: '/users',    icon: 'pi-users', label: 'Users' },
          { to: '/settings', icon: 'pi-cog',   label: 'Settings' },
        ],
      }]
    : []),
])
```

- [ ] **Step 2: Replace `ROUTE_LABELS` map**

Find `const ROUTE_LABELS = { ... }` and replace it:

```js
const ROUTE_LABELS = {
  dashboard:  'Dashboard',
  registry:   'Registry',
  agents:     'Agents',
  evaluate:   'Evaluate',
  datasets:   'Datasets',
  runs:       'Eval Runs',
  playground: 'Playground',
  analytics:  'Analytics',
  settings:   'Settings',
  users:      'Users',
}
```

- [ ] **Step 3: Fix hardcoded indigo hex fallbacks in `<style scoped>`**

In the `<style scoped>` block, there are two places where `#6366f1` is hardcoded. Replace both:

Find:
```css
background: color-mix(in srgb, var(--p-primary-500, #6366f1) 14%, transparent);
```
Replace with:
```css
background: color-mix(in srgb, var(--p-primary-500, var(--color-primary)) 14%, transparent);
```

Find:
```css
background: color-mix(in srgb, var(--p-primary-500, #6366f1) 22%, transparent) !important;
```
Replace with:
```css
background: color-mix(in srgb, var(--p-primary-500, var(--color-primary)) 22%, transparent) !important;
```

- [ ] **Step 4: Commit**

```bash
git add src/layouts/DefaultLayout.vue
git commit -m "feat: restructure sidebar nav and fix amber color references in DefaultLayout"
```

---

## Task 7: Full Regression Check

- [ ] **Step 1: Run the full test suite**

```bash
cd frontend && npm run test
```

Expected: all tests pass (store tests + shell view tests). Zero failures.

- [ ] **Step 2: Start the dev server and verify visually**

```bash
cd frontend && npm run dev
```

Open `http://localhost:3000` in a browser. Verify:

1. Background is near-black (`#0A0B0D`) — not the previous blue-tinted dark
2. Sidebar shows the new sections: Overview, Registry, Evaluate, Observe, Admin
3. Active nav item highlight is **amber**, not indigo
4. Navigate to `/registry/agents` — page renders "Agents" title and amber construction icon
5. Navigate to `/evaluate/datasets` — page renders "Datasets" title
6. Navigate to `/evaluate/runs` — page renders "Eval Runs" title
7. Navigate to `/evaluate/playground` — page renders "Playground" title
8. Navigate to `/analytics` — page renders "Analytics" title
9. PrimeVue components (breadcrumb, avatar, tags) use amber accent

- [ ] **Step 3: Run lint**

```bash
cd frontend && npm run lint
```

Expected: no errors.

- [ ] **Step 4: Final commit if any lint fixes were applied**

```bash
git add -A && git commit -m "fix: lint cleanup after theme restructure" --allow-empty
```

---

## Out of Scope

- Building actual feature UI for any new module
- Migrating or deleting old module views (`agents/`, `runs/`, `tools/`, etc.)
- Backend changes
- Authentication flow changes
