import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/authService'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user  = ref(null)
  const token = ref(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin    = computed(() => !!user.value?.is_superuser)
  const fullName   = computed(() => user.value?.full_name || user.value?.email || '')

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
      // Token invalid → clear local state silently (backend is not callable
      // with a bad token, so no /auth/logout attempt).
      _clearLocal()
      router.push({ name: 'Login' })
    }
  }

  // Re-entry guard — the 401 response interceptor also calls logout(), so
  // a failing /auth/logout must not trigger a second /auth/logout call.
  let _loggingOut = false

  /**
   * Full logout.
   *  1. Fire-and-forget the backend /auth/logout (stateless for JWT, but
   *     gives the server a hook for session tracking / token blacklists).
   *  2. Clear local state + persisted token.
   *  3. Redirect to /login, preserving the current path as `?redirect=`
   *     so the user lands back where they were after re-auth.
   *
   *  `silent=true` → auto-logout (e.g. from 401 interceptor). No
   *  `reason=signed-out` query added.
   */
  async function logout({ silent = false, redirect = true } = {}) {
    if (_loggingOut) return
    _loggingOut = true

    try {
      if (token.value) {
        // Best-effort — never block logout on a server error
        try { await authService.logout() } catch { /* logout is local-authoritative */ }
      }

      _clearLocal()

      if (redirect) {
        const from = router.currentRoute.value.fullPath
        const query = { ...(silent ? {} : { reason: 'signed-out' }) }
        if (from && from !== '/' && !from.startsWith('/login')) query.redirect = from
        router.push({ name: 'Login', query })
      }
    } finally {
      _loggingOut = false
    }
  }

  function _clearLocal() {
    user.value  = null
    token.value = null
  }

  return {
    user, token,
    isLoggedIn, isAdmin, fullName,
    login, fetchMe, logout,
  }
}, {
  persist: { paths: ['token'] }
})
