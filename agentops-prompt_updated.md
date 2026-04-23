# AgentOps — AI Agent Operations Platform

## Product Prompt / Specification

---

## Vision

Build **AgentOps** — a full-stack operations platform for registering, evaluating, and managing AI agents across their entire lifecycle. The platform enables teams to register heterogeneous AI agents (LLM-based, RAG pipelines, vision models, multi-step chains), run structured evaluations against curated datasets, perform manual human-in-the-loop verification, and analyze evaluation results through rich dashboards.

---

## Phase 1 — Core Scope (Build Now)

### 1. Agent Registry

A centralized catalog where every AI agent is registered with its metadata.

**Required Fields per Agent:**

| Field | Type | Description |
|---|---|---|
| Agent Name | string | Human-readable identifier (e.g., "Wine Label Recognizer v2") |
| Agent Type | enum | `LLM`, `RAG`, `Vision`, `Multi-Step Chain`, `Tool-Use`, `Custom` |
| Agent Endpoint | URL | The HTTP endpoint to invoke the agent (e.g., `https://api.internal/agents/wine-recognizer`) |
| Model / Provider | string | Underlying model info (e.g., "Gemini 1.5 Pro", "Claude Sonnet", "GPT-4o") |
| Description | text | What the agent does, its purpose, expected input/output |
| Input Schema | JSON | Expected input format (e.g., `{ "image_url": "string", "context": "string" }`) |
| Output Schema | JSON | Expected output format (e.g., `{ "label": "string", "confidence": "float" }`) |
| Version | semver | Agent version for tracking iterations (e.g., "1.2.0") |
| Tags / Labels | string[] | Categorization tags (e.g., `["production", "wine", "vision", "samsung"]`) |
| Owner / Team | string | Responsible team or individual |
| Status | enum | `Draft`, `Active`, `Deprecated`, `Archived` |
| Created At / Updated At | datetime | Timestamps |
| Auth Config | object | How to authenticate with the endpoint (API key header, bearer token, etc.) |

**UI Requirements:**

- Registration form with field validation and JSON schema editor (Monaco-based) for input/output schemas
- Agent list view with search, filter by type/status/tags, and sort
- Agent detail page showing full metadata, evaluation history, and version timeline
- Inline version comparison (diff view of schema changes across versions)

---

### 2. Agent Evaluation System

Three modes of evaluation, all tied to registered agents.

#### 2a. Automated Evaluation with Pre-defined Datasets

Run a registered agent against a curated evaluation dataset and auto-score results.

**Evaluation Dataset Schema:**

```
EvalDataset {
  id: uuid
  name: string                    // e.g., "Wine Label Test Set v3"
  description: text
  agent_type: enum                // Which agent type this dataset targets
  created_by: string
  created_at: datetime
  updated_at: datetime
  tags: string[]
  
  items: EvalDatasetItem[]
}

EvalDatasetItem {
  id: uuid
  dataset_id: uuid (FK)
  input: JSON                     // The input payload to send to the agent
  expected_output: JSON           // Ground truth / expected result
  metadata: JSON                  // Additional context (source, difficulty, category)
  created_at: datetime
}
```

**Eval Run Flow:**

1. User selects an agent + a compatible dataset
2. System iterates over dataset items, calls the agent endpoint with each input
3. Agent response is captured alongside latency, status code, and raw response
4. Auto-scoring compares agent output vs. expected output using configurable matchers:
   - **Exact Match** — strict JSON equality
   - **Fuzzy Match** — similarity threshold (e.g., Levenshtein, cosine on text fields)
   - **Field-Level Match** — compare specific JSON fields independently
   - **LLM-as-Judge** — use a secondary LLM to grade the response against expected output
   - **Custom Scorer** — user-provided scoring function (Python/JS snippet)
5. Results stored per-item with pass/fail + score + matcher details

**Eval Run Record:**

```
EvalRun {
  id: uuid
  agent_id: uuid (FK)
  dataset_id: uuid (FK)
  status: enum (Pending, Running, Completed, Failed)
  started_at: datetime
  completed_at: datetime
  config: JSON                    // Matcher type, thresholds, timeout settings
  summary: {
    total: int
    passed: int
    failed: int
    errored: int
    avg_latency_ms: float
    avg_score: float
  }
  
  results: EvalRunResult[]
}

EvalRunResult {
  id: uuid
  run_id: uuid (FK)
  dataset_item_id: uuid (FK)
  agent_input: JSON
  agent_output: JSON
  expected_output: JSON
  score: float (0.0 - 1.0)
  passed: boolean
  latency_ms: int
  status_code: int
  matcher_details: JSON           // Why it passed/failed, field-level breakdown
  error: string | null
}
```

---

#### 2b. Manual / Human-in-the-Loop Evaluation (Playground)

For cases where automated scoring is insufficient — like verifying Gemini's wine label recognition from field images.

**Playground Workflow (Wine Label Example):**

1. **Input Panel** — Shows the original field image of the wine bottle sent to the agent
2. **Agent Response Panel** — Shows Gemini's raw response: recognized wine name, vintage, region, grape variety, confidence scores
3. **Evaluation Panel** — Human reviewer provides:
   - **Overall Verdict**: `Pass` / `Fail` / `Partial`
   - **Field-Level Verdicts**: For each output field (wine_name, vintage, region, etc.), mark as `Correct`, `Incorrect`, `Partially Correct`, `Not Applicable`
   - **Reviewer Notes**: Free-text explanation of why it failed (e.g., "Vintage recognized as 2019 but bottle shows 2018")
   - **Severity**: `Critical`, `Major`, `Minor` (for failures)
   - **Corrected Output**: Optionally provide the ground truth

**Manual Eval Data Model:**

