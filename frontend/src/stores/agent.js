import { defineStore } from 'pinia'
import { ref } from 'vue'
import { agentService } from '@/services/agentService'

export const useAgentStore = defineStore('agent', () => {
  const agents  = ref([])
  const current = ref(null)

  async function loadAgents(params = {}) {
    const { data } = await agentService.getAll(params)
    agents.value = Array.isArray(data) ? data : []
  }

  async function loadById(id) {
    const { data } = await agentService.getById(id)
    current.value = data
  }

  async function createAgent(payload) {
    const { data } = await agentService.create(payload)
    agents.value.unshift(data)
    return data
  }

  async function updateAgent(id, payload) {
    const { data } = await agentService.update(id, payload)
    const index = agents.value.findIndex(a => a.id === id)
    if (index !== -1) agents.value[index] = data
    if (current.value?.id === id) current.value = data
    return data
  }

  async function deleteAgent(id) {
    await agentService.delete(id)
    agents.value = agents.value.filter(a => a.id !== id)
    if (current.value?.id === id) current.value = null
  }

  return { agents, current, loadAgents, loadById, createAgent, updateAgent, deleteAgent }
})
