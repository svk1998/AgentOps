import { defineStore } from 'pinia'
import { ref } from 'vue'
import { promptOptimizerService } from '@/services/promptOptimizerService'

export const usePromptOptimizerStore = defineStore('promptOptimizer', () => {
  // ── State ──
  const runs       = ref([])
  const activeRun  = ref(null)   // the run currently shown in the optimizer view
  const total      = ref(0)

  // ── Actions ──
  async function loadRuns(params = {}) {
    const { data } = await promptOptimizerService.getRuns(params)
    runs.value  = data.items
    total.value = data.total
  }

  async function loadRunById(id) {
    const { data } = await promptOptimizerService.getRunById(id)
    activeRun.value = data
  }

  async function startRun(payload) {
    const { data } = await promptOptimizerService.createRun(payload)
    activeRun.value = data
    runs.value.unshift(data)
    total.value++
    return data
  }

  async function stopRun(id) {
    const { data } = await promptOptimizerService.stopRun(id)
    _patchRun(id, { status: data.status })
  }

  async function deleteRun(id) {
    await promptOptimizerService.deleteRun(id)
    runs.value  = runs.value.filter(r => r.id !== id)
    total.value--
    if (activeRun.value?.id === id) activeRun.value = null
  }

  // Called by WebSocket handler when a new iteration arrives
  function appendIteration(runId, iteration) {
    if (activeRun.value?.id === runId) {
      activeRun.value.iterations.push(iteration)
      if (iteration.isGoalReached || activeRun.value.iterations.length >= activeRun.value.maxIterations) {
        activeRun.value.status = iteration.isGoalReached ? 'completed' : 'failed'
      }
    }
    _patchRun(runId, { status: activeRun.value?.status ?? 'running' })
  }

  function clearActiveRun() {
    activeRun.value = null
  }

  function _patchRun(id, patch) {
    const index = runs.value.findIndex(r => r.id === id)
    if (index !== -1) runs.value[index] = { ...runs.value[index], ...patch }
    if (activeRun.value?.id === id) activeRun.value = { ...activeRun.value, ...patch }
  }

  return {
    runs, activeRun, total,
    loadRuns, loadRunById, startRun, stopRun, deleteRun,
    appendIteration, clearActiveRun,
  }
})
