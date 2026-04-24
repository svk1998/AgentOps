<template>
  <div class="login-shell">
    <!-- Subtle grid backdrop -->
    <div class="login-backdrop" aria-hidden="true" />

    <main class="login-main">
      <!-- Brand -->
      <div class="login-brand">
        <svg width="32" height="32" viewBox="0 0 18 18" fill="none">
          <rect x="1" y="1" width="16" height="16" rx="3" fill="var(--accent)" />
          <path
            d="M5 12 L9 5 L13 12 M6.5 10 H11.5"
            stroke="var(--accent-text)"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            fill="none"
          />
        </svg>
        <div class="brand-text">
          <div class="brand-name mono">agentops</div>
          <div class="brand-tag mono faint">evaluation · observability · ops</div>
        </div>
      </div>

      <!-- Card -->
      <div class="login-card">
        <div class="login-head">
          <div class="login-eyebrow mono faint">authentication required</div>
          <h1 class="login-title">Sign in</h1>
        </div>

        <!-- Signed-out banner — appears after user-initiated logout -->
        <div v-if="reason === 'signed-out'" class="login-banner mono">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 8l3 3 7-7"/>
          </svg>
          Signed out. See you again.
        </div>

        <!-- Session-expired banner — appears when auto-refresh fails -->
        <div v-else-if="reason === 'session-expired'" class="login-warn mono">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="8" cy="8" r="6.5"/><path d="M8 4.5v4M8 11.5v0.01"/>
          </svg>
          Your session expired. Please sign in again.
        </div>

        <form class="login-form" @submit.prevent="handleLogin">
          <div class="field">
            <label for="email" class="field-label mono">Email</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              class="input login-input"
              placeholder="you@company.com"
              autocomplete="email"
              autofocus
              required
            />
          </div>

          <div class="field">
            <label for="password" class="field-label mono">
              <span>Password</span>
              <span class="field-hint mono">min 8 chars</span>
            </label>
            <div class="password-wrap">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                class="input login-input password-input"
                placeholder="••••••••"
                autocomplete="current-password"
                required
                minlength="8"
              />
              <button
                type="button"
                class="password-toggle"
                :aria-label="showPassword ? 'Hide password' : 'Show password'"
                @click="showPassword = !showPassword"
              >
                <svg v-if="showPassword" width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z"/>
                  <circle cx="8" cy="8" r="2"/>
                </svg>
                <svg v-else width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M2 2l12 12"/>
                  <path d="M6.7 3.2A7.5 7.5 0 0 1 8 3c4.5 0 7 5 7 5a13 13 0 0 1-2.2 2.9M9.9 9.9A2 2 0 0 1 6.1 6.1M3 5a13 13 0 0 0-2 3s2.5 5 7 5a7 7 0 0 0 3-.6"/>
                </svg>
              </button>
            </div>
          </div>

          <div v-if="error" class="login-error mono">
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
              <circle cx="8" cy="8" r="6.5"/><path d="M8 5v3.5"/><circle cx="8" cy="11" r="0.6" fill="currentColor"/>
            </svg>
            {{ error }}
          </div>

          <button type="submit" class="btn primary login-submit" :disabled="loading">
            <svg v-if="loading" width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" class="spin">
              <path d="M14 8a6 6 0 1 1-6-6" stroke-linecap="round"/>
            </svg>
            {{ loading ? 'Signing in…' : 'Sign in' }}
            <kbd v-if="!loading" class="submit-kbd">↵</kbd>
          </button>
        </form>

        <div class="login-footer">
          <span class="mono faint">No account?</span>
          <span class="mono dim">Ask an admin to create one</span>
        </div>
      </div>

      <!-- Status pill -->
      <div class="login-status mono">
        <span class="status-dot-live" aria-hidden="true" />
        <span class="faint">api</span>
        <span class="dim">·</span>
        <span class="faint">{{ apiBase }}</span>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const form = ref({ email: '', password: '' })
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

const apiBase = import.meta.env.VITE_API_BASE_URL || '/api/v1'
const reason = computed(() => route.query.reason || null)

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(form.value)
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Sign-in failed — check your credentials'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── Shell ── */
.login-shell {
  position: relative;
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: var(--bg);
  padding: 24px;
  overflow: hidden;
}

/* Grid backdrop — subtle terminal aesthetic, visible in both themes */
.login-backdrop {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(to right, var(--border-strong) 1px, transparent 1px),
    linear-gradient(to bottom, var(--border-strong) 1px, transparent 1px);
  background-size: 40px 40px;
  opacity: 0.5;
  mask-image: radial-gradient(circle at 50% 50%, black 0%, transparent 70%);
  -webkit-mask-image: radial-gradient(circle at 50% 50%, black 0%, transparent 70%);
  pointer-events: none;
}

.login-main {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  width: 100%;
  max-width: 400px;
}

/* ── Brand ── */
.login-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding-bottom: 4px;
}
.brand-text { display: flex; flex-direction: column; gap: 2px; }
.brand-name { font-size: 16px; font-weight: 600; color: var(--text); letter-spacing: 0.01em; }
.brand-tag  { font-size: 10.5px; letter-spacing: 0.04em; }

/* ── Card ── */
.login-card {
  width: 100%;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: cardIn 0.3s ease;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0);   }
}

.login-head { display: flex; flex-direction: column; gap: 6px; }
.login-eyebrow { font-size: 10.5px; letter-spacing: 0.08em; text-transform: uppercase; }
.login-title   { font-size: 20px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }

/* ── Form ── */
.login-form { display: flex; flex-direction: column; gap: 14px; }

.field { display: flex; flex-direction: column; gap: 6px; }
.field-label {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 10.5px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-faint);
}
.field-hint { font-size: 9.5px; color: var(--text-faint); text-transform: none; letter-spacing: 0.02em; }

.login-input { height: 34px; font-size: 13px; font-family: var(--sans); }

.password-wrap { position: relative; display: flex; }
.password-input { padding-right: 36px; flex: 1; }
.password-toggle {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-faint);
  transition: color 0.1s;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: inline-flex;
}
.password-toggle:hover { color: var(--text); }

.login-error {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  background: var(--err-dim);
  border: 1px solid var(--err);
  border-radius: var(--r);
  color: var(--err);
  font-size: 11.5px;
}

.login-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  background: var(--ok-dim);
  border: 1px solid var(--ok);
  border-radius: var(--r);
  color: var(--ok);
  font-size: 11.5px;
}

.login-warn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  background: var(--warn-dim);
  border: 1px solid var(--warn);
  border-radius: var(--r);
  color: var(--warn);
  font-size: 11.5px;
}

.login-submit {
  height: 34px;
  width: 100%;
  justify-content: center;
  font-size: 13px;
  gap: 8px;
  position: relative;
}
.submit-kbd {
  position: absolute;
  right: 10px;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--accent-text);
  opacity: 0.6;
  padding: 1px 5px;
  border: 1px solid currentColor;
  border-radius: 3px;
  line-height: 1;
}
.spin { animation: spin 1s linear infinite; }

/* ── Footer ── */
.login-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--border);
  font-size: 11px;
}
.login-link {
  color: var(--accent);
  text-decoration: none;
  transition: opacity 0.1s;
}
.login-link:hover { opacity: 0.8; }

/* ── Status ── */
.login-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10.5px;
  padding: 4px 8px;
  border-radius: var(--r);
}
.status-dot-live {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--ok);
  animation: pulse-dot 1.4s ease-in-out infinite;
}
</style>
