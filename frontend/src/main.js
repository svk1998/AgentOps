import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import Tooltip from 'primevue/tooltip'
import { definePreset } from '@primeuix/themes'
import Aura from '@primeuix/themes/aura'

import App from './App.vue'
import router from './router'
import './services/interceptors' // register axios interceptors
import { useAuthStore } from './stores/auth'
import { useThemeStore } from './stores/theme'

// Global styles
import 'primeicons/primeicons.css'
import './assets/main.css'

// ── PrimeVue preset ────────────────────────────────────────────────────────
// Override Aura's default emerald primary with the indigo palette that
// matches the existing brand. Dark mode is driven by the `.app-dark` class
// we put on <html> in index.html.
const AgentOpsPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50:  '#FFFBEB',
      100: '#FEF3C7',
      200: '#FDE68A',
      300: '#FCD34D',
      400: '#FBBF24',
      500: '#F5A524',
      600: '#D97706',
      700: '#B45309',
      800: '#92400E',
      900: '#78350F',
      950: '#3A2A0E',
    },
    colorScheme: {
      dark: {
        surface: {
          0:   '#ffffff',
          50:  '#E6E8EB',
          100: '#9BA3AE',
          200: '#6E7685',
          300: '#5B6270',
          400: '#2A3038',
          500: '#1C2025',
          600: '#16191D',
          700: '#111316',
          800: '#0F1114',
          900: '#0A0B0D',
          950: '#070809',
        },
      },
    },
  },
})

const app = createApp(App)

// Pinia (state management)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)

// Router
app.use(router)

// PrimeVue + services + directives
app.use(PrimeVue, {
  theme: {
    preset: AgentOpsPreset,
    options: {
      darkModeSelector: '.app-dark',
      cssLayer: false,
    },
  },
  ripple: true,
})
app.use(ToastService)
app.use(ConfirmationService)
app.directive('tooltip', Tooltip)

// Initialize theme (reads persisted choice, else OS preference) and applies
// it to <html> before the first render — prevents a flash of wrong theme.
useThemeStore()

// Rehydrate auth state from the persisted JWT (if any) BEFORE mounting.
// This calls /auth/me so the `user` object is ready when the router guards
// evaluate meta.requiresAuth / requiresRole. Without this, a page refresh
// on an authenticated route bounces to /login because `user` is briefly null.
async function boot() {
  const auth = useAuthStore()
  await auth.init()
  app.mount('#app')
}

boot()