```
ManualEvalSession {
  id: uuid
  agent_id: uuid (FK)
  eval_run_id: uuid | null        // Can be linked to an automated run or standalone
  reviewer: string
  status: enum (In Progress, Completed)
  created_at: datetime
  completed_at: datetime
}

ManualEvalItem {
  id: uuid
  session_id: uuid (FK)
  agent_input: JSON
  agent_output: JSON
  verdict: enum (Pass, Fail, Partial)
  field_verdicts: JSON            // { "wine_name": "Correct", "vintage": "Incorrect", ... }
  reviewer_notes: text
  severity: enum (Critical, Major, Minor) | null
  corrected_output: JSON | null
  reviewed_at: datetime
}
```

**UI Requirements:**

- Side-by-side layout: Input (image/text) | Agent Output | Evaluation Form
- Keyboard shortcuts for rapid review (P = Pass, F = Fail, arrow keys to navigate)
- Progress bar showing items reviewed / total
- Ability to filter queue by confidence score (review low-confidence items first)
- Image zoom/pan for visual inspection of field images
- Bulk import of agent inputs for manual eval (CSV/JSON upload)

---

#### 2c. Evaluation Analytics & Reporting

Dashboards and analysis over all evaluation results (both automated and manual).

**Metrics & Visualizations:**

