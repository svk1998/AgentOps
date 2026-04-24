# Frontend Architecture

Vue 3 SPA, strictly layered. **Data flows one way:**
`Component → Composable → Store → Service → Axios → Backend`
Components never import Axios directly.

## Folder layout

```
src/
├── assets/                    ← global CSS (theme tokens, reset, utilities)
│   ├── main.css               entry stylesheet (imported by main.js)
│   └── theme.css              design tokens — exact AgentOps standalone palette
│
├── components/
│   ├── ui/                    ← canonical design system — 11 reusable components
│   │   │   Visual atoms (pure presentation)
│   │   ├── Chip.vue           pill with variants (ok/warn/err/info/accent)
│   │   ├── StatusDot.vue      semantic status indicator
│   │   ├── Sparkline.vue      SVG mini-chart
│   │   │   Data display
│   │   ├── DataTable.vue      data-dense table, slot-based cell rendering
│   │   ├── Kpi.vue            label + value + delta + sparkline KPI card
│   │   ├── Panel.vue          titled card with header + actions slot
│   │   │   Layout / page chrome
│   │   ├── PageHeader.vue     every view's top block: eyebrow + title + meta + actions
│   │   ├── EmptyState.vue     icon + title + subtitle for empty lists
│   │   │   Forms / interaction
│   │   ├── FormField.vue      label + control slot + hint + error wrapper
│   │   ├── SearchInput.vue    search input with magnifier icon + clear button
│   │   └── Dialog.vue         Teleport'd modal with ESC + backdrop close + autofocus
│   └── _legacy/               ← pre-Phase-1 App* components, kept for
│                                orphaned modules only (not used by new views)
│
├── composables/               ← shared composition-function utilities
│   ├── useApi.js              standard {data, error, loading, refetch} fetch
│   ├── useToast.js            toast (wraps PrimeVue's useToast)
│   ├── useConfirm.js          confirmation dialog (wraps PrimeVue useConfirm)
│   └── useAsync.js            generic async state helper
│
├── constants/
│   └── enums.js               shared backend-enum values (AGENT_TYPES, USER_ROLES, …)
│
├── layouts/
│   └── DefaultLayout.vue      app shell: sidebar, topbar, user menu
│
├── modules/                   ← feature-scoped code
│   └── <feature>/
│       ├── views/             routed pages
│       └── components/        feature-specific components (optional)
│
│   Active modules (Phase 1):
│     auth         — login
│     account      — self-profile (/account)
│     dashboard    — Fleet overview (/dashboard)
│     registry     — agent registry (/registry/agents)
│     evaluate     — datasets, runs, playground
│     analytics    — per-agent analytics
│     users        — admin user CRUD (/users, /users/:id)
│     settings     — admin platform settings
│
│   Legacy modules (orphaned, not in nav — kept for migration):
│     agents, runs, tools, models, prompt-optimizer, workflows
│
├── router/
│   ├── index.js               router instance + global guards
│   └── routes.js              route tree
│
├── services/                  ← resource-specific axios wrappers
│   ├── api.js                 axios instance (VITE_API_BASE_URL)
│   ├── interceptors.js        request (attach JWT) + response (401 → logout)
│   ├── authService.js         /auth/* endpoints
│   ├── agentService.js        /agents/* endpoints
│   ├── datasetService.js      /datasets/* endpoints
│   ├── evalRunService.js      /eval-runs/* endpoints
│   ├── manualEvalService.js   /manual-eval/* endpoints
│   ├── analyticsService.js    /analytics/* endpoints
│   ├── ragDatasetService.js   /rag-datasets/* endpoints
│   └── userService.js         /users/* endpoints
│
├── stores/                    ← Pinia stores (global state)
│   ├── auth.js                user session, token, login/logout/refresh
│   └── theme.js               light/dark mode
│
├── utils/
│   └── format.js              pure formatters (dates, numbers, tokens)
│
├── App.vue                    root component — RouterView + Toast + ConfirmDialog
└── main.js                    app bootstrap (installs Pinia, router, PrimeVue;
                                awaits auth.init() before mount)
```

## Libraries we use

