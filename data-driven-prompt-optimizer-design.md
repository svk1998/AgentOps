# Data-Driven Prompt Optimizer — Design Document

## 1. Problem Statement

Whether you're using a self-hosted inference server (vLLM, SGLang, TGI, Ollama), a cloud API (OpenAI, Anthropic, Google), or a local `transformers` pipeline — system instructions and prompt templates are written by hand and iterated manually. This is slow, inconsistent, and doesn't scale across tasks or models. We need an automated, **backend-agnostic** pipeline that takes a system instruction, a prompt template, and a dataset of sample inputs — then iteratively rewrites the system instruction (and optionally selects few-shot demonstrations) to maximize a measurable eval metric against *any* target model.

The optimizer should work identically regardless of where the model runs. The only thing that changes is a provider config block.

---

## 2. Concept (Inspired by Vertex AI Data-Driven Optimizer)

Google's Vertex AI prompt optimizer works as follows:

1. You provide a **system instruction**, a **prompt template** (with `{variable}` placeholders), and a **sample dataset** (JSONL/CSV rows that fill those variables).
2. You choose an **optimization mode**: rewrite the system instruction (`instruction`), select few-shot examples (`demonstration`), or both (`instruction_and_demo`).
3. You choose **evaluation metrics** (model-based like coherence/groundedness, computation-based like ROUGE/BLEU/exact_match, or custom metrics).
4. The optimizer runs a loop: generate candidate instructions → run all sample prompts against the target model → evaluate outputs → use the eval signal to propose better instructions → repeat for N steps.
5. Output: the best-scoring system instruction (and optional few-shot demo set) along with the eval trajectory.

We replicate this loop with a pluggable provider layer — the optimizer doesn't know or care whether the model is served by vLLM, Ollama, Anthropic's API, or a raw HuggingFace pipeline. Each provider just implements a `generate()` interface.

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Prompt Optimizer CLI / API                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────────┐    ┌────────────────────────┐     │
│  │  Config   │───▶│  Optimizer   │───▶│  Results Store         │     │
│  │  Loader   │    │  Loop        │    │  (best instructions,   │     │
│  └──────────┘    │              │    │   eval trajectory)     │     │
│                  │  For each    │    └────────────────────────┘     │
│                  │  step:       │                                   │
│                  │   1. Rewrite │    ┌────────────────────────┐     │
│                  │   2. Render  │───▶│  LLM Provider          │     │
│                  │   3. Infer   │◀───│  (target_model)        │     │
│                  │   4. Evaluate│    │                        │     │
│                  │   5. Score   │    │  Implementations:      │     │
│                  │   6. Select  │    │  ├─ OpenAICompatible   │     │
│                  │      best    │    │  │  (vLLM/SGLang/TGI)  │     │
│                  └──────┬───────┘    │  ├─ Anthropic          │     │
│                         │           │  ├─ Ollama             │     │
│                         │           │  ├─ HuggingFacePipeline│     │
│                         │           │  └─ Custom             │     │
│                         │           └────────────────────────┘     │
│                         │                                          │
│                  ┌──────▼───────┐    ┌────────────────────────┐     │
│                  │  Evaluator   │───▶│  LLM Provider          │     │
│                  │              │    │  (judge_model)         │     │
│                  │  - Judge LLM │    │  (can be any provider) │     │
│                  │  - Compute   │    └────────────────────────┘     │
│                  │  - Custom Fn │                                   │
│                  └──────────────┘    ┌────────────────────────┐     │
│                                     │  LLM Provider          │     │
│                  ┌──────────────┐───▶│  (rewriter_model)      │     │
│                  │  Rewriter    │◀───│  (can be any provider) │     │
│                  │  (meta-LLM)  │    └────────────────────────┘     │
│                  └──────────────┘                                   │
└─────────────────────────────────────────────────────────────────────┘
```

**The three model roles (target, rewriter, judge) can each point at different providers.** For example: target on local vLLM, rewriter on Anthropic Claude, judge on Ollama. Or all three on the same vLLM instance. The optimizer doesn't care.

### Key Components

| Component | Responsibility |
|---|---|
| **Config Loader** | Reads YAML/JSON config: system instruction, prompt template, dataset path, optimization mode, eval metrics, provider configs, num_steps, QPS limits |
| **Optimizer Loop** | Orchestrates the iterative rewrite-infer-evaluate cycle |
| **Prompt Renderer** | Substitutes `{variables}` in the template with dataset rows, prepends system instruction |
| **LLM Provider** | Abstract interface for `generate(messages) → response`. Concrete implementations for OpenAI-compat (vLLM/SGLang/TGI), Anthropic, Ollama, HuggingFace local, etc. Handles concurrency/retries. |
| **Evaluator** | Scores each (prompt, response) pair using the configured metric(s) |
| **Rewriter** | Uses a meta-LLM call (via any provider) to propose improved system instructions based on eval feedback |
| **Demo Selector** | (Optional) Selects the best subset of dataset rows to use as few-shot examples |
| **Results Store** | Persists eval trajectory, best instruction per step, final output |

---

## 4. Optimization Modes

### 4.1 `instruction` — System Instruction Rewriting

The core loop:

```
best_instruction = initial_system_instruction
best_score = evaluate(best_instruction, dataset)

