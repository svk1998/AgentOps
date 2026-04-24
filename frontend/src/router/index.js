import { createRouter, createWebHistory } from 'vue-router'
import { routes } from './routes'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0, behavior: 'smooth' }),
})

/**
 * Global navigation guard.
 *
 * Auth state is hydrated once on app boot (see main.js:boot() — it awaits
 * auth.init() before mounting). This guard defensively awaits auth.ready
 * too, so in-flight hydration never causes a bad gate decision if some
 * other code triggers a route change before boot completes.
 */
router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Defensive: wait for initial hydration so `user` is populated before
  // we evaluate requiresAuth / requiresRole.
  if (!auth.ready) await auth.init()

  // Page title
  document.title = to.meta.title
    ? `${to.meta.title} — ${import.meta.env.VITE_APP_TITLE}`
    : import.meta.env.VITE_APP_TITLE

  // Redirect signed-in users away from guest-only pages (/login, /register)
  if (to.meta.guestOnly && auth.isLoggedIn) {
    return { name: 'Dashboard' }
  }

  // Redirect unauthenticated users to login, preserving intended destination
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }

  // Role-based access control
  if (to.meta.requiresRole && !auth.hasRole(to.meta.requiresRole)) {
    return { name: 'Dashboard' }
  }
})

export default router
