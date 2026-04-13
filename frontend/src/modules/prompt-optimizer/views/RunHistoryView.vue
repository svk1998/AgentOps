<template>
  <div class="history-page">
    <div class="page-header">
      <div>
        <h2>Run History</h2>
        <p class="page-sub">All previous prompt optimization runs.</p>
      </div>
      <RouterLink to="/prompt-optimizer" class="btn-primary">+ New Run</RouterLink>
    </div>

    <div class="card">
      <p v-if="loading" class="muted">Loading runs...</p>
      <p v-else-if="error" class="danger">{{ error }}</p>

      <table v-else class="table">
        <thead>
          <tr>
            <th>Base Prompt</th>
            <th>Model</th>
            <th>Status</th>
            <th>Iterations</th>
            <th>Best Score</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="run in store.runs" :key="run.id" class="run-row" @click="goToRun(run.id)">
            <td>
              <span class="prompt-snippet">{{ truncate(run.basePrompt, 60) }}</span>
            </td>
            <td><code class="model-tag">{{ run.model }}</code></td>
            <td><span class="run-status" :class="run.status">{{ run.status }}</span></td>
            <td>{{ run.iterations?.length ?? 0 }} / {{ run.maxIterations }}</td>
            <td>
              <span v-if="run.bestScore != null" class="score" :class="scoreClass(run.bestScore)">
                {{ run.bestScore }}%
              </span>
              <span v-else class="muted-inline">—</span>
            </td>
            <td>{{ formatDate(run.createdAt) }}</td>
            <td class="actions" @click.stop>
              <RouterLink :to="`/prompt-optimizer/${run.id}`" class="btn-sm">View</RouterLink>
              <button
                class="btn-sm danger"
                :disabled="deleteLoading"
                @click="handleDelete(run.id)"
              >
                Delete
              </button>
            </td>
          </tr>
          <tr v-if="store.runs.length === 0">
            <td colspan="7" class="empty">No runs yet. Start your first optimization.</td>
          </tr>
        </tbody>
      </table>

      <p class="table-footer">Total: {{ store.total }} runs</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { usePromptOptimizerStore } from '@/stores/promptOptimizer'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'
import { formatDate, truncate } from '@/utils/format'

const store  = usePromptOptimizerStore()
const toast  = useToast()
const router = useRouter()

const loading = ref(false)
const error   = ref(null)

const { execute: handleDelete, loading: deleteLoading } = useAsync(async (id) => {
  await store.deleteRun(id)
  toast.success('Run deleted')
})

function goToRun(id) {
  router.push(`/prompt-optimizer/${id}`)
}

function scoreClass(score) {
  if (score >= 80) return 'high'
  if (score >= 50) return 'mid'
  return 'low'
}

onMounted(async () => {
  loading.value = true
  try {
    await store.loadRuns()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.history-page { display: flex; flex-direction: column; gap: 1.25rem; }

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}
.page-header h2 { font-size: 1.1rem; font-weight: 600; }
.page-sub { font-size: 0.85rem; color: var(--color-text-muted); margin-top: 0.2rem; }

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  overflow: hidden;
}

.table { width: 100%; border-collapse: collapse; }
.table th, .table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.9rem;
}
.table th {
  background: #f8fafc;
  font-weight: 600;
  font-size: 0.8rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
}
.run-row { cursor: pointer; }
.run-row:hover { background: #f8fafc; }

.prompt-snippet { color: var(--color-text); }

.model-tag {
  font-size: 0.8rem;
  background: #f1f5f9;
  padding: 0.15rem 0.4rem;
  border-radius: 0.25rem;
  color: #475569;
}

.run-status {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  display: inline-block;
}
.run-status.running   { background: #dbeafe; color: #1d4ed8; }
.run-status.completed { background: #dcfce7; color: #15803d; }
.run-status.failed    { background: #fee2e2; color: #dc2626; }
.run-status.cancelled { background: #fef9c3; color: #92400e; }

.score { font-size: 0.85rem; font-weight: 600; }
.score.high { color: var(--color-success); }
.score.mid  { color: var(--color-warning); }
.score.low  { color: var(--color-danger); }
.muted-inline { color: var(--color-text-muted); }

.actions { display: flex; gap: 0.5rem; }
.btn-sm {
  padding: 0.3rem 0.65rem;
  font-size: 0.8rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: white;
  cursor: pointer;
  text-decoration: none;
  color: var(--color-text);
  transition: background 0.15s;
  display: inline-block;
}
.btn-sm:hover   { background: #f1f5f9; }
.btn-sm:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-sm.danger  { color: var(--color-danger); border-color: #fecaca; }
.btn-sm.danger:hover { background: #fef2f2; }

.table-footer { padding: 0.75rem 1rem; font-size: 0.8rem; color: var(--color-text-muted); }
.empty { text-align: center; color: var(--color-text-muted); padding: 2rem !important; }
.muted  { padding: 1rem; color: var(--color-text-muted); font-size: 0.9rem; }
.danger { padding: 1rem; color: var(--color-danger); font-size: 0.9rem; }

.btn-primary {
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}
.btn-primary:hover { background: var(--color-primary-hover); }
</style>