for step in range(num_steps):
    # Ask the rewriter model to propose a better instruction
    candidate = rewriter.rewrite(
        current_instruction=best_instruction,
        current_score=best_score,
        sample_failures=get_worst_examples(dataset, best_instruction, k=5),
        task_description=infer_task_from_template(prompt_template),
    )

    # Evaluate the candidate
    candidate_score = evaluate(candidate, dataset)

    if candidate_score > best_score:
        best_instruction = candidate
        best_score = candidate_score

    log_step(step, candidate, candidate_score)
```

**Rewriter meta-prompt** (the prompt sent to the rewriter model):

```
You are a prompt engineering expert. Your job is to improve an LLM system
instruction so that it produces better outputs on a specific task.

## Current System Instruction
{current_instruction}

## Current Score
{current_score} (metric: {metric_name})

## Examples Where the Model Failed
{sample_failures_formatted}

## Task Context
The prompt template is: {prompt_template}
The evaluation metric is: {metric_name} (higher is better)

## Instructions
Analyze why the current system instruction leads to poor outputs on the
failing examples. Then write an improved system instruction that addresses
these failure modes. Only output the new system instruction, nothing else.
```

### 4.2 `demonstration` — Few-Shot Example Selection

Instead of rewriting the instruction, this mode searches for the best subset of K examples from the dataset to prepend as few-shot demonstrations.

Strategy: greedy search or combinatorial sampling over subsets → evaluate each subset → pick the highest-scoring one.

```
best_demo_set = None
best_score = -inf

for trial in range(num_demo_trials):
    demo_set = sample_k_examples(dataset, k=demo_set_size, exclude=eval_set)
    score = evaluate_with_demos(system_instruction, demo_set, eval_set)

    if score > best_score:
        best_demo_set = demo_set
        best_score = score
```

### 4.3 `instruction_and_demo` — Combined

Run instruction optimization first, then demo selection using the optimized instruction (or interleave them).

---

## 5. Evaluation System

### 5.1 Computation-Based Metrics (No Extra Model Needed)

| Metric | Implementation |
|---|---|
| `exact_match` | `prediction.strip() == reference.strip()` |
| `rouge_1`, `rouge_2`, `rouge_l` | `rouge-score` Python library |
| `bleu` | `sacrebleu` or `nltk.translate.bleu_score` |
| `json_valid` | Attempt `json.loads(prediction)`, return 1/0 |
| `regex_match` | User-supplied regex pattern |

These require a **ground truth / reference** column in the dataset.

### 5.2 Model-Based (Judge) Metrics

Use any LLM provider as a judge (same model, different model, different provider entirely). Send a scoring prompt:

```
You are evaluating the quality of an AI assistant's response.

## Task
{task_description}

