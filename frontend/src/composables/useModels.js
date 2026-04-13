/**
 * Composable for loading and grouping available LLM models.
 * Shared between PromptOptimizerView, AgentFormModal, RunTriggerModal.
 */
import { ref, computed } from 'vue'
import api from '@/services/api'

const PROVIDER_LABELS = {
  openai:    'OpenAI',
  anthropic: 'Anthropic',
  groq:      'Groq',
  ollama:    'Ollama (local)',
  vllm:      'vLLM',
}

export function useModels() {
  const models  = ref([])
  const loading = ref(false)

  const groupedModels = computed(() => {
    const groups = {}
    for (const m of models.value) {
      if (!groups[m.provider]) groups[m.provider] = []
      groups[m.provider].push(m)
    }
    return groups
  })

  function providerLabel(provider) {
    return PROVIDER_LABELS[provider] ?? provider
  }

  async function loadModels() {
    loading.value = true
    try {
      const { data } = await api.get('/models')
      models.value = data
    } catch {
      models.value = []
    } finally {
      loading.value = false
    }
  }

  return { models, loading, groupedModels, providerLabel, loadModels }
}
