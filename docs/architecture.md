# AgentOps — Architecture Diagrams

## 1. Application Architecture

Data always flows in one direction through fixed layers.
Components never call Axios directly — they go through stores and services.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "13px"}}}%%
graph LR
    subgraph SPA["🖥️  Browser — Vue 3 SPA"]
        direction TB

        subgraph VIEWS["Views   src/modules/*/views/"]
            direction LR
            V1["LoginView"]
            V2["DashboardView"]
            V3["AgentsView\nAgentDetailView"]
            V4["PromptOptimizerView\nRunHistoryView"]
            V5["UsersView"]
        end

        subgraph COMP["Composables   src/composables/"]
            direction LR
            C1["useAsync\nloading · error wrapper"]
            C2["useFetch\nreactive URL fetching"]
            C3["useToast\nglobal notifications"]
        end

        subgraph STORES["Pinia Stores   src/stores/"]
            direction LR
            SA["authStore\ntoken persisted to localStorage\nuser re-fetched on boot"]
            SU["userStore"]
            SG["agentStore"]
            SP["promptOptimizerStore"]
        end

        subgraph SVC["Services   src/services/"]
            direction LR
            SV1["authService"]
            SV2["userService"]
            SV3["agentService"]
            SV4["promptOptimizerService"]
        end

        subgraph HTTP["HTTP Layer   src/services/"]
            AX["Axios Instance\napi.js\nbaseURL · timeout · JSON headers"]
            INT["interceptors.js\nrequest — attach Authorization: Bearer token\nresponse — 401 logout · 403 warn · 5xx log"]
        end

        VIEWS -->|"read state, dispatch actions"| STORES
        VIEWS -->|"wrap calls with loading/error"| COMP
        COMP  -->|"call store actions"| STORES
        STORES --> SV1 & SV2 & SV3 & SV4
        SV1 & SV2 & SV3 & SV4 --> AX
        AX --> INT
    end

    BE[("Backend API\nVITE_API_BASE_URL\nproxied to :8000 in dev")]
    INT -->|"REST / JSON"| BE

    classDef views  fill:#4f46e5,color:#fff,stroke:#3730a3
    classDef comp   fill:#0891b2,color:#fff,stroke:#0e7490
    classDef stores fill:#059669,color:#fff,stroke:#047857
    classDef svc    fill:#b45309,color:#fff,stroke:#92400e
    classDef http   fill:#475569,color:#fff,stroke:#334155
    classDef be     fill:#7c3aed,color:#fff,stroke:#6d28d9

    class V1,V2,V3,V4,V5 views
    class C1,C2,C3 comp
    class SA,SU,SG,SP stores
    class SV1,SV2,SV3,SV4 svc
    class AX,INT http
    class BE be
```

---

## 2. Router Structure & Auth Guards

All navigation passes through a single `beforeEach` guard in `src/router/index.js`.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "13px"}}}%%
graph TD
    subgraph GUARD["beforeEach guard — src/router/index.js"]
        direction TB
        NAV(["Navigation triggered"])
        NAV --> TITLE["Set document.title from route meta"]
        TITLE --> G1{"guestOnly route\nand user is logged in?"}
        G1 -->|Yes| R_DASH(["→ Dashboard"])
        G1 -->|No| G2{"requiresAuth route\nand user is NOT logged in?"}
        G2 -->|Yes| R_LOGIN(["→ Login\nwith ?redirect=intended-url"])
        G2 -->|No| G3{"requiresRole set\nand role mismatch?"}
        G3 -->|Yes| R_DASH2(["→ Dashboard"])
        G3 -->|No| PROCEED(["✓ Proceed to route"])
    end

    subgraph ROUTES["Route Map — src/router/routes.js"]
        direction TB
        LOGIN_R["/login\nguestOnly · no layout wrapper"]

        subgraph LAYOUT["/ — DefaultLayout  sidebar + topbar"]
            DASH_R["/dashboard\nrequiresAuth"]
            PO_R["/prompt-optimizer\nrequiresAuth"]
            POH_R["/prompt-optimizer/history\nrequiresAuth"]
            AG_R["/agents\nrequiresAuth"]
            AGD_R["/agents/:id\nrequiresAuth"]
            USR_R["/users\nrequiresAuth · requiresRole: admin"]
        end

        CATCH_R["/:pathMatch — NotFoundView\n404 catch-all"]
    end

    classDef decision fill:#f59e0b,color:#000,stroke:#d97706
    classDef terminal fill:#059669,color:#fff,stroke:#047857
    classDef block    fill:#4f46e5,color:#fff,stroke:#3730a3
    classDef route    fill:#0891b2,color:#fff,stroke:#0e7490
    classDef admin    fill:#dc2626,color:#fff,stroke:#b91c1c

    class G1,G2,G3 decision
    class NAV,PROCEED terminal
    class TITLE block
    class LOGIN_R,DASH_R,PO_R,POH_R,AG_R,AGD_R,CATCH_R route
    class USR_R admin
```

---

## 3. Auth Flow — Boot & Login

Shows token persistence, user rehydration on reload, and role-based navigation.

```mermaid
sequenceDiagram
    actor User
    participant App  as App.vue
    participant Guard as Router beforeEach
    participant Store as authStore
    participant API  as Backend API

    Note over App,API: App boot — rehydrate user from persisted token

    App  ->>  Store : fetchMe()
    alt token found in localStorage
        Store ->> API  : GET /auth/me
        API  -->> Store : user object
        Store -->> App  : user hydrated, isLoggedIn = true
    else no token
        Store -->> App  : stay logged out
    end

    Note over User,Guard: Unauthenticated navigation

    User  ->>  Guard : navigate to /dashboard
    Guard ->>  Store : check isLoggedIn
    Store -->> Guard : false
    Guard -->> User  : redirect → /login?redirect=/dashboard

    Note over User,API: Login

    User  ->>  Store : login(credentials)
    Store ->>  API   : POST /auth/login
    API  -->>  Store : {token, user}
    Store -->> Store : persist token to localStorage
    Store -->> User  : redirect → /dashboard  (from ?redirect param)

    Note over User,Guard: Role-based navigation

    User  ->>  Guard : navigate to /users  (requiresRole: admin)
    Guard ->>  Store : check isLoggedIn
    Store -->> Guard : true
    Guard ->>  Store : hasRole("admin")

    alt user IS admin
        Store -->> Guard : true
        Guard -->> User  : proceed to /users
    else user is NOT admin
        Store -->> Guard : false
        Guard -->> User  : redirect → /dashboard
    end

    Note over User,API: Token expiry

    User  ->>  API   : any authenticated request
    API  -->>  Store : 401 Unauthorized
    Store -->> Store : logout() — clear token + user
    Store -->> User  : redirect → /login
```