## User Prompt
{rendered_prompt}

## AI Response
{model_response}

## Evaluation Criteria: {metric_name}
{metric_rubric}

Rate the response on a scale of 1-5. Respond with ONLY a JSON object:
{"score": <int>, "explanation": "<brief reasoning>"}
```

Supported judge metrics (with built-in rubrics):

| Metric | What It Measures |
|---|---|
| `coherence` | Logical flow and readability |
| `groundedness` | Only uses information from the provided context |
| `relevance` | Addresses the user's actual question |
| `fluency` | Grammar, naturalness of language |
| `safety` | No harmful or inappropriate content |
| `instruction_following` | Adheres to the system instruction constraints |
| `completeness` | Covers all aspects of the question |

### 5.3 Custom Metrics

User provides a Python function with signature:

```python
def my_metric(response: str, reference: str | None, input_data: dict) -> float:
    """Return a score where higher is better."""
    ...
```

Registered via config:

```yaml
eval_metrics:
  - type: custom
    name: my_domain_metric
    function: path.to.module:my_metric
```

### 5.4 Multi-Metric Aggregation

When using multiple metrics, aggregate via weighted sum or weighted average:

```yaml
eval_metrics:
  - type: rouge_l
    weight: 0.4
  - type: judge:coherence
    weight: 0.3
  - type: judge:groundedness
    weight: 0.3
aggregation: weighted_average  # or weighted_sum
```

---

## 6. Configuration Schema

```yaml
# ── Required ────────────────────────────────────────
project_name: "test-script-gen-optimizer"

system_instruction: |
  You are an expert test automation engineer...

prompt_template: |
  API Context:
  {api_context}

  Requirement:
  {requirement}

  Write the test script.

dataset_path: "./data/samples.jsonl"       # or .csv
output_dir: "./results/run_001/"

target_model:
  provider: "openai_compatible"            # openai_compatible | anthropic | ollama | huggingface | custom
  base_url: "http://localhost:8000/v1"     # vLLM / SGLang / TGI / LiteLLM / any OpenAI-compat server
  model: "Qwen/Qwen2.5-Coder-32B"
  api_key: null                            # null for local, or env var name like "$ANTHROPIC_API_KEY"
  temperature: 0.3
  max_tokens: 2048

optimization_mode: "instruction"           # instruction | demonstration | instruction_and_demo

eval_metrics:
  - type: rouge_l
    weight: 1.0

# ── Optional ────────────────────────────────────────

# Rewriter and judge can use completely different providers.
# Defaults to target_model config if unset.
rewriter_model:
  provider: "anthropic"                    # example: use Claude as the meta-rewriter
  model: "claude-sonnet-4-20250514"
  api_key: "$ANTHROPIC_API_KEY"
  temperature: 0.7

judge_model:                               # required only for model-based metrics
  provider: "ollama"                       # example: use a local Ollama model as judge
  base_url: "http://localhost:11434"
  model: "llama3.1:70b"
  temperature: 0.0

# --- OR all three on the same local server ---
# rewriter_model:
#   provider: "openai_compatible"
#   base_url: "http://localhost:8000/v1"
#   model: "Qwen/Qwen2.5-Coder-32B"
#   temperature: 0.7
#
# judge_model:
#   provider: "openai_compatible"
#   base_url: "http://localhost:8000/v1"
#   model: "Qwen/Qwen2.5-Coder-32B"
#   temperature: 0.0

num_steps: 10                              # instruction optimization iterations (10-20)
num_demo_trials: 15                        # demonstration search trials
demo_set_size: 3                           # few-shot examples per prompt (2-6)

target_model_qps: 5.0                      # concurrency limit
eval_qps: 5.0

reference_column: "expected_output"        # column name for ground truth (if any)
ground_truth_from_model: null              # or a provider config block to auto-generate references

response_format: "text/plain"              # or "application/json"
language: "en"

