import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

/**
 * Theme store — dark (default) or light.
 *
 *  - Persists choice to localStorage via pinia-plugin-persistedstate.
 *  - Syncs <html data-theme="..."> on every change so the CSS tokens
 *    in assets/theme.css can swap light/dark variables automatically.
 *  - Also respects OS preference on first load if the user has never
 *    explicitly picked a theme.
 */
export const useThemeStore = defineStore('theme', () => {
  const THEMES = ['dark', 'light']
  const stored = null // populated by pinia-persisted-state
  const initial = detectInitial(stored)

  const theme = ref(initial)
  const hasExplicitChoice = ref(false)

  function apply(next) {
    if (!THEMES.includes(next)) return
    theme.value = next
    hasExplicitChoice.value = true
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', next)
    }
  }

  function toggle() {
    apply(theme.value === 'dark' ? 'light' : 'dark')
  }

  // React to restored state (pinia-persistedstate hydration happens after init)
  watch(theme, (next) => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', next)
    }
  }, { immediate: true })

  return { theme, hasExplicitChoice, apply, toggle }
}, {
  persist: { paths: ['theme', 'hasExplicitChoice'] },
})

function detectInitial(stored) {
  if (stored === 'dark' || stored === 'light') return stored
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'
  }
  return 'dark'
}
