import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/authService'

// Mock the service — store doesn't hit real HTTP
vi.mock('@/services/authService')
vi.mock('@/router', () => ({ default: { push: vi.fn() } }))

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('starts unauthenticated', () => {
    const auth = useAuthStore()
    expect(auth.isLoggedIn).toBe(false)
    expect(auth.user).toBeNull()
  })

  it('sets token and user on login', async () => {
    authService.login.mockResolvedValue({
      data: { token: 'abc123', user: { id: 1, firstName: 'Shiv', role: 'admin' } }
    })

    const auth = useAuthStore()
    await auth.login({ email: 'shiv@example.com', password: 'pass' })

    expect(auth.isLoggedIn).toBe(true)
    expect(auth.token).toBe('abc123')
    expect(auth.isAdmin).toBe(true)
  })

  it('clears state on logout', async () => {
    const auth = useAuthStore()
    auth.token = 'abc123'
    auth.user  = { id: 1 }

    auth.logout()

    expect(auth.isLoggedIn).toBe(false)
    expect(auth.user).toBeNull()
  })
})