data_limit: 50                             # max dataset rows to use per eval pass
```

---

## 7. LLM Provider Abstraction

This is the core design that makes the optimizer backend-agnostic. Every component that talks to an LLM goes through the same interface.

### 7.1 Abstract Interface

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Message:
    role: str          # "system" | "user" | "assistant"
    content: str

@dataclass
class GenerateResponse:
    text: str
    usage: dict | None = None    # {"prompt_tokens": ..., "completion_tokens": ...}
    raw: dict | None = None      # full API response for debugging

class LLMProvider(ABC):
    """All LLM backends implement this single interface."""

    @abstractmethod
    async def generate(
        self,
        messages: list[Message],
        temperature: float = 0.3,
        max_tokens: int = 2048,
        response_format: str | None = None,   # "json_object" or None
    ) -> GenerateResponse:
        ...

    @abstractmethod
    async def healthcheck(self) -> bool:
        """Return True if the backend is reachable and ready."""
        ...
```

### 7.2 Concrete Implementations

| Provider | When to Use | Key Details |
|---|---|---|
| `OpenAICompatibleProvider` | vLLM, SGLang, TGI, LiteLLM, Azure OpenAI, OpenAI itself | Uses `httpx` → `POST /v1/chat/completions`. Most self-hosted servers expose this. |
| `AnthropicProvider` | Claude models via Anthropic API | Uses `httpx` → `POST /v1/messages`. Maps `system` message to Anthropic's `system` param. |
| `OllamaProvider` | Local Ollama server | Uses `httpx` → `POST /api/chat`. Slightly different request/response shape. |
| `HuggingFaceProvider` | Direct `transformers` pipeline, no server | Loads model in-process. Useful for small models or eval-only scenarios. |
| `CustomProvider` | User-supplied adapter | User provides a Python callable or a module path. For niche servers, internal APIs, etc. |

### 7.3 Provider Factory

```python
def create_provider(config: dict) -> LLMProvider:
    """Instantiate the right provider from a config block."""
    provider_type = config.get("provider", "openai_compatible")

    match provider_type:
        case "openai_compatible":
            return OpenAICompatibleProvider(
                base_url=config["base_url"],
                model=config["model"],
                api_key=resolve_env(config.get("api_key")),
            )
        case "anthropic":
            return AnthropicProvider(
                model=config["model"],
                api_key=resolve_env(config.get("api_key", "$ANTHROPIC_API_KEY")),
            )
        case "ollama":
            return OllamaProvider(
                base_url=config.get("base_url", "http://localhost:11434"),
                model=config["model"],
            )
        case "huggingface":
            return HuggingFaceProvider(
                model=config["model"],
                device=config.get("device", "auto"),
            )
        case "custom":
            return load_custom_provider(config["module_path"])
        case _:
            raise ValueError(f"Unknown provider: {provider_type}")
```

### 7.4 Mix-and-Match Examples

The power of the abstraction is that all three model roles are independent:

```yaml
# Scenario A: Fully air-gapped, everything on one vLLM server
target_model:    { provider: openai_compatible, base_url: "http://gpu-box:8000/v1", model: "Qwen2.5-72B" }
rewriter_model:  null   # falls back to target_model
judge_model:     null   # falls back to target_model

# Scenario B: Local target, Claude as rewriter (smarter meta-reasoning)
target_model:    { provider: openai_compatible, base_url: "http://gpu-box:8000/v1", model: "Qwen2.5-7B" }
rewriter_model:  { provider: anthropic, model: "claude-sonnet-4-20250514" }
judge_model:     { provider: openai_compatible, base_url: "http://gpu-box:8000/v1", model: "Qwen2.5-72B" }

# Scenario C: Ollama for everything (laptop dev mode)
target_model:    { provider: ollama, model: "llama3.1:8b" }
rewriter_model:  { provider: ollama, model: "llama3.1:8b" }
judge_model:     { provider: ollama, model: "llama3.1:8b" }

# Scenario D: Cloud APIs, no local infra
target_model:    { provider: openai_compatible, base_url: "https://api.openai.com/v1", model: "gpt-4o", api_key: "$OPENAI_API_KEY" }
rewriter_model:  { provider: anthropic, model: "claude-sonnet-4-20250514", api_key: "$ANTHROPIC_API_KEY" }
judge_model:     { provider: openai_compatible, base_url: "https://api.openai.com/v1", model: "gpt-4o-mini", api_key: "$OPENAI_API_KEY" }
```

