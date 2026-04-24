<template>
  <div class="page">
    <!-- Header -->
    <div class="page-head">
      <div>
        <div class="page-eyebrow mono faint">account</div>
        <h1 class="page-title">Your account</h1>
        <div class="page-sub mono">
          <span>{{ auth.user?.email }}</span>
          <span class="sep">·</span>
          <span :class="auth.user?.is_active ? 'text-success' : 'text-danger'">
            {{ auth.user?.is_active ? 'active' : 'inactive' }}
          </span>
          <span class="sep">·</span>
          <span class="text-accent">{{ auth.user?.role }}</span>
        </div>
      </div>
    </div>

    <div class="grid">
      <!-- ── Profile panel ── -->
      <Panel title="Profile" subtitle="basic identity">
        <form class="form" @submit.prevent="saveProfile">
          <div class="profile-row">
            <div class="avatar-lg">{{ initials }}</div>
            <div class="profile-meta">
              <div class="profile-name mono">{{ auth.user?.display_name || auth.user?.email }}</div>
              <div class="profile-joined mono faint">
                joined {{ auth.user?.created_at ? formatRelativeTime(auth.user.created_at) : '—' }}
                <span v-if="auth.user?.last_login_at"> · last login {{ formatRelativeTime(auth.user.last_login_at) }}</span>
              </div>
            </div>
          </div>

          <div class="field">
            <label class="field-label mono">Display name</label>
            <input
              v-model="profile.display_name"
              type="text"
              class="input"
              placeholder="How your name appears in the app"
            />
          </div>

          <div class="field">
            <label class="field-label mono">Email</label>
            <input v-model="profile.email" type="email" class="input" required />
          </div>

          <div class="readonly-row">
            <div class="ro-col">
              <div class="ro-label mono faint">Role</div>
              <Chip :variant="roleVariant(auth.user?.role)">{{ auth.user?.role }}</Chip>
            </div>
            <div class="ro-col">
              <div class="ro-label mono faint">Status</div>
              <Chip :variant="auth.user?.is_active ? 'ok' : null">
                {{ auth.user?.is_active ? 'active' : 'inactive' }}
              </Chip>
            </div>
            <div class="ro-col">
              <div class="ro-label mono faint">User ID</div>
              <span class="mono" style="font-size:11px; color:var(--text-dim)">
                {{ (auth.user?.id || '').slice(0, 8) }}…
              </span>
            </div>
          </div>

          <p class="field-note mono faint">Role and status are managed by an administrator.</p>

          <div v-if="profileMsg" class="form-ok mono">
            <CircleCheck :size="12" :stroke-width="1.75" /> {{ profileMsg }}
          </div>
          <div v-if="profileError" class="form-error mono">
            <CircleAlert :size="12" :stroke-width="1.75" /> {{ profileError }}
          </div>

          <div class="form-actions">
            <button type="submit" class="btn primary" :disabled="profileBusy || !profileDirty">
              {{ profileBusy ? 'Saving…' : 'Save profile' }}
            </button>
          </div>
        </form>
      </Panel>

      <!-- ── Password panel ── -->
      <Panel title="Password" subtitle="change your sign-in password">
        <form class="form" @submit.prevent="savePassword">
          <div class="field">
            <label class="field-label mono">
              <span>New password</span>
              <span class="field-hint mono">min 8 chars</span>
            </label>
            <input
              v-model="passwordForm.password"
              type="password"
              class="input"
              autocomplete="new-password"
              minlength="8"
              required
              placeholder="••••••••"
            />
          </div>

          <div class="field">
            <label class="field-label mono">Confirm password</label>
            <input
              v-model="passwordForm.confirm"
              type="password"
              class="input"
              autocomplete="new-password"
              minlength="8"
              required
              placeholder="••••••••"
            />
          </div>

          <div v-if="passwordMsg" class="form-ok mono">
            <CircleCheck :size="12" :stroke-width="1.75" /> {{ passwordMsg }}
          </div>
          <div v-if="passwordError" class="form-error mono">
            <CircleAlert :size="12" :stroke-width="1.75" /> {{ passwordError }}
          </div>

          <div class="form-actions">
            <button type="submit" class="btn primary" :disabled="passwordBusy">
              {{ passwordBusy ? 'Updating…' : 'Update password' }}
            </button>
          </div>
        </form>
      </Panel>

      <!-- ── Session panel ── -->
      <Panel title="Session" subtitle="sign out and manage devices">
        <div class="session-row">
          <div>
            <div class="mono" style="font-size:12px; color:var(--text)">This device</div>
            <div class="mono faint" style="font-size:10.5px">
              API · {{ apiBase }}<span v-if="auth.user?.last_login_at"> · last login {{ formatRelativeTime(auth.user.last_login_at) }}</span>
            </div>
          </div>
          <button class="btn ghost danger" @click="handleSignOut">
            <LogOut :size="12" :stroke-width="1.75" />
            Sign out
          </button>
        </div>
      </Panel>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { CircleCheck, CircleAlert, LogOut } from 'lucide-vue-next'