| Library | Purpose |
|---|---|
| **Vue 3** + `<script setup>` | component framework |
| **Vue Router 4** | routing + global auth guard |
| **Pinia** | state management, persisted via `pinia-plugin-persistedstate` |
| **Axios** | HTTP client (single instance in `services/api.js`) |
| **Vite** | build tool |
| **lucide-vue-next** | icon library — used **everywhere** for icons |
| **jwt-decode** | client-side JWT `exp` claim decoding for session management |
| **PrimeVue** (limited) | Toast + ConfirmDialog services only. Custom UI primitives for everything visible |

### Why no generic UI framework?

The design is very specific (amber accent on near-black, 10.5px uppercase
mono labels, tabular numerics, 1-px-gap KPI strips). Vuetify / Element Plus
/ Naive UI would all require heavy restyling and still fight us on details.
Headless libs like `reka-ui` or `@headlessui/vue` are a good alternative
**if** we need more a11y-correct behavior than we've built — but at this
scale PrimeVue's Toast + ConfirmDialog services cover it, and our own
`<Dialog>` wraps the remaining modal pattern we actually need.

**Rule of thumb:**
 - Something repeated across 3+ views → make it a reusable component in
   `components/ui/` using our tokens.
 - Something that requires focus-trap / keyboard nav / ARIA we don't want
   to own → reach for a library (PrimeVue today; add `reka-ui` if needed).

## Standard patterns

### Data-fetching in a view

```js
import { useApi } from '@/composables/useApi'
import { agentService } from '@/services/agentService'

const filters = ref({ status: '' })

const { data: agents, error, loading, refetch } = useApi(
  () => agentService.list(filters.value),
  { initialData: [], watchDeps: [() => filters.value.status] },
)
```

`useApi` auto-fetches on mount, re-fetches when `watchDeps` change, and exposes
`refetch()` to trigger manually (e.g., after a mutation).

### User feedback

```js
import { useToast } from '@/composables/useToast'
const toast = useToast()

toast.success('Created agent')
toast.error('Failed to save — network issue')
```

### Confirmation dialogs

```js
import { useConfirm } from '@/composables/useConfirm'
const confirm = useConfirm()

confirm.danger({
  message: 'Deactivate this user? They will no longer sign in.',
  accept: async () => { await userService.remove(id); await refetch() },
})
```

### Shared enums

Use the canonical lists from `constants/enums.js` instead of inlining string
arrays. This keeps dropdowns, StatusDot mappings, and Chip variants
consistent across views.

```js
import { USER_ROLES, USER_ROLE_CHIP, RUN_STATUS_DOT } from '@/constants/enums'
```

## Adding a new feature module

1. Create `src/modules/<feature>/`
2. Add `views/<Feature>View.vue` — the routed page
3. Add a route entry in `src/router/routes.js` with appropriate `meta`
4. Add a nav entry in `DefaultLayout.vue`'s `navSections` (if user-facing)
5. Add a corresponding service in `src/services/<feature>Service.js`
6. If the feature has its own enum values, add them to `constants/enums.js`

## Design system references

- **Tokens**: `src/assets/theme.css` — `--bg`, `--accent`, `--border`,
  `--text`, `--text-dim`, etc. All amber/neutral-dark from the AgentOps
  standalone. Light theme variants under `[data-theme="light"]`.
- **Global classes**: `src/assets/theme.css` — `.btn`, `.chip`, `.card`,
  `.kbd`, `.input`, plus layout helpers `.hstack`, `.vstack`, `.spacer`,
  `.mono`, `.dim`, `.faint`.
- **Typography**: `Inter Tight` (sans), `JetBrains Mono` (mono) — loaded
  from Google Fonts in `index.html`.

## Auth state

See `src/stores/auth.js` for the full flow. Key points:

- Only the **raw JWT** is persisted. User data is always re-fetched via
  `GET /auth/me` on boot, so revoked/edited users re-hydrate with fresh
  role and active state.
- `auth.init()` runs in `main.js` **before** `app.mount()` so route
  guards see the correct `isLoggedIn` value on the first navigation.
- Tokens auto-refresh **2 minutes before expiry** via `/auth/refresh`.
  A failed refresh routes to `/login?reason=session-expired`.
