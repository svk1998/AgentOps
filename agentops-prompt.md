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
| **Database** | MySQL (primary store) + Redis (caching, job queues) |
| **Task Queue** | Celery or Kafka for async eval run execution |
| **Auth** | JWT-based with role-based access control |
| **Containerization** | Docker Compose (dev), Kubernetes (prod) |

---

## Data Model Summary (Phase 1 ERD)

```
Agent (1) ─────── (N) EvalRun
  │                      │
  │                      ├── (N) EvalRunResult
  │                      │
  │                      └── (0..1) ManualEvalSession
  │                                    │
  │                                    └── (N) ManualEvalItem
  │
  ├── (N) AgentVersion
  │
EvalDataset (1) ── (N) EvalDatasetItem
  │
  ├── (N) DatasetVersion (snapshots)
  │
RAGEvalDataset (1) ── (N) RAGEvalItem
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