- **Accuracy Over Time** — Line chart tracking pass rate across eval runs per agent, with version markers
- **Field-Level Accuracy Heatmap** — Which output fields fail most often (e.g., "vintage" has 72% accuracy but "region" has 95%)
- **Confusion Matrix** — For classification-type agents, show predicted vs. actual categories
- **Latency Distribution** — Histogram of agent response times with P50/P95/P99 markers
- **Error Breakdown** — Pie chart of failure categories (wrong answer, timeout, malformed response, auth error)
- **Reviewer Agreement** — Inter-annotator agreement (Cohen's Kappa) when multiple reviewers evaluate the same items
- **Regression Detection** — Automatic comparison between current run and last N runs; flag if accuracy drops > configurable threshold
- **Cost Tracking** — If agent uses paid APIs, estimate cost per eval run based on token/call counts

**Filtering & Drill-Down:**

- Filter by agent, agent type, dataset, date range, version, reviewer
- Click any data point to see underlying eval items
- Export results as CSV/JSON

---

### 3. Evaluation Dataset Management

A first-class system for creating, curating, versioning, and organizing evaluation datasets.

**Features:**

- **CRUD Operations** — Create/Read/Update/Delete datasets and their items
- **Bulk Import** — Upload CSV, JSON, or JSONL files to populate dataset items
- **Bulk Export** — Download datasets in CSV/JSON/JSONL format
- **Schema Validation** — Validate that dataset items conform to the target agent's input/output schemas
- **Versioning** — Snapshot datasets before modification; track changes over time; rollback to previous versions
- **Tagging & Search** — Tag datasets by domain, difficulty, agent type; full-text search across dataset items
- **Dataset Statistics** — Item count, label distribution, coverage metrics, freshness indicators
- **Sampling** — Create evaluation subsets via random sampling or stratified sampling by metadata fields
- **Dataset Linking** — Link datasets to specific agent types; prevent incompatible agent-dataset pairings during eval runs
- **Annotation Workflow** — For datasets that need human labeling, support assign → label → review → approve pipeline

**Dataset Item Editor UI:**

- Table view with inline editing for simple datasets
- Card view for image/rich-media datasets (show image thumbnail + associated metadata)
- JSON editor for complex input/output pairs
- Diff view when editing to show what changed

---

### 4. RAG Evaluation & Dataset Management

Specialized evaluation support for Retrieval-Augmented Generation pipelines.

**RAG-Specific Eval Dimensions:**

| Metric | What It Measures |
|---|---|
| **Retrieval Relevance** | Are the retrieved chunks actually relevant to the query? |
| **Retrieval Completeness** | Did the retriever find ALL relevant chunks? |
| **Context Faithfulness** | Does the generated answer stick to retrieved context (no hallucination)? |
| **Answer Relevance** | Does the final answer actually address the user's question? |
| **Answer Correctness** | Is the answer factually correct compared to ground truth? |
| **Chunk Attribution** | Can each claim in the answer be traced to a specific chunk? |

**RAG Dataset Schema:**

```
RAGEvalDataset {
  id: uuid
  name: string
  knowledge_base_ref: string      // Reference to the knowledge base being tested
  
  items: RAGEvalItem[]
}

RAGEvalItem {
  id: uuid
  query: string                   // User question
  expected_answer: string         // Ground truth answer
  relevant_chunk_ids: string[]    // IDs of chunks that SHOULD be retrieved
  relevant_passages: string[]     // Text of relevant passages (for scoring)
  metadata: JSON                  // Difficulty, category, source document, etc.
}
```

**RAG Eval Run captures additional data:**

```
RAGEvalResult extends EvalRunResult {
  retrieved_chunks: {
    chunk_id: string
    content: string
    relevance_score: float
    was_expected: boolean
  }[]
  retrieval_precision: float
  retrieval_recall: float
  faithfulness_score: float
  answer_relevance_score: float
  chunk_attribution: JSON         // Mapping of answer claims to source chunks
}
```

**RAG Dataset Management Additions:**

- **Knowledge Base Sync** — Import chunks from a vector store to reference as ground truth
- **Question Generation** — Optionally use LLM to auto-generate test questions from knowledge base passages
- **Chunk Viewer** — Side-by-side view of query → retrieved chunks → generated answer, with relevance highlighting
- **Retrieval Tuning Insights** — Show how changing top-k, similarity threshold affects retrieval metrics

---

## Phase 2 — Advanced Lifecycle & Observability (Plan Ahead, Build Later)

### A. Standardized Agent Lifecycle (Offline & Online)

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  BUILD    │───▶│  TEST    │───▶│  DEPLOY  │───▶│ MONITOR  │
│           │    │          │    │          │    │          │
│ Register  │    │ Eval     │    │ Staged   │    │ Live     │
│ Version   │    │ Suite    │    │ Rollout  │    │ Metrics  │
│ Schema    │    │ Pass     │    │ Canary   │    │ Alerts   │
│ Config    │    │ Gate     │    │ Promote  │    │ Drift    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

**BUILD** — Agent registration + versioning (Phase 1 covers this)

**TEST** — Quality gates that must pass before deployment:
- Minimum accuracy threshold on designated eval datasets
- No regression vs. previous version beyond allowed delta
- Latency within SLA bounds
- Cost per invocation within budget

**DEPLOY** — Staged rollout:
- Canary deployment (route 5% traffic to new version)
- Progressive rollout (5% → 25% → 50% → 100%)
- Traffic splitting with configurable routing rules
- Automatic rollback trigger: if live error rate exceeds threshold, revert to last stable version

**MONITOR** — Continuous observability:
- Live accuracy sampling (periodically send production inputs through eval pipeline)
- Latency dashboards (real-time P50/P95/P99)
- Cost accumulation tracking
- Data drift detection (alert when input distribution shifts from eval dataset distribution)
- Model drift detection (alert when output quality degrades over time)

---

### B. Validation & Observability

**Scenario / Regression Testing:**

- Define test scenarios as named collections of eval cases representing critical user journeys
- Run regression suites on every agent version bump (CI/CD integration via webhook)
- Diff reports: show exactly which test cases flipped from pass → fail between versions
- Flaky test detection: flag test cases with inconsistent results across runs

**End-to-End Tracing:**

- Distributed tracing for multi-step agent pipelines (e.g., Image → OCR → LLM → Post-processing)
- Each step logged with: input, output, latency, token count, model called, cost
- Trace waterfall visualization (similar to Jaeger/Zipkin but for agent pipelines)
- Span-level error attribution: when a pipeline fails, pinpoint which step caused the failure

**Staged Rollouts & Automatic Rollbacks:**

- Deployment environments: `dev` → `staging` → `canary` → `production`
- Promotion rules engine: "Promote to production only if canary accuracy > 95% over 1 hour on > 100 requests"
- Rollback triggers: error rate spike, latency degradation, accuracy drop below threshold
- Rollback executes in < 30 seconds; notification sent to agent owner

---

### C. Evaluation Metrics Framework

Three pillars of agent quality:

**1. Accuracy Metrics:**

| Metric | Scope | Description |
|---|---|---|
| Pass Rate | Overall | % of eval items that pass |
| Field Accuracy | Per-field | % correct per output field |
| Precision / Recall / F1 | Classification agents | Standard classification metrics |
| BLEU / ROUGE / BERTScore | Text generation agents | Text quality metrics |
| Exact Match (EM) | QA agents | % of answers that exactly match ground truth |
| Hallucination Rate | RAG agents | % of claims not grounded in retrieved context |

**2. Reasoning Quality Metrics:**

| Metric | Description |
|---|---|
| Chain-of-Thought Coherence | Does the reasoning follow logically step-by-step? |
| Tool Use Correctness | Does the agent invoke the right tools with correct parameters? |
| Instruction Following | Does the agent follow all constraints in the prompt? |
| Step Completion Rate | For multi-step agents, what % of required steps execute correctly? |

**3. Cost & Latency Metrics:**

| Metric | Description |
|---|---|
| Tokens In / Out | Input and output token counts per invocation |
| Cost per Invocation | Estimated $ cost (model pricing × token counts) |
| Cost per Correct Answer | Total cost / number of correct answers (efficiency metric) |
| Time to First Token (TTFT) | Latency before first response token |
| End-to-End Latency | Total time from request to complete response |
| Throughput | Requests per second the agent can handle |

---

## Tech Stack Recommendations

| Layer | Technology |
|---|---|
| **Frontend** | Vue 3 + TypeScript, Pinia (state), Vue Router, Vite, TailwindCSS |
| **UI Components** | Shadcn-vue or PrimeVue for data tables, forms, charts |
| **Code/JSON Editor** | Monaco Editor (for schema editing, custom scorer code) |
| **Charts** | Apache ECharts or Chart.js for analytics dashboards |
| **Backend** | FastAPI (Python) with async support |
| **Database** | PostgreSQL 16+ (primary store — JSONB, arrays, window functions) + Redis (caching, job queues, eval progress) |
| **Task Queue** | Celery or Kafka for async eval run execution |
| **Auth** | JWT-based with role-based access control |
| **Containerization** | Docker Compose (dev), Kubernetes (prod) |

---

## Data Model — PostgreSQL DDL (Phase 1)

### Why PostgreSQL

- **JSONB** — Binary-stored, GIN-indexable JSON for agent schemas, eval payloads, matcher details, field verdicts. Queryable with `@>`, `->`, `->>` operators.
- **Native arrays** — `TEXT[]` for tags, `UUID[]` for chunk IDs. GIN-indexed for containment queries.
- **Analytical functions** — `percentile_cont()` for P50/P95/P99 latency, window functions for regression detection, `FILTER` clauses for conditional aggregates.
- **MVCC** — Readers never block writers. Critical for concurrent eval runs + live analytics.

### Extensions & Setup

```sql
-- Required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";       -- uuid_generate_v4()
CREATE EXTENSION IF NOT EXISTS "pgcrypto";         -- gen_random_uuid() alternative
CREATE EXTENSION IF NOT EXISTS "pg_trgm";          -- Trigram fuzzy search on names/descriptions

-- Custom enum types
CREATE TYPE agent_type AS ENUM (
    'llm', 'rag', 'vision', 'multi_step_chain', 'tool_use', 'custom'
);

CREATE TYPE agent_status AS ENUM (
    'draft', 'active', 'deprecated', 'archived'
);

CREATE TYPE eval_run_status AS ENUM (
    'pending', 'running', 'completed', 'failed', 'cancelled'
);

CREATE TYPE manual_verdict AS ENUM (
    'pass', 'fail', 'partial'
);

CREATE TYPE severity_level AS ENUM (
    'critical', 'major', 'minor'
);

CREATE TYPE manual_session_status AS ENUM (
    'in_progress', 'completed'
);

CREATE TYPE dataset_item_status AS ENUM (
    'active', 'disabled', 'flagged'
);

CREATE TYPE user_role AS ENUM (
    'admin', 'evaluator', 'viewer'
);
```

### Core Tables

```sql
-- ============================================================
-- USERS & AUTH
-- ============================================================

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    display_name    VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            user_role NOT NULL DEFAULT 'viewer',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_role ON users (role);


-- ============================================================
-- AGENT REGISTRY
-- ============================================================

CREATE TABLE agents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    agent_type      agent_type NOT NULL,
    endpoint_url    VARCHAR(2048) NOT NULL,
    model_provider  VARCHAR(255),                       -- e.g., "Gemini 1.5 Pro", "Claude Sonnet"
    description     TEXT,
    input_schema    JSONB NOT NULL DEFAULT '{}',         -- JSON Schema defining expected input
    output_schema   JSONB NOT NULL DEFAULT '{}',         -- JSON Schema defining expected output
    version         VARCHAR(50) NOT NULL DEFAULT '1.0.0',-- semver
    tags            TEXT[] NOT NULL DEFAULT '{}',         -- PostgreSQL array, GIN-indexed
    owner           VARCHAR(255),                        -- team or individual
    status          agent_status NOT NULL DEFAULT 'draft',
    auth_config     JSONB DEFAULT '{}',                  -- { "type": "bearer", "header": "Authorization", ... }
    config          JSONB DEFAULT '{}',                  -- Additional agent-specific config (timeout, retries, etc.)
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agents_type ON agents (agent_type);
CREATE INDEX idx_agents_status ON agents (status);
CREATE INDEX idx_agents_tags ON agents USING GIN (tags);
CREATE INDEX idx_agents_name_trgm ON agents USING GIN (name gin_trgm_ops);
CREATE INDEX idx_agents_created_at ON agents (created_at DESC);


-- Agent version history — snapshot on every update
CREATE TABLE agent_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id        UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    version         VARCHAR(50) NOT NULL,
    snapshot        JSONB NOT NULL,                      -- Full agent state at this version
    change_summary  TEXT,                                -- What changed (human-written or auto-diff)
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agent_versions_agent ON agent_versions (agent_id, created_at DESC);
CREATE UNIQUE INDEX idx_agent_versions_unique ON agent_versions (agent_id, version);


-- ============================================================
-- EVALUATION DATASETS
-- ============================================================

CREATE TABLE eval_datasets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    agent_type      agent_type,                          -- Target agent type (for compatibility check)
    tags            TEXT[] NOT NULL DEFAULT '{}',
    item_count      INTEGER NOT NULL DEFAULT 0,          -- Denormalized counter
    current_version INTEGER NOT NULL DEFAULT 1,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_eval_datasets_agent_type ON eval_datasets (agent_type);
CREATE INDEX idx_eval_datasets_tags ON eval_datasets USING GIN (tags);
CREATE INDEX idx_eval_datasets_name_trgm ON eval_datasets USING GIN (name gin_trgm_ops);


CREATE TABLE eval_dataset_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID NOT NULL REFERENCES eval_datasets(id) ON DELETE CASCADE,
    input           JSONB NOT NULL,                      -- Input payload to send to agent
    expected_output JSONB NOT NULL,                      -- Ground truth
    metadata        JSONB DEFAULT '{}',                  -- Category, difficulty, source, notes
    status          dataset_item_status NOT NULL DEFAULT 'active',
    sort_order      INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_dataset_items_dataset ON eval_dataset_items (dataset_id);
CREATE INDEX idx_dataset_items_status ON eval_dataset_items (dataset_id, status);
CREATE INDEX idx_dataset_items_metadata ON eval_dataset_items USING GIN (metadata);


-- Dataset version snapshots — frozen copies for reproducibility
CREATE TABLE dataset_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID NOT NULL REFERENCES eval_datasets(id) ON DELETE CASCADE,
    version_number  INTEGER NOT NULL,
    item_count      INTEGER NOT NULL,
    snapshot_data   JSONB NOT NULL,                      -- Array of all items at snapshot time
    notes           TEXT,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_dataset_versions_unique ON dataset_versions (dataset_id, version_number);


-- ============================================================
-- RAG-SPECIFIC DATASETS
-- ============================================================

CREATE TABLE rag_eval_datasets (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    knowledge_base_ref  VARCHAR(512),                    -- Reference to the KB being tested
    tags                TEXT[] NOT NULL DEFAULT '{}',
    item_count          INTEGER NOT NULL DEFAULT 0,
    created_by          UUID REFERENCES users(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rag_datasets_tags ON rag_eval_datasets USING GIN (tags);


CREATE TABLE rag_eval_items (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id          UUID NOT NULL REFERENCES rag_eval_datasets(id) ON DELETE CASCADE,
    query               TEXT NOT NULL,                   -- User question
    expected_answer     TEXT NOT NULL,                   -- Ground truth answer
    relevant_chunk_ids  TEXT[] NOT NULL DEFAULT '{}',    -- Chunk IDs that SHOULD be retrieved
    relevant_passages   TEXT[] NOT NULL DEFAULT '{}',    -- Text of relevant passages
    metadata            JSONB DEFAULT '{}',              -- Difficulty, category, source doc
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rag_items_dataset ON rag_eval_items (dataset_id);
CREATE INDEX idx_rag_items_chunks ON rag_eval_items USING GIN (relevant_chunk_ids);


-- ============================================================
-- EVALUATION RUNS
-- ============================================================

CREATE TABLE eval_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id        UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    dataset_id      UUID REFERENCES eval_datasets(id),       -- NULL if RAG dataset
    rag_dataset_id  UUID REFERENCES rag_eval_datasets(id),   -- NULL if standard dataset
    status          eval_run_status NOT NULL DEFAULT 'pending',
    config          JSONB NOT NULL DEFAULT '{}',              -- Matcher type, thresholds, timeout, concurrency
    
    -- Denormalized summary (updated on completion)
    total_items     INTEGER NOT NULL DEFAULT 0,
    passed          INTEGER NOT NULL DEFAULT 0,
    failed          INTEGER NOT NULL DEFAULT 0,
    errored         INTEGER NOT NULL DEFAULT 0,
    avg_latency_ms  DOUBLE PRECISION,
    avg_score       DOUBLE PRECISION,
    p50_latency_ms  DOUBLE PRECISION,
    p95_latency_ms  DOUBLE PRECISION,
    p99_latency_ms  DOUBLE PRECISION,
    total_cost_usd  DOUBLE PRECISION,                         -- Estimated cost if applicable
    
    agent_version   VARCHAR(50),                              -- Snapshot of agent version at run time
    triggered_by    UUID REFERENCES users(id),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Ensure exactly one dataset type is linked
    CONSTRAINT chk_dataset_type CHECK (
        (dataset_id IS NOT NULL AND rag_dataset_id IS NULL) OR
        (dataset_id IS NULL AND rag_dataset_id IS NOT NULL)
    )
);

CREATE INDEX idx_eval_runs_agent ON eval_runs (agent_id, created_at DESC);
CREATE INDEX idx_eval_runs_dataset ON eval_runs (dataset_id) WHERE dataset_id IS NOT NULL;
CREATE INDEX idx_eval_runs_rag_dataset ON eval_runs (rag_dataset_id) WHERE rag_dataset_id IS NOT NULL;
CREATE INDEX idx_eval_runs_status ON eval_runs (status);
CREATE INDEX idx_eval_runs_agent_version ON eval_runs (agent_id, agent_version);


-- Individual eval results per dataset item
CREATE TABLE eval_run_results (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id              UUID NOT NULL REFERENCES eval_runs(id) ON DELETE CASCADE,
    dataset_item_id     UUID,                                -- FK to eval_dataset_items or rag_eval_items
    item_index          INTEGER NOT NULL,                    -- Order within the run
    
    agent_input         JSONB NOT NULL,                      -- Actual input sent
    agent_output        JSONB,                               -- Agent's response (NULL if errored)
    expected_output     JSONB NOT NULL,                      -- Ground truth
    
    score               DOUBLE PRECISION,                    -- 0.0 - 1.0
    passed              BOOLEAN,
    latency_ms          INTEGER,
    status_code         INTEGER,                             -- HTTP status from agent endpoint
    tokens_in           INTEGER,                             -- If available from response headers
    tokens_out          INTEGER,
    estimated_cost_usd  DOUBLE PRECISION,
    
    matcher_details     JSONB DEFAULT '{}',                  -- Field-level breakdown, why pass/fail
    error               TEXT,                                -- Error message if failed
    raw_response        JSONB,                               -- Full HTTP response for debugging
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_eval_results_run ON eval_run_results (run_id);
CREATE INDEX idx_eval_results_passed ON eval_run_results (run_id, passed);
CREATE INDEX idx_eval_results_score ON eval_run_results (run_id, score);
CREATE INDEX idx_eval_results_item ON eval_run_results (dataset_item_id) WHERE dataset_item_id IS NOT NULL;


-- RAG-specific result extensions (separate table to keep eval_run_results clean)
CREATE TABLE rag_eval_result_details (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    eval_result_id          UUID NOT NULL UNIQUE REFERENCES eval_run_results(id) ON DELETE CASCADE,
    
    retrieved_chunks        JSONB NOT NULL DEFAULT '[]',     -- Array of { chunk_id, content, relevance_score, was_expected }
    retrieval_precision     DOUBLE PRECISION,
    retrieval_recall        DOUBLE PRECISION,
    faithfulness_score      DOUBLE PRECISION,                -- Does answer stick to context?
    answer_relevance_score  DOUBLE PRECISION,                -- Does answer address the query?
    chunk_attribution       JSONB DEFAULT '{}',              -- Mapping: answer claims → source chunks
    
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rag_details_result ON rag_eval_result_details (eval_result_id);


-- ============================================================
-- MANUAL / HUMAN-IN-THE-LOOP EVALUATION
-- ============================================================

CREATE TABLE manual_eval_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id        UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    eval_run_id     UUID REFERENCES eval_runs(id),           -- Optional: linked to automated run
    name            VARCHAR(255),
    description     TEXT,
    status          manual_session_status NOT NULL DEFAULT 'in_progress',
    
    total_items     INTEGER NOT NULL DEFAULT 0,
    reviewed_count  INTEGER NOT NULL DEFAULT 0,              -- Denormalized progress counter
    
    assignment_config JSONB DEFAULT '{}',                    -- Reviewer assignments, round-robin config
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

CREATE INDEX idx_manual_sessions_agent ON manual_eval_sessions (agent_id);
CREATE INDEX idx_manual_sessions_run ON manual_eval_sessions (eval_run_id) WHERE eval_run_id IS NOT NULL;
CREATE INDEX idx_manual_sessions_status ON manual_eval_sessions (status);


CREATE TABLE manual_eval_items (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES manual_eval_sessions(id) ON DELETE CASCADE,
    eval_result_id      UUID REFERENCES eval_run_results(id),-- Optional: linked to automated result
    item_index          INTEGER NOT NULL,
    
    agent_input         JSONB NOT NULL,                      -- Original input (image URL, text, etc.)
    agent_output        JSONB NOT NULL,                      -- Agent's response to verify
    
    -- Review fields (NULL until reviewed)
    verdict             manual_verdict,
    field_verdicts      JSONB,                               -- { "wine_name": "correct", "vintage": "incorrect", ... }
    severity            severity_level,
    reviewer_notes      TEXT,
    corrected_output    JSONB,                               -- Ground truth provided by reviewer
    
    reviewer_id         UUID REFERENCES users(id),
    assigned_to         UUID REFERENCES users(id),           -- Pre-assignment for queue distribution
    is_reviewed         BOOLEAN NOT NULL DEFAULT FALSE,
    reviewed_at         TIMESTAMPTZ,
    review_duration_ms  INTEGER,                             -- Time spent reviewing (for analytics)
    
    -- Optimistic locking for concurrent reviewers
    lock_version        INTEGER NOT NULL DEFAULT 0,
    locked_by           UUID REFERENCES users(id),
    locked_at           TIMESTAMPTZ,
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_manual_items_session ON manual_eval_items (session_id);
CREATE INDEX idx_manual_items_unreviewed ON manual_eval_items (session_id, is_reviewed) WHERE NOT is_reviewed;
CREATE INDEX idx_manual_items_reviewer ON manual_eval_items (reviewer_id) WHERE reviewer_id IS NOT NULL;
CREATE INDEX idx_manual_items_verdict ON manual_eval_items (session_id, verdict) WHERE verdict IS NOT NULL;
CREATE INDEX idx_manual_items_assigned ON manual_eval_items (assigned_to) WHERE assigned_to IS NOT NULL;


-- ============================================================
-- AUDIT LOG
-- ============================================================

CREATE TABLE audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id),
    action          VARCHAR(100) NOT NULL,                   -- e.g., "agent.created", "eval_run.started", "dataset.item_added"
    entity_type     VARCHAR(50) NOT NULL,                    -- "agent", "eval_dataset", "eval_run", etc.
    entity_id       UUID NOT NULL,
    changes         JSONB,                                   -- { "field": { "old": ..., "new": ... } }
    ip_address      INET,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_entity ON audit_log (entity_type, entity_id, created_at DESC);
CREATE INDEX idx_audit_user ON audit_log (user_id, created_at DESC);
CREATE INDEX idx_audit_action ON audit_log (action, created_at DESC);
-- Partition by month for large-scale deployments
-- CREATE TABLE audit_log (...) PARTITION BY RANGE (created_at);
```

### Useful Analytical Views

```sql
-- ============================================================
-- VIEWS FOR ANALYTICS QUERIES
-- ============================================================

-- Agent accuracy trend (per run)
CREATE VIEW v_agent_accuracy_trend AS
SELECT
    er.agent_id,
    a.name AS agent_name,
    er.id AS run_id,
    er.agent_version,
    er.created_at AS run_date,
    er.total_items,
    er.passed,
    er.failed,
    er.errored,
    CASE WHEN er.total_items > 0
         THEN ROUND((er.passed::NUMERIC / er.total_items) * 100, 2)
         ELSE 0
    END AS pass_rate_pct,
    er.avg_latency_ms,
    er.p95_latency_ms,
    er.total_cost_usd
FROM eval_runs er
JOIN agents a ON a.id = er.agent_id
WHERE er.status = 'completed'
ORDER BY er.agent_id, er.created_at DESC;


-- Field-level accuracy breakdown (from matcher_details JSONB)
CREATE VIEW v_field_accuracy AS
SELECT
    er.agent_id,
    er.id AS run_id,
    er.agent_version,
    field_key,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE field_value->>'match' = 'true') AS matched,
    ROUND(
        (COUNT(*) FILTER (WHERE field_value->>'match' = 'true'))::NUMERIC / NULLIF(COUNT(*), 0) * 100,
        2
    ) AS accuracy_pct
FROM eval_runs er
JOIN eval_run_results rr ON rr.run_id = er.id
CROSS JOIN LATERAL jsonb_each(rr.matcher_details->'field_results') AS f(field_key, field_value)
WHERE er.status = 'completed'
  AND rr.matcher_details ? 'field_results'
GROUP BY er.agent_id, er.id, er.agent_version, field_key;


-- Manual review progress
CREATE VIEW v_manual_review_progress AS
SELECT
    ms.id AS session_id,
    ms.name AS session_name,
    a.name AS agent_name,
    ms.total_items,
    ms.reviewed_count,
    CASE WHEN ms.total_items > 0
         THEN ROUND((ms.reviewed_count::NUMERIC / ms.total_items) * 100, 1)
         ELSE 0
    END AS progress_pct,
    COUNT(*) FILTER (WHERE mi.verdict = 'pass') AS pass_count,
    COUNT(*) FILTER (WHERE mi.verdict = 'fail') AS fail_count,
    COUNT(*) FILTER (WHERE mi.verdict = 'partial') AS partial_count,
    COUNT(*) FILTER (WHERE mi.severity = 'critical') AS critical_failures,
    AVG(mi.review_duration_ms) FILTER (WHERE mi.is_reviewed) AS avg_review_time_ms
FROM manual_eval_sessions ms
JOIN agents a ON a.id = ms.agent_id
LEFT JOIN manual_eval_items mi ON mi.session_id = ms.id
GROUP BY ms.id, ms.name, a.name, ms.total_items, ms.reviewed_count;


-- Regression detection: compare last 2 runs per agent
CREATE VIEW v_regression_detection AS
WITH ranked_runs AS (
    SELECT
        agent_id,
        id AS run_id,
        agent_version,
        created_at,
        passed,
        total_items,
        CASE WHEN total_items > 0
             THEN ROUND((passed::NUMERIC / total_items) * 100, 2)
             ELSE 0
        END AS pass_rate,
        avg_latency_ms,
        ROW_NUMBER() OVER (PARTITION BY agent_id ORDER BY created_at DESC) AS rn
    FROM eval_runs
    WHERE status = 'completed'
)
SELECT
    curr.agent_id,
    curr.run_id AS current_run,
    curr.agent_version AS current_version,
    curr.pass_rate AS current_pass_rate,
    prev.run_id AS previous_run,
    prev.agent_version AS previous_version,
    prev.pass_rate AS previous_pass_rate,
    (curr.pass_rate - prev.pass_rate) AS pass_rate_delta,
    CASE WHEN (curr.pass_rate - prev.pass_rate) < -5 THEN TRUE ELSE FALSE END AS is_regression
FROM ranked_runs curr
JOIN ranked_runs prev ON curr.agent_id = prev.agent_id AND prev.rn = 2
WHERE curr.rn = 1;
```

### Analytical Query Examples

```sql
-- Latency percentiles for a specific run (PostgreSQL-native)
SELECT
    percentile_cont(0.50) WITHIN GROUP (ORDER BY latency_ms) AS p50,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95,
    percentile_cont(0.99) WITHIN GROUP (ORDER BY latency_ms) AS p99,
    AVG(latency_ms) AS avg_latency
FROM eval_run_results
WHERE run_id = '<run-uuid>';


-- Find all agents tagged with "vision" AND "production"
SELECT * FROM agents
WHERE tags @> ARRAY['vision', 'production'];


-- Search datasets by fuzzy name match
SELECT * FROM eval_datasets
WHERE name % 'wine lable'                -- pg_trgm similarity (handles typos)
ORDER BY similarity(name, 'wine lable') DESC
LIMIT 10;


-- RAG retrieval quality per run
SELECT
    rr.run_id,
    AVG(rd.retrieval_precision) AS avg_precision,
    AVG(rd.retrieval_recall) AS avg_recall,
    AVG(rd.faithfulness_score) AS avg_faithfulness,
    AVG(rd.answer_relevance_score) AS avg_answer_relevance
FROM eval_run_results rr
JOIN rag_eval_result_details rd ON rd.eval_result_id = rr.id
WHERE rr.run_id = '<run-uuid>'
GROUP BY rr.run_id;


-- Error category breakdown for a run
SELECT
    COALESCE(
        CASE
            WHEN error ILIKE '%timeout%' THEN 'Timeout'
            WHEN error ILIKE '%auth%' OR status_code = 401 THEN 'Auth Error'
            WHEN status_code >= 500 THEN 'Server Error'
            WHEN status_code >= 400 THEN 'Client Error'
            WHEN agent_output IS NULL THEN 'No Response'
            ELSE 'Wrong Answer'
        END,
        'Unknown'
    ) AS error_category,
    COUNT(*) AS count,
    ROUND(COUNT(*)::NUMERIC / SUM(COUNT(*)) OVER () * 100, 1) AS pct
FROM eval_run_results
WHERE run_id = '<run-uuid>' AND NOT passed
GROUP BY error_category
ORDER BY count DESC;


-- Cost per correct answer (efficiency metric)
SELECT
    a.name,
    er.agent_version,
    er.total_cost_usd,
    er.passed,
    CASE WHEN er.passed > 0
         THEN ROUND((er.total_cost_usd / er.passed)::NUMERIC, 4)
         ELSE NULL
    END AS cost_per_correct
FROM eval_runs er
JOIN agents a ON a.id = er.agent_id
WHERE er.status = 'completed' AND er.total_cost_usd IS NOT NULL
ORDER BY a.name, er.created_at DESC;
```

### Migration & Index Notes

```sql
-- Trigger for auto-updating updated_at
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all mutable tables
CREATE TRIGGER set_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON eval_datasets FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON eval_dataset_items FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON rag_eval_datasets FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- Trigger to maintain item_count on eval_datasets
CREATE OR REPLACE FUNCTION update_dataset_item_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE eval_datasets SET item_count = item_count + 1 WHERE id = NEW.dataset_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE eval_datasets SET item_count = item_count - 1 WHERE id = OLD.dataset_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_dataset_item_count
AFTER INSERT OR DELETE ON eval_dataset_items
FOR EACH ROW EXECUTE FUNCTION update_dataset_item_count();

-- Same for rag_eval_datasets
CREATE OR REPLACE FUNCTION update_rag_dataset_item_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE rag_eval_datasets SET item_count = item_count + 1 WHERE id = NEW.dataset_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE rag_eval_datasets SET item_count = item_count - 1 WHERE id = OLD.dataset_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_rag_item_count
AFTER INSERT OR DELETE ON rag_eval_items
FOR EACH ROW EXECUTE FUNCTION update_rag_dataset_item_count();
```

### ERD Summary

```
users
  │
  ├──creates──▶ agents (1) ─────────── (N) agent_versions
  │                │
  │                ├── (N) eval_runs ──── (N) eval_run_results
  │                │       │                     │
  │                │       │                     └── (0..1) rag_eval_result_details
  │                │       │
  │                │       └── (0..1) manual_eval_sessions ── (N) manual_eval_items
  │                │
  │                └──────────────────── audit_log
  │
  ├──creates──▶ eval_datasets (1) ──── (N) eval_dataset_items
  │                │
  │                └── (N) dataset_versions
  │
  └──creates──▶ rag_eval_datasets (1) ── (N) rag_eval_items
```

---

## Key User Journeys (Phase 1)

**Journey 1: Register a New Agent**
1. Navigate to Agent Registry → Click "Register Agent"
2. Fill in agent details: name, type (Vision), endpoint URL, Gemini as provider
3. Define input schema (image_url) and output schema (wine_name, vintage, region, confidence)
4. Set status to Active → Save

**Journey 2: Create and Run an Automated Evaluation**
1. Navigate to Datasets → Create new dataset "Wine Labels — Field Photos v1"
2. Bulk import 200 test cases from JSON (image URLs + expected wine details)
3. Navigate to Evaluations → New Eval Run
4. Select agent "Wine Label Recognizer" + dataset "Wine Labels v1"
5. Configure matcher: Field-Level Match on wine_name (fuzzy, 0.85 threshold) + vintage (exact)
6. Run evaluation → Watch progress in real-time
7. View results: 78% pass rate, vintage field is the weakest at 65% accuracy

**Journey 3: Manual Verification in Playground**
1. From eval run results, click "Send Failures to Manual Review"
2. Opens Playground with 44 failed items queued
3. Reviewer sees: field photo (left) | Gemini's response (center) | eval form (right)
4. For each item: verify Gemini's output, mark fields correct/incorrect, add notes
5. Use keyboard shortcuts (P/F/→) for rapid review
6. On completion, manual eval results merge into analytics

**Journey 4: Analyze Results & Detect Regression**
1. Navigate to Analytics for "Wine Label Recognizer"
2. See accuracy trend across versions: v1.0 (72%) → v1.1 (78%) → v1.2 (75% ← regression!)
3. Drill into v1.2 regression: field-level heatmap shows "region" accuracy dropped 12%
4. Click into failed "region" items → discover a prompt change broke European wine regions
5. Export regression report for team review

**Journey 5: RAG Pipeline Evaluation**
1. Register RAG agent (e.g., "Product Support Bot")
2. Create RAG dataset with queries, expected answers, and relevant chunk IDs
3. Run RAG evaluation → system captures retrieved chunks + generated answers
4. Review retrieval precision/recall, faithfulness scores, chunk attribution
5. Identify: retriever misses 30% of relevant chunks for multi-document questions → tune top-k

---

## Design System Notes

- **Aesthetic**: Industrial-utilitarian meets data-dense dashboards. Think Datadog/Grafana clarity with a dark-mode-first approach
- **Layout**: Sidebar navigation (Agents | Datasets | Evaluations | Analytics | Settings), main content area with breadcrumbs
- **Typography**: Monospace for JSON/code, proportional sans-serif for UI text
- **Color coding**: Green = Pass, Red = Fail, Amber = Partial, Blue = In Progress, Gray = Not Evaluated
- **Responsiveness**: Desktop-first (this is an internal ops tool), but table views should be usable on tablets

---

## API Design Skeleton (Phase 1)

```
# Agent Registry
POST   /api/agents                    # Register new agent
GET    /api/agents                    # List agents (with filters)
GET    /api/agents/{id}               # Get agent details
PUT    /api/agents/{id}               # Update agent
DELETE /api/agents/{id}               # Archive agent
GET    /api/agents/{id}/versions      # Version history

# Eval Datasets
POST   /api/datasets                  # Create dataset
GET    /api/datasets                  # List datasets
GET    /api/datasets/{id}             # Get dataset with items
PUT    /api/datasets/{id}             # Update dataset metadata
DELETE /api/datasets/{id}             # Delete dataset
POST   /api/datasets/{id}/items       # Add items (single or bulk)
PUT    /api/datasets/{id}/items/{itemId}  # Update item
DELETE /api/datasets/{id}/items/{itemId}  # Delete item
POST   /api/datasets/{id}/import      # Bulk import (CSV/JSON/JSONL)
GET    /api/datasets/{id}/export      # Bulk export
POST   /api/datasets/{id}/snapshot    # Create version snapshot
GET    /api/datasets/{id}/versions    # List versions

# RAG Datasets (extends base dataset)
POST   /api/rag-datasets              # Create RAG dataset
GET    /api/rag-datasets              # List RAG datasets
POST   /api/rag-datasets/{id}/sync    # Sync from knowledge base

# Evaluation Runs
POST   /api/eval-runs                 # Start new eval run
GET    /api/eval-runs                 # List eval runs
GET    /api/eval-runs/{id}            # Get run with summary
GET    /api/eval-runs/{id}/results    # Get paginated results
POST   /api/eval-runs/{id}/cancel     # Cancel running eval

# Manual Evaluation
POST   /api/manual-eval/sessions      # Create manual eval session
GET    /api/manual-eval/sessions/{id} # Get session with items
POST   /api/manual-eval/sessions/{id}/items/{itemId}/review  # Submit review
GET    /api/manual-eval/queue/{sessionId}  # Get next unreviewed item

# Analytics
GET    /api/analytics/agents/{id}/accuracy-trend   # Accuracy over time
GET    /api/analytics/agents/{id}/field-accuracy    # Per-field breakdown
GET    /api/analytics/agents/{id}/latency           # Latency distribution
GET    /api/analytics/agents/{id}/regressions       # Regression detection
GET    /api/analytics/compare                        # Compare agents/versions
```

---

## Non-Functional Requirements

- **Eval runs must be async** — queue-based execution, WebSocket/SSE for progress updates
- **Result storage** — Handle large eval runs (10k+ items) with paginated access
- **Concurrent reviews** — Multiple reviewers can work on the same manual eval session without conflicts (optimistic locking)
- **Audit trail** — Log who changed what in agent configs, datasets, and eval results
- **RBAC** — Admin (full access), Evaluator (run evals + review), Viewer (read-only analytics)
