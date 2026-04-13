import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/authService'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user  = ref(null)
  const token = ref(null)

  const isLoggedIn  = computed(() => !!token.value)
  const isAdmin     = computed(() => !!user.value?.is_superuser)
  const fullName    = computed(() => user.value?.full_name || user.value?.email || '')

  async function login(credentials) {
    const { data } = await authService.login(credentials)
    token.value = data.access_token
    await fetchMe()
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      const { data } = await authService.me()
      user.value = data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value  = null
    token.value = null
    router.push({ name: 'Login' })
  }

  return { user, token, isLoggedIn, isAdmin, fullName, login, fetchMe, logout }
}, {
  persist: { paths: ['token'] }
})
