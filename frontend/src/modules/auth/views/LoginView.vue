<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <h1>⚡ MyApp</h1>
        <p>Sign in to your account</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="field">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="you@company.com"
            autocomplete="email"
            required
          />
        </div>

        <div class="field">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAsync } from '@/composables/useAsync'

const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()

const form = ref({ email: '', password: '' })

const { execute, loading, error } = useAsync(auth.login)

async function handleLogin() {
  try {
    await execute(form.value)
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch {
    // error is already set by useAsync, do not redirect
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #f1f5f9;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 0.75rem;
  padding: 2.5rem;
  box-shadow: var(--shadow-md);
}

.login-header { text-align: center; margin-bottom: 2rem; }
.login-header h1 { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; }
.login-header p  { color: var(--color-text-muted); font-size: 0.9rem; }

.login-form { display: flex; flex-direction: column; gap: 1.25rem; }

.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field label { font-size: 0.875rem; font-weight: 500; }
.field input {
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.15s;
}
.field input:focus { border-color: var(--color-primary); }

.error-msg {
  color: var(--color-danger);
  font-size: 0.85rem;
  padding: 0.5rem;
  background: #fef2f2;
  border-radius: var(--radius);
}

.btn-primary {
  padding: 0.7rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-primary:hover:not(:disabled) { background: var(--color-primary-hover); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
