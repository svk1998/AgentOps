import { defineStore } from 'pinia'
import { ref } from 'vue'
import { userService } from '@/services/userService'

export const useUserStore = defineStore('user', () => {
  // ── State ──
  const users   = ref([])
  const current = ref(null)
  const total   = ref(0)

  // ── Actions ──
  async function loadUsers(params = {}) {
    const { data } = await userService.getAll(params)
    users.value = data.items
    total.value = data.total
  }

  async function loadById(id) {
    const { data } = await userService.getById(id)
    current.value = data
  }

  async function createUser(payload) {
    const { data } = await userService.create(payload)
    users.value.unshift(data)
    total.value++
  }

  async function updateUser(id, payload) {
    const { data } = await userService.update(id, payload)
    const index = users.value.findIndex(u => u.id === id)
    if (index !== -1) users.value[index] = data
  }

  async function deleteUser(id) {
    await userService.delete(id)
    users.value = users.value.filter(u => u.id !== id)
    total.value--
  }

  return { users, current, total, loadUsers, loadById, createUser, updateUser, deleteUser }
})
