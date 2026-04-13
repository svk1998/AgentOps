<template>
  <div class="optimizer-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h2>Prompt Optimizer</h2>
        <p class="page-sub">Iteratively refines your prompt until the output matches the goal.</p>
      </div>
      <RouterLink to="/prompt-optimizer/history" class="btn-secondary">View History</RouterLink>
    </div>

    <!-- Two-panel layout -->
    <div class="panels">
      <!-- ── Left: Configuration ── -->
      <div class="panel config-panel">
        <div class="panel-title">Configuration</div>

        <div class="field">
          <label class="field-label">Base Prompt <span class="required">*</span></label>
          <textarea
            v-model="form.basePrompt"
            class="textarea"
            placeholder="Enter the initial prompt to optimize..."
            rows="6"
            :disabled="isRunning"
          />
        </div>

        <div class="field">
          <label class="field-label">Required Output / Goal <span class="required">*</span></label>
          <textarea
            v-model="form.requiredOutput"
            class="textarea"
            placeholder="Describe what the ideal output should look like..."
            rows="6"
            :disabled="isRunning"
          />
        </div>

        <div class="field-row">
          <div class="field">
            <label class="field-label">Model</label>
            <select v-model="form.model" class="select" :disabled="isRunning || modelsLoading">
              <option v-if="modelsLoading" disabled value="">Loading models…</option>
              <template v-for="(group, provider) in groupedModels" :key="provider">
                <optgroup :label="providerLabel(provider)">
                  <option v-for="m in group" :key="m.id" :value="m.id">{{ m.name }}</option>
                </optgroup>
              </template>
            </select>
          </div>

          <div class="field">
            <label class="field-label">Max Iterations</label>
            <input
              v-model.number="form.maxIterations"
              type="number"
              class="input"
              min="1"
              max="20"
              :disabled="isRunning"
            />
          </div>
        </div>

        <div class="field">
          <label class="field-label">Score Threshold (%)</label>
          <div class="threshold-row">
            <input
              v-model.number="form.scoreThreshold"
              type="range"
              min="50"
              max="100"
              step="5"
              class="range-input"
              :disabled="isRunning"
            />
            <span class="threshold-val">{{ form.scoreThreshold }}%</span>
          </div>
          <p class="field-hint">Stop when output matches goal at this percentage.</p>
        </div>

        <!-- Actions -->
        <div class="panel-actions">
          <button
            v-if="!isRunning"
            class="btn-primary"
            :disabled="!canSubmit || submitLoading"
            @click="handleStart"
          >
            <span v-if="submitLoading">Starting...</span>
            <span v-else>Optimize Prompt</span>
          </button>
          <button
            v-else
            class="btn-danger"
            :disabled="stopLoading"
            @click="handleStop"
          >
            <span v-if="stopLoading">Stopping...</span>
            <span v-else>Stop</span>
          </button>
          <button class="btn-ghost" @click="handleReset" :disabled="isRunning">Reset</button>
        </div>
      </div>

      <!-- ── Right: Results ── -->
      <div class="panel results-panel">
        <div class="panel-title-row">
          <div class="panel-title">Results</div>
          <div v-if="run" class="run-meta">
            <span class="run-status" :class="run.status">{{ run.status }}</span>
            <span class="run-iter">{{ run.iterations.length }} / {{ run.maxIterations }} iterations</span>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="!run" class="empty-state">
          <div class="empty-icon">🧠</div>
          <p>Configure and run the optimizer to see iteration results here.</p>
        </div>

        <!-- Running indicator -->
        <div v-else-if="isRunning && run.iterations.length === 0" class="empty-state">
          <div class="spinner-lg" />
          <p>Waiting for first iteration...</p>
        </div>

        <!-- Iterations -->
        <div v-else class="iterations-list">
          <IterationCard
            v-for="(iter, index) in run.iterations"
            :key="iter.id ?? index"
            :iteration="iter"
            :isLatest="index === run.iterations.length - 1 && isRunning"
          />

          <!-- Running pulse at the bottom -->
          <div v-if="isRunning" class="running-pulse">
            <div class="pulse-dot" />
            <span>Agent is working on next iteration...</span>
          </div>
        </div>

        <!-- Final result banner -->
        <div v-if="finalIteration" class="result-banner" :class="finalIteration.isGoalReached ? 'success' : 'warn'">
          <div class="banner-top">
            <span v-if="finalIteration.isGoalReached">Goal reached in {{ run.iterations.length }} iteration{{ run.iterations.length > 1 ? 's' : '' }}</span>
            <span v-else>Max iterations reached — best result: {{ finalIteration.score }}%</span>
          </div>
          <div class="field">
            <p class="section-label">Final Optimized Prompt</p>
            <pre class="text-block copyable" @click="copyFinalPrompt">{{ finalIteration.prompt }}</pre>
            <p class="copy-hint">Click to copy</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { usePromptOptimizerStore } from '@/stores/promptOptimizer'
