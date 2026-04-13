<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Models</h1>
        <p class="page-subtitle">{{ models.length }} models available</p>
      </div>
      <AppButton variant="ghost" size="sm" :loading="loading" @click="loadModels">Refresh</AppButton>
    </div>

    <div v-if="loading && !models.length" class="loading-state">
      <AppSpinner :size="32" />
    </div>

    <div v-else class="providers-list">
      <AppCard
        v-for="(group, provider) in groupedModels"
        :key="provider"
      >
        <template #header>
          <div class="provider-header">
            <div class="provider-name-row">
              <span class="provider-pill">{{ providerLabel(provider) }}</span>
              <AppBadge variant="neutral">{{ group.length }} models</AppBadge>
            </div>
            <AppBadge
              v-if="provider === 'ollama' || provider === 'vllm'"
              :variant="group.length ? 'success' : 'danger'"
            >
              {{ group.length ? 'Reachable' : 'Unreachable' }}
            </AppBadge>
          </div>
        </template>
        <div class="models-list">
          <div v-for="m in group" :key="m.id" class="model-row">
            <div class="model-info">
              <span class="model-name">{{ m.name }}</span>
              <span class="model-id font-mono">{{ m.id }}</span>
            </div>
            <button class="copy-btn" :title="copied === m.id ? 'Copied!' : 'Copy model ID'" @click="copy(m.id)">
              {{ copied === m.id ? '✓' : '⎘' }}
            </button>
          </div>
        </div>
      </AppCard>

      <AppEmptyState
        v-if="!loading && !models.length"
        title="No models available"
        description="Add API keys to .env or start Ollama/vLLM to see models here."
      >
        <template #icon>🤖</template>
      </AppEmptyState>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useModels } from '@/composables/useModels'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'

const { models, loading, groupedModels, providerLabel, loadModels } = useModels()

const copied = ref('')
async function copy(id) {
  await navigator.clipboard.writeText(id)
  copied.value = id
  setTimeout(() => { copied.value = '' }, 2000)
}

onMounted(loadModels)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 1.5rem; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; }
.page-title  { font-size: 1.4rem; font-weight: 700; }
.page-subtitle { color: var(--color-text-muted); font-size: 0.875rem; margin-top: 0.2rem; }
.loading-state { display: grid; place-items: center; height: 200px; }

.providers-list { display: flex; flex-direction: column; gap: 1rem; }

.provider-header { display: flex; align-items: center; justify-content: space-between; width: 100%; }
.provider-name-row { display: flex; align-items: center; gap: 0.75rem; }
.provider-pill {
  font-size: 0.875rem; font-weight: 600;
}

.models-list { display: flex; flex-direction: column; }
.model-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.65rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
  transition: background var(--transition);
}
.model-row:last-child { border-bottom: none; }
.model-row:hover { background: var(--color-surface-2); }
.model-info { display: flex; flex-direction: column; gap: 0.15rem; }
.model-name { font-size: 0.875rem; font-weight: 500; }
.model-id   { font-size: 0.75rem; color: var(--color-text-muted); }
.copy-btn {
  background: var(--color-surface-3); border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); color: var(--color-text-muted);
  cursor: pointer; padding: 0.2rem 0.5rem; font-size: 0.75rem;
  transition: color var(--transition), background var(--transition);
}
.copy-btn:hover { color: var(--color-text); background: var(--color-surface-2); }
</style>