import { useAuthStore } from '@/stores/auth'
import { userService } from '@/services/userService'
import { formatRelativeTime } from '@/utils/format'

import Panel from '@/components/ui/Panel.vue'
import Chip from '@/components/ui/Chip.vue'

const auth = useAuthStore()

const profile = ref({ display_name: '', email: '' })
const profileBusy = ref(false)
const profileError = ref('')
const profileMsg = ref('')

const passwordForm = ref({ password: '', confirm: '' })
const passwordBusy = ref(false)
const passwordError = ref('')
const passwordMsg = ref('')

const apiBase = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const initials = computed(() => {
  const src = auth.user?.display_name || auth.user?.email || ''
  return src.split(/[\s@]/).map(s => s[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() || '?'
})

const profileDirty = computed(() => {
  if (!auth.user) return false
  return (
    profile.value.display_name !== (auth.user.display_name || '') ||
    profile.value.email !== auth.user.email
  )
})

function roleVariant(role) {
  return { admin: 'accent', evaluator: 'info', viewer: null }[role] ?? null
}

function hydrate() {
  profile.value = {
    display_name: auth.user?.display_name || '',
    email: auth.user?.email || '',
  }
}

async function saveProfile() {
  if (!auth.user) return
  profileBusy.value = true
  profileError.value = ''
  profileMsg.value = ''
  try {
    const payload = {
      email: profile.value.email,
      display_name: profile.value.display_name || null,
    }
    await userService.update(auth.user.id, payload)
    await auth.fetchMe()
    hydrate()
    profileMsg.value = 'Profile updated'
  } catch (e) {
    profileError.value = e?.response?.data?.detail || e?.message || 'Update failed'
  } finally {
    profileBusy.value = false
  }
}

async function savePassword() {
  if (!auth.user) return
  passwordError.value = ''
  passwordMsg.value = ''
  if (passwordForm.value.password !== passwordForm.value.confirm) {
    passwordError.value = 'Passwords do not match'
    return
  }
  passwordBusy.value = true
  try {
    await userService.update(auth.user.id, { password: passwordForm.value.password })
    passwordForm.value = { password: '', confirm: '' }
    passwordMsg.value = 'Password updated'
  } catch (e) {
    passwordError.value = e?.response?.data?.detail || e?.message || 'Update failed'
  } finally {
    passwordBusy.value = false
  }
}

async function handleSignOut() {
  await auth.logout()
}

onMounted(() => {
  if (auth.user) hydrate()
})
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 14px; }

.page-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; padding: 2px 2px 6px; flex-wrap: wrap; }
.page-eyebrow { font-size: 10.5px; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }
.page-title { font-size: 22px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }
.page-sub { font-size: 11.5px; color: var(--text-dim); display: flex; gap: 6px; align-items: center; margin-top: 2px; }
.page-sub .sep { color: var(--text-faint); }

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
.grid > :last-child { grid-column: 1 / -1; }
@media (max-width: 900px) { .grid { grid-template-columns: 1fr; } .grid > :last-child { grid-column: auto; } }

.form { display: flex; flex-direction: column; gap: 14px; }

.profile-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 6px 0 2px;
}
.avatar-lg {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--accent-dim);
  color: var(--accent);
  font-size: 18px;
  font-weight: 700;
  font-family: var(--mono);
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.profile-meta { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.profile-name { font-size: 14px; color: var(--text); }
.profile-joined { font-size: 11px; }

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
.field-note { font-size: 10.5px; color: var(--text-faint); }

.readonly-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 10px;
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: var(--r);
}
.ro-col { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.ro-label { font-size: 9.5px; letter-spacing: 0.06em; text-transform: uppercase; }

.form-ok, .form-error {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border-radius: var(--r);
  font-size: 11.5px;
  border: 1px solid;
}
.form-ok    { background: var(--ok-dim);  border-color: var(--ok);  color: var(--ok); }
.form-error { background: var(--err-dim); border-color: var(--err); color: var(--err); }

.form-actions { display: flex; justify-content: flex-end; gap: 6px; }

.session-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
}
.btn.ghost.danger { color: var(--err); }
.btn.ghost.danger:hover { background: var(--err-dim); color: var(--err); }
</style>
