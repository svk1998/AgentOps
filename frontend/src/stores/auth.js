import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { jwtDecode } from 'jwt-decode'

import { authService } from '@/services/authService'
import router from '@/router'

/**
 * Auth store — the source of truth for who is signed in.
 *
 * Persistence model:
 *  - Only the raw JWT is persisted to localStorage (via
 *    pinia-plugin-persistedstate). The `user` object is derived by
 *    calling GET /auth/me on boot — never persisted, so revoked/edited
 *    users always re-hydrate with fresh role/is_active data.
 *  - On app boot, `init()` validates the stored token's `exp` claim
 *    locally (cheap, no network), then calls fetchMe() to populate
 *    `user`. If the token is expired or invalid, local state is cleared
 *    and the user is routed to /login.
 *
 * Refresh strategy:
 *  - A timer fires REFRESH_LEAD_MS (2 minutes) before the token would
 *    expire and silently exchanges it for a fresh one via /auth/refresh.
 *  - A 401 on any API call clears state and kicks the user to /login
 *    (handled by the response interceptor).
 */

// Fire refresh 2 minutes before expiry — enough slack for the round trip
// on a slow connection, but not so early that idle users refresh a lot.
const REFRESH_LEAD_MS = 2 * 60 * 1000

export const useAuthStore = defineStore('auth', () => {
  const user  = ref(null)
  const token = ref(null)
  const ready = ref(false)  // true after init() finishes (success or failure)

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin    = computed(() => !!user.value?.is_superuser)
  const fullName   = computed(() => user.value?.full_name || user.value?.email || '')

  /**
   * Role check for router guards.
   *   - 'admin' matches anyone with is_superuser
   *   - any other role string matches when user.role === role
   */
  function hasRole(role) {
    if (!user.value) return false
    if (role === 'admin') return !!user.value.is_superuser
    return user.value.role === role
  }

  /** Epoch ms when the current token expires, or null. */
  const expiresAt = computed(() => {
    if (!token.value) return null
    try {
      const { exp } = jwtDecode(token.value)
      return typeof exp === 'number' ? exp * 1000 : null
    } catch { return null }
  })

  /** Is the stored token present and not yet expired? */
  function isTokenValid() {
    if (!token.value) return false
    const exp = expiresAt.value
    return !!exp && exp > Date.now()
  }

  // ── Init (call once at app boot, before mounting) ──────────────────────
  async function init() {
    if (ready.value) return
    try {
      if (isTokenValid()) {
        await fetchMe()
        scheduleRefresh()
      } else if (token.value) {
        // Stored token is expired — discard silently
        _clearLocal()
      }
    } catch {
      _clearLocal()
    } finally {
      ready.value = true
    }
  }

  // ── Login / me / refresh / logout ──────────────────────────────────────

  async function login(credentials) {
    const { data } = await authService.login(credentials)
    token.value = data.access_token
    await fetchMe()
    scheduleRefresh()
  }

  async function fetchMe() {
    if (!token.value) return
    const { data } = await authService.me()
    user.value = data
  }

  /**
   * Swap the current valid JWT for a fresh one. Safe to call at any time —
   * returns false if no valid token is present so callers can just await
   * it without branching.
   */
  async function refresh() {
    if (!isTokenValid()) return false
    try {
      const { data } = await authService.refreshToken()
      token.value = data.access_token
      scheduleRefresh()
      return true
    } catch {
      // Refresh failed — treat the session as dead so the user re-signs-in
      _clearLocal()
      router.push({ name: 'Login', query: { reason: 'session-expired' } })
      return false
    }
  }

  // Re-entry guard — the 401 interceptor also calls logout(), so a failing
  // /auth/logout must not trigger a second /auth/logout call.
  let _loggingOut = false

  async function logout({ silent = false, redirect = true } = {}) {
    if (_loggingOut) return
    _loggingOut = true
    try {
      _cancelRefresh()
      if (token.value) {
        try { await authService.logout() } catch { /* local-authoritative */ }
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
    _cancelRefresh()
    user.value  = null
    token.value = null
  }

  // ── Auto-refresh timer ─────────────────────────────────────────────────
  let _refreshTimer = null

  function scheduleRefresh() {
    _cancelRefresh()
    const exp = expiresAt.value
    if (!exp) return
    const fireIn = exp - Date.now() - REFRESH_LEAD_MS
    // If the token is already within the lead window, refresh shortly.
    const delay = Math.max(fireIn, 5_000)
    _refreshTimer = setTimeout(() => { refresh() }, delay)
  }

  function _cancelRefresh() {
    if (_refreshTimer) {
      clearTimeout(_refreshTimer)
      _refreshTimer = null
    }
  }

  return {
    // state
    user, token, ready,
    // derived
    isLoggedIn, isAdmin, fullName, expiresAt,
    // actions
    init, login, fetchMe, refresh, logout,
    isTokenValid, hasRole,
  }
}, {
  // Only the raw token is persisted; user + ready are derived on boot.
  persist: { paths: ['token'] },
})
