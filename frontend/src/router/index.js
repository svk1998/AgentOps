import { createRouter, createWebHistory } from 'vue-router'
import { routes } from './routes'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0, behavior: 'smooth' })
})

// ── Global Navigation Guard ──
router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Update page title
  document.title = to.meta.title
    ? `${to.meta.title} — ${import.meta.env.VITE_APP_TITLE}`
    : import.meta.env.VITE_APP_TITLE

  // Redirect logged-in users away from guest-only pages (e.g. /login)
  if (to.meta.guestOnly && auth.isLoggedIn) {
    return { name: 'Dashboard' }
  }

  // Redirect unauthenticated users to login, preserve intended destination
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }

  // Role-based access control
  if (to.meta.requiresRole && !auth.hasRole(to.meta.requiresRole)) {
    return { name: 'Dashboard' } // or a dedicated /forbidden page
  }
})

export default router
