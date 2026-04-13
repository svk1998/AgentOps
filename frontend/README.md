# AgentOps

Platform for managing AI agents, optimizing prompts, and routing across cloud and self-hosted models.

## Stack

| Concern       | Library                     |
|---------------|-----------------------------|
| Framework     | Vue 3 (Composition API)     |
| Build         | Vite 5                      |
| Routing       | Vue Router 4                |
| State         | Pinia + persistedstate      |
| HTTP          | Axios                       |
| Testing       | Vitest + Vue Test Utils     |

## Project Structure

```
src/
├── assets/          # Global CSS + static files
├── components/
│   ├── ui/          # Base atomic components (BaseButton, etc.)
│   └── shared/      # Cross-feature components (Navbar, 404, etc.)
├── composables/     # Reusable logic (useFetch, useAsync, useToast)
├── layouts/         # Page layout wrappers
├── modules/         # Feature domains (auth, dashboard, users)
│   └── [feature]/
│       ├── components/
│       ├── composables/
│       ├── views/
│       └── store/   (if feature-scoped store is needed)
├── router/          # Vue Router config + route definitions
├── services/        # Axios instance + feature-specific API calls
├── stores/          # Global Pinia stores
└── utils/           # Pure helper functions
```

## Getting Started

```bash
npm install
npm run dev       # Start dev server at localhost:3000
npm run build     # Production build
npm run test      # Run unit tests
npm run lint      # Lint + autofix
```

## Environment Variables

Copy `.env.development` and update values:
```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_TITLE=AgentOps
```

> Only `VITE_` prefixed variables are exposed to the browser.

## Data Flow

```
Component → Composable → Store → Service → Axios → Backend
```

Never call Axios directly from a component.