---

## 8. Dataset Format

### JSONL (Recommended)

Each line is a JSON object whose keys match `{variables}` in the prompt template:

```jsonl
{"api_context": "class Camera:\n  def capture()...", "requirement": "Test auto-focus in low light", "expected_output": "def test_autofocus_low_light():..."}
{"api_context": "class Display:\n  def set_brightness()...", "requirement": "Test brightness range 0-100", "expected_output": "def test_brightness_range():..."}
```

### CSV

Same idea, column headers match template variables.

---

## 9. Output Format

```
results/run_001/
├── config.yaml                     # Frozen copy of input config
├── trajectory.jsonl                # Per-step log
│   # Each line: {"step": 0, "instruction": "...", "score": 0.72, "metric_breakdown": {...}}
├── best_instruction.txt            # Final optimized system instruction
├── best_demos.jsonl                # (If demo mode) Selected few-shot examples
├── eval_details/
│   ├── step_00.jsonl               # Per-sample scores for step 0
│   ├── step_01.jsonl
│   └── ...
└── summary.json                    # Final summary
    # {"best_score": 0.89, "baseline_score": 0.72, "improvement": "+23.6%", "best_step": 7, "total_steps": 10}
```

---

## 10. Implementation Plan

### Phase 1 — Core Loop (Week 1)

- [ ] Config loader (YAML → Pydantic models)
- [ ] **LLM Provider abstraction** (`LLMProvider` ABC + `OpenAICompatibleProvider` + `create_provider` factory)
- [ ] Prompt renderer (Jinja2-style `{var}` substitution)
- [ ] LLM caller (async `httpx` client via provider interface, retry + rate-limiting)
- [ ] Computation-based evaluator (exact_match, rouge, bleu)
- [ ] Instruction rewriter (meta-prompt via provider)
- [ ] Optimizer loop (instruction mode only)
- [ ] CLI entry point: `python -m prompt_optimizer --config config.yaml`
- [ ] Output: trajectory JSONL + best_instruction.txt

### Phase 2 — Providers + Evaluation Depth (Week 2)

- [ ] Additional providers: `AnthropicProvider`, `OllamaProvider`, `HuggingFaceProvider`
- [ ] Model-based (judge) evaluator with configurable rubrics
- [ ] Custom metric plugin system (`importlib` dynamic load)
- [ ] Multi-metric aggregation (weighted_sum / weighted_average)
- [ ] Ground-truth auto-generation from a source model (via any provider)

### Phase 3 — Demo Selection + Advanced (Week 3)

- [ ] Demonstration selector (greedy + random sampling)
- [ ] `instruction_and_demo` combined mode
- [ ] Parallel eval with `asyncio.Semaphore` for QPS control
- [ ] Progress dashboard (rich/tqdm live table showing step, score, delta)

### Phase 4 — Web UI + Integration (Week 4)