import { useAuthStore } from '@/stores/auth'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import IterationCard from '../components/IterationCard.vue'

const store     = usePromptOptimizerStore()
const authStore = useAuthStore()
const toast     = useToast()

// ── Model catalogue ───────────────────────────────────────────────────────────

const models        = ref([])
const modelsLoading = ref(false)

const PROVIDER_LABELS = {
  openai:    'OpenAI',
  anthropic: 'Anthropic',
  groq:      'Groq',
  ollama:    'Ollama (local)',
  vllm:      'vLLM',
}

function providerLabel(provider) {
  return PROVIDER_LABELS[provider] ?? provider
}

const groupedModels = computed(() => {
  const groups = {}
  for (const m of models.value) {
    if (!groups[m.provider]) groups[m.provider] = []
    groups[m.provider].push(m)
  }
  return groups
})

async function loadModels() {
  modelsLoading.value = true
  try {
    const { data } = await api.get('/v1/models')
    models.value = data
    // Keep form.model valid — fall back to first available model if the
    // current selection disappeared (e.g. Ollama was stopped).
    if (data.length && !data.find(m => m.id === form.value.model)) {
      form.value.model = data[0].id
    }
  } catch {
    toast.error('Could not load model list')
  } finally {
    modelsLoading.value = false
  }
}

const form = ref({
  basePrompt:     '',
  requiredOutput: '',
  model:          'groq/llama-3.3-70b-versatile',
  maxIterations:  5,
  scoreThreshold: 80,
})

onMounted(loadModels)

const run       = computed(() => store.activeRun)
const isRunning = computed(() => run.value?.status === 'running')

const finalIteration = computed(() => {
  if (!run.value || isRunning.value) return null
  const iters = run.value.iterations
  return iters.length > 0 ? iters[iters.length - 1] : null
})

const canSubmit = computed(() =>
  form.value.basePrompt.trim().length > 0 &&
  form.value.requiredOutput.trim().length > 0
)

// ── SSE ──────────────────────────────────────────────────────────────────────

let eventSource = null

function connectSSE(runId) {
  disconnectSSE()
  const base = import.meta.env.VITE_API_BASE_URL ?? ''
  const url  = `${base}/v1/prompt-optimizer/runs/${runId}/stream?token=${authStore.token}`
  eventSource = new EventSource(url)

  eventSource.onmessage = (event) => {
    let msg
    try { msg = JSON.parse(event.data) } catch { return }

    if (msg.type === 'iteration') {
      store.appendIteration(runId, msg.data)
    } else if (msg.type === 'done' || msg.type === 'cancelled') {
      // appendIteration already sets the terminal status; just close the stream
      disconnectSSE()
    } else if (msg.type === 'error') {
      toast.error(msg.data?.message ?? 'Optimizer error')
      disconnectSSE()
    }
  }

  eventSource.onerror = () => {
    disconnectSSE()
  }
}

function disconnectSSE() {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
}

onUnmounted(disconnectSSE)

// ── Actions ──────────────────────────────────────────────────────────────────

const { execute: handleStart, loading: submitLoading } = useAsync(async () => {
  store.clearActiveRun()
  const newRun = await store.startRun({ ...form.value })
  connectSSE(newRun.id)
  toast.success('Optimizer started')
})

const { execute: handleStop, loading: stopLoading } = useAsync(async () => {
  if (!run.value) return
  await store.stopRun(run.value.id)
  disconnectSSE()
  toast.success('Optimizer stopped')
})

function handleReset() {
  disconnectSSE()
  store.clearActiveRun()
  form.value = {
    basePrompt:     '',
    requiredOutput: '',
    model:          'groq/llama-3.3-70b-versatile',
    maxIterations:  5,
    scoreThreshold: 80,
  }
}

