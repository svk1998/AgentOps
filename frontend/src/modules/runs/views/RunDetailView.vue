<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Run Detail</h1>
        <p class="page-subtitle font-mono" style="font-size:0.75rem">{{ id }}</p>
      </div>
      <div class="header-actions">
        <AppButton
          v-if="run && ['pending','running'].includes(run.status)"
          variant="danger"
          size="sm"
          :loading="cancelling"
          @click="cancelRun"
        >
          Cancel
        </AppButton>
        <AppButton variant="ghost" size="sm" @click="load">Refresh</AppButton>
      </div>
    </div>

    <div v-if="!run && loading" class="loading-state">
      <AppSpinner :size="32" />
    </div>

    <div v-else-if="run" class="run-layout">
      <!-- Log viewer -->
      <AppCard :padding="false" class="log-panel">
        <template #header>
          <span class="card-title">
            Live Logs
            <AppBadge :variant="run.status" :dot="run.status === 'running'" style="margin-left:.5rem">
              {{ run.status }}
            </AppBadge>
          </span>
          <span class="log-count text-muted">{{ logs.length }} entries</span>
        </template>
        <div ref="logContainer" class="log-list">
          <div
            v-for="log in logs"
            :key="log.sequence ?? log.id"
            :class="['log-line', `log-line--${log.level}`]"
          >
            <span class="log-seq">{{ String(log.sequence ?? '').padStart(3, '0') }}</span>
            <span class="log-level">{{ log.level?.toUpperCase() }}</span>
            <span class="log-msg">{{ log.message }}</span>
          </div>
          <div v-if="!logs.length && !loading" class="log-empty">No logs yet...</div>
          <div v-if="run.status === 'running'" class="log-cursor">▌</div>
        </div>
      </AppCard>

      <!-- Metadata panel -->
      <div class="meta-panel">
        <!-- Status card -->
        <AppCard>
          <template #header><span class="card-title">Run Info</span></template>
          <div class="meta-rows">
            <div class="meta-row">
              <span class="meta-key">Status</span>
              <AppBadge :variant="run.status" :dot="run.status === 'running'">{{ run.status }}</AppBadge>
            </div>
            <div class="meta-row">
              <span class="meta-key">Agent</span>
              <RouterLink v-if="run.agent_id" :to="`/agents/${run.agent_id}`" class="meta-link">
                {{ run.agent_name || run.agent_id }}
              </RouterLink>
            </div>
            <div class="meta-row">
              <span class="meta-key">Started</span>
              <span class="meta-val">{{ formatDateTime(run.created_at) }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-key">Duration</span>
              <span class="meta-val">{{ formatDuration(run.created_at, run.finished_at) }}</span>
            </div>
            <div v-if="run.usage" class="meta-row">
              <span class="meta-key">Tokens</span>
              <span class="meta-val font-mono">
                {{ formatTokens(run.usage.total_tokens) }}
                <span class="text-subtle">({{ run.usage.prompt_tokens }}p / {{ run.usage.completion_tokens }}c)</span>
              </span>
            </div>
          </div>
        </AppCard>

        <!-- Input -->
        <AppCard>
          <template #header><span class="card-title">Input</span></template>
          <AppCode :content="JSON.stringify(run.input, null, 2)" />
        </AppCard>

        <!-- Output -->
        <AppCard v-if="run.output || run.error">
          <template #header>
            <span class="card-title">{{ run.error ? 'Error' : 'Output' }}</span>
          </template>
          <AppCode
            v-if="run.error"
            :content="run.error"
            style="--color-text: var(--color-danger-text)"
          />
          <AppCode v-else :content="JSON.stringify(run.output, null, 2)" />
        </AppCard>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { runService } from '@/services/runService'
import { useSSE } from '@/composables/useSSE'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppCode from '@/components/ui/AppCode.vue'
import { formatTokens, formatRelativeTime, formatDuration, formatDateTime } from '@/utils/format'

const route = useRoute()
const auth  = useAuthStore()
const toast = useToast()
const id    = route.params.id

const run        = ref(null)
const logs       = ref([])
const loading    = ref(false)
const cancelling = ref(false)
const logContainer = ref(null)

const { connect, disconnect } = useSSE()

async function load() {
  loading.value = true
  try {
    const [runRes, logsRes] = await Promise.all([
      runService.getById(id),
      runService.getLogs(id),
    ])
    run.value  = runRes.data
    logs.value = logsRes.data
  } finally { loading.value = false }
}

function scrollToBottom() {
  nextTick(() => {
    if (logContainer.value) logContainer.value.scrollTop = logContainer.value.scrollHeight
  })
}

watch(logs, scrollToBottom, { deep: true })

async function cancelRun() {
  cancelling.value = true
  try {
    const { data } = await runService.cancel(id)
    run.value = data
    toast.success('Run cancelled')
    disconnect()
  } catch { toast.error('Failed to cancel') }
  finally  { cancelling.value = false }
}

onMounted(async () => {
  await load()

  if (run.value?.status === 'pending' || run.value?.status === 'running') {
    const url = `/api/v1/runs/${id}/stream?token=${auth.token}`
    connect(url, (data) => {
      if (data.message === '__done__') {
        load()
        disconnect()
        return
      }
      logs.value.push(data)
      // also refresh run metadata periodically
      if (data.sequence % 10 === 0) load()
    })
  }
})

onUnmounted(disconnect)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 1.25rem; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; }
.page-title  { font-size: 1.4rem; font-weight: 700; }
.header-actions { display: flex; gap: 0.5rem; }
.loading-state { display: grid; place-items: center; height: 300px; }

.run-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 1rem;
  align-items: start;
}
@media (max-width: 900px) { .run-layout { grid-template-columns: 1fr; } }

/* Log panel */
.log-panel  { height: calc(100vh - 220px); display: flex; flex-direction: column; }
.card-title { font-size: 0.9rem; font-weight: 600; display: flex; align-items: center; }
.log-count  { font-size: 0.78rem; }

.log-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  line-height: 1.7;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.log-line   { display: flex; gap: 0.75rem; padding: 0.15rem 0.4rem; border-radius: 3px; }
.log-line--error   { background: var(--color-danger-subtle); }
.log-line--warning { background: var(--color-warning-subtle); }
.log-seq   { color: var(--color-text-subtle); width: 28px; flex-shrink: 0; text-align: right; }
.log-level { width: 50px; flex-shrink: 0; font-weight: 600; }
.log-line--info  .log-level { color: var(--color-info); }
.log-line--error .log-level { color: var(--color-danger-text); }
.log-line--warning .log-level { color: var(--color-warning-text); }
.log-line--debug .log-level { color: var(--color-text-subtle); }
.log-msg   { flex: 1; color: var(--color-text); word-break: break-word; }
.log-empty { color: var(--color-text-subtle); text-align: center; padding: 2rem; }
.log-cursor { color: var(--color-primary); animation: pulse-dot 1s infinite; font-size: 1rem; }

/* Meta panel */
.meta-panel { display: flex; flex-direction: column; gap: 1rem; }
.meta-rows  { display: flex; flex-direction: column; gap: 0.6rem; }
.meta-row   { display: flex; justify-content: space-between; align-items: center; gap: 1rem; font-size: 0.82rem; }
.meta-key   { color: var(--color-text-muted); flex-shrink: 0; }
.meta-val   { color: var(--color-text); text-align: right; }
.meta-link  { color: var(--color-primary-light); }
.meta-link:hover { text-decoration: underline; }
</style>