- [ ] FastAPI wrapper around the optimizer
- [ ] Vue/React dashboard: configure a run, monitor live, browse results
- [ ] Integration with the existing test-script-generation pipeline (use optimizer to tune the few-shot prompt builder's system instruction)
- [ ] PostgreSQL run history table

---

## 11. Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Language | Python 3.11+ | Ecosystem, async, existing infra |
| Config | Pydantic v2 + YAML | Typed validation, easy to read |
| HTTP Client | `httpx` (async) | Non-blocking calls to any HTTP-based LLM API |
| Provider SDKs | `anthropic` (optional), `openai` (optional), `ollama` (optional) | Only install what you need — core only requires `httpx` |
| Eval Libs | `rouge-score`, `sacrebleu`, `nltk` | Standard NLP metrics |
| Templating | Python `str.format_map` or Jinja2 | Variable substitution |
| CLI | `typer` or `argparse` | CLI-first approach |
| Results | JSONL files + optional PostgreSQL | Lightweight, queryable |
| Web UI (Phase 4) | FastAPI + Vue 3 | Matches existing stack |

---

## 12. Key Design Decisions

**Why not just use DSPy / OPRO / TextGrad?**  
Those frameworks are excellent but have opinions about backends, carry heavy dependencies, or assume specific API shapes. Our optimizer is intentionally minimal — a thin provider abstraction over any LLM backend. We adopt ideas from OPRO (rewrite via LLM), DSPy (bootstrapped demos), and TextGrad (gradient-like feedback) without importing those libraries. This also means it works in air-gapped environments out of the box, and equally well against cloud APIs.

**Why a provider abstraction instead of just using LiteLLM?**  
LiteLLM is a fine option and you could use it as the `openai_compatible` provider's backend. But having our own thin abstraction means: (a) no external dependency for the simplest case, (b) full control over retry/timeout/rate-limiting behavior per-role, (c) we can add `HuggingFaceProvider` for in-process inference with no server at all, and (d) the interface stays stable even if LiteLLM's API changes. That said, nothing stops you from implementing a `LiteLLMProvider` that delegates to it.

**Three independent model roles (target / rewriter / judge)**  
This is a deliberate design choice. The target model is whatever you're optimizing prompts for — it could be a tiny 7B model. The rewriter benefits from strong meta-reasoning ability (a bigger model, or Claude). The judge needs to be calibrated for the eval rubric. Tying all three to one backend would be artificially limiting.

**Rewriter model = Target model by default?**  
Yes — simplest deployment, one server to manage. But the config makes it trivial to point the rewriter at a smarter model. The rewriter needs to be good at meta-reasoning about prompts, not necessarily good at the task itself.

**Eval cost control**  
Each step runs the full dataset through the target model + evaluator. With 50 samples × 10 steps = 500 inferences (+ 500 judge calls if model-based). At typical local throughput of ~20 req/s, that's ~50 seconds per run. For cloud APIs at higher latency, it might be 5-10 minutes. `data_limit` caps this if the dataset is large.

---

## 13. Rewriter Prompt Design (Critical)

The quality of the rewriter meta-prompt is the single biggest lever. Key principles:

1. **Show failures**: Include 3-5 worst-scoring (prompt, response, score, explanation) pairs so the rewriter understands what's going wrong.
2. **Show successes**: Include 1-2 best-scoring pairs as positive signal.
3. **Be specific about the metric**: Tell the rewriter exactly what "coherence" or "rouge_l" means.
4. **Constrain the output**: "Output ONLY the new system instruction. Do not include any explanation."
5. **Iterative memory**: Pass the previous instruction + score so the rewriter doesn't regress. Optionally pass the last 2-3 attempts to avoid cycles.

---

## 14. Example Usage

```bash
# Run optimization
python -m prompt_optimizer --config ./configs/test_script_gen.yaml

# Output
# [Step 0/10] Baseline score: 0.72 (rouge_l)
# [Step 1/10] Candidate score: 0.74 (+2.8%) ✓ New best
# [Step 2/10] Candidate score: 0.73 (-1.4%) ✗ Keeping previous
# ...
# [Step 9/10] Candidate score: 0.89 (+1.1%) ✓ New best
#
# ✅ Optimization complete
# Best score: 0.89 (baseline: 0.72, improvement: +23.6%)
# Saved to: ./results/run_001/best_instruction.txt
```

---

## 15. Extensibility Hooks

- **Pre/post step callbacks**: For logging to external systems, Slack notifications, etc.
- **Custom rewriter strategy**: Swap the meta-prompt or use a different rewriting algorithm (e.g., evolutionary mutation of instructions).
- **Eval caching**: Hash (instruction + prompt) → skip re-evaluation if seen before.
- **Warm start**: Resume from a previous run's best instruction instead of the initial one.
- **A/B comparison mode**: Run two configs side-by-side and compare trajectories.