async function copyFinalPrompt() {
  if (!finalIteration.value) return
  await navigator.clipboard.writeText(finalIteration.value.prompt)
  toast.success('Prompt copied to clipboard')
}
</script>

<style scoped>
.optimizer-page { display: flex; flex-direction: column; gap: 1.25rem; height: 100%; }

/* Header */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-shrink: 0;
}
.page-header h2  { font-size: 1.1rem; font-weight: 600; }
.page-sub        { font-size: 0.85rem; color: var(--color-text-muted); margin-top: 0.2rem; }

/* Panels */
.panels {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 1.25rem;
  flex: 1;
  min-height: 0;
}

.panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
}

.panel-title {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-text-muted);
  letter-spacing: 0.04em;
  flex-shrink: 0;
}

.panel-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

/* Form fields */
.field { display: flex; flex-direction: column; gap: 0.35rem; }
.field-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text);
}
.required { color: var(--color-danger); margin-left: 2px; }
.field-hint { font-size: 0.78rem; color: var(--color-text-muted); }

.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }

.textarea, .select, .input {
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 0.9rem;
  font-family: var(--font-sans);
  outline: none;
  background: white;
  transition: border-color 0.15s;
  width: 100%;
}
.textarea { resize: vertical; line-height: 1.6; }
.textarea:focus, .select:focus, .input:focus { border-color: var(--color-primary); }
.textarea:disabled, .select:disabled, .input:disabled { background: #f8fafc; color: var(--color-text-muted); cursor: not-allowed; }

.threshold-row { display: flex; align-items: center; gap: 0.75rem; }
.range-input   { flex: 1; cursor: pointer; accent-color: var(--color-primary); }
.threshold-val { font-size: 0.85rem; font-weight: 600; color: var(--color-primary); min-width: 36px; }

/* Panel actions */
.panel-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: auto;
  padding-top: 0.5rem;
  flex-shrink: 0;
}

.btn-primary {
  flex: 1;
  padding: 0.6rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-primary:hover:not(:disabled) { background: var(--color-primary-hover); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-danger {
  flex: 1;
  padding: 0.6rem 1rem;
  background: var(--color-danger);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-danger:hover:not(:disabled) { background: #b91c1c; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-ghost {
  padding: 0.6rem 1rem;
  background: transparent;
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 0.9rem;
  cursor: pointer;
}
.btn-ghost:hover:not(:disabled) { background: #f1f5f9; }
.btn-ghost:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-secondary {
  padding: 0.5rem 1rem;
  background: #f1f5f9;
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
}
.btn-secondary:hover { background: #e2e8f0; }

/* Results panel */
.run-meta    { display: flex; align-items: center; gap: 0.75rem; }
.run-iter    { font-size: 0.8rem; color: var(--color-text-muted); }
.run-status  {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
}
.run-status.running   { background: #dbeafe; color: #1d4ed8; }
.run-status.completed { background: #dcfce7; color: #15803d; }
.run-status.failed    { background: #fee2e2; color: #dc2626; }
.run-status.cancelled { background: #fef9c3; color: #92400e; }

.results-panel { gap: 1rem; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  flex: 1;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  min-height: 200px;
}
.empty-icon { font-size: 2.5rem; }

.iterations-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.running-pulse {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.75rem;
  font-size: 0.85rem;
  color: var(--color-text-muted);
}
.pulse-dot {
  width: 10px;
  height: 10px;
  background: var(--color-primary);
  border-radius: 50%;
  flex-shrink: 0;
  animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.4; transform: scale(0.8); }
}

.spinner-lg {
  width: 32px; height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Result banner */
.result-banner {
  border-radius: var(--radius);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.25rem;
}
.result-banner.success { background: #f0fdf4; border: 1px solid #86efac; }
.result-banner.warn    { background: #fffbeb; border: 1px solid #fde68a; }

.banner-top { font-size: 0.9rem; font-weight: 600; }

.section-label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin-bottom: 0.3rem;
}
.text-block {
  background: #f8fafc;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  padding: 0.65rem 0.75rem;
  font-size: 0.85rem;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--font-sans);
  line-height: 1.6;
}
.text-block.copyable { cursor: pointer; }
.text-block.copyable:hover { background: #f1f5f9; }
.copy-hint { font-size: 0.75rem; color: var(--color-text-muted); text-align: right; }
</style>
