<template>
  <div v-if="loading && !user" class="page">
    <div class="loading mono faint">Loading…</div>
  </div>

  <div v-else-if="!user" class="page">
    <Panel :padding="false">
      <div class="empty-state">
        <CircleAlert :size="24" :stroke-width="1.5" style="color: var(--err); opacity: 0.8" />
        <p class="empty-title">User not found</p>
        <p class="empty-sub mono">{{ error || 'This user does not exist or you do not have permission to view them.' }}</p>
        <RouterLink to="/users" class="btn ghost" style="margin-top: 8px">
          <ArrowLeft :size="12" :stroke-width="1.75" /> Back to users
        </RouterLink>
      </div>
    </Panel>
  </div>

  <div v-else class="page">
    <!-- Header with back link -->
    <div class="page-head">
      <div>
        <RouterLink to="/users" class="back-link mono">
          <ArrowLeft :size="11" :stroke-width="1.75" /> users
        </RouterLink>
        <div class="page-title-row">
          <div class="user-avatar-lg">{{ initials }}</div>
          <div>
            <h1 class="page-title">{{ user.display_name || user.email }}</h1>
            <div class="page-sub mono">
              <StatusDot :status="user.is_active ? 'ok' : 'pending'" />
              <span :class="user.is_active ? 'text-success' : 'text-muted'">
                {{ user.is_active ? 'active' : 'inactive' }}
              </span>
              <span class="sep">·</span>
              <Chip :variant="roleVariant(user.role)">{{ user.role }}</Chip>
              <span class="sep">·</span>
              <span>joined {{ formatRelativeTime(user.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="page-actions">
        <button
          v-if="user.is_active && user.id !== auth.user?.id"
          class="btn ghost danger"
          @click="confirmDeactivate"
        >
          <UserX :size="12" :stroke-width="1.75" /> Deactivate
        </button>
        <button
          v-else-if="!user.is_active"
          class="btn ghost success"
          @click="handleReactivate"
        >
          <UserCheck :size="12" :stroke-width="1.75" /> Reactivate
        </button>
      </div>
    </div>

    <div class="grid">
      <!-- Profile edit -->
      <Panel title="Profile" subtitle="identity and access">
        <form class="form" @submit.prevent="saveProfile">
          <div class="field">
            <label class="field-label mono">Email</label>
            <input v-model="form.email" type="email" class="input" required />
          </div>

          <div class="field">
            <label class="field-label mono">Display name</label>
            <input v-model="form.display_name" type="text" class="input" placeholder="e.g. Jane Doe" />
          </div>

          <div class="grid-2">
            <div class="field">
              <label class="field-label mono">Role</label>
              <select v-model="form.role" class="input">
                <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label mono">Status</label>
              <select v-model="form.is_active" class="input">
                <option :value="true">active</option>
                <option :value="false">inactive</option>
              </select>
            </div>
          </div>

          <div v-if="profileMsg" class="form-ok mono">
            <CircleCheck :size="12" :stroke-width="1.75" /> {{ profileMsg }}
          </div>
          <div v-if="profileError" class="form-error mono">
            <CircleAlert :size="12" :stroke-width="1.75" /> {{ profileError }}
          </div>

          <div class="form-actions">
            <button type="submit" class="btn primary" :disabled="profileBusy">
              {{ profileBusy ? 'Saving…' : 'Save changes' }}
            </button>
          </div>
        </form>
      </Panel>

      <!-- Password reset -->
      <Panel title="Password" subtitle="admin password reset">
        <form class="form" @submit.prevent="savePassword">
          <div class="field">
            <label class="field-label mono">
              <span>New password</span>
              <span class="field-hint mono">min 8 chars · sent manually to user</span>
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

          <div v-if="passwordMsg" class="form-ok mono">
            <CircleCheck :size="12" :stroke-width="1.75" /> {{ passwordMsg }}
          </div>
          <div v-if="passwordError" class="form-error mono">
            <CircleAlert :size="12" :stroke-width="1.75" /> {{ passwordError }}
          </div>

          <div class="form-actions">
            <button type="submit" class="btn primary" :disabled="passwordBusy">
              {{ passwordBusy ? 'Resetting…' : 'Reset password' }}
            </button>
          </div>
        </form>
      </Panel>

      <!-- Metadata -->
      <Panel title="Metadata" subtitle="read-only system fields">
        <div class="meta-grid">
          <div class="meta-item">
            <div class="meta-label mono faint">User ID</div>
            <div class="meta-value mono" style="font-size:11px">{{ user.id }}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label mono faint">Created</div>
            <div class="meta-value mono" :title="formatDateTime(user.created_at)">
              {{ formatDateTime(user.created_at) }}
            </div>
          </div>
          <div class="meta-item">
            <div class="meta-label mono faint">Last updated</div>
            <div class="meta-value mono" :title="formatDateTime(user.updated_at)">
              {{ formatRelativeTime(user.updated_at) }}
            </div>
          </div>
          <div class="meta-item">
            <div class="meta-label mono faint">Last login</div>
            <div class="meta-value mono">
              <span v-if="user.last_login_at" :title="formatDateTime(user.last_login_at)">
                {{ formatRelativeTime(user.last_login_at) }}
              </span>
              <span v-else class="text-subtle">never</span>
            </div>
          </div>
        </div>
      </Panel>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { ArrowLeft, CircleCheck, CircleAlert, UserX, UserCheck } from 'lucide-vue-next'

import { userService } from '@/services/userService'
import { useAuthStore } from '@/stores/auth'
import { formatRelativeTime, formatDateTime } from '@/utils/format'

import Panel from '@/components/ui/Panel.vue'
import Chip from '@/components/ui/Chip.vue'
import StatusDot from '@/components/ui/StatusDot.vue'

const ROLES = ['admin', 'evaluator', 'viewer']

const route = useRoute()
const auth = useAuthStore()

const user = ref(null)
const loading = ref(false)
const error = ref('')

const form = ref({ email: '', display_name: '', role: 'viewer', is_active: true })
const profileBusy = ref(false)
const profileError = ref('')
const profileMsg = ref('')

const passwordForm = ref({ password: '' })
const passwordBusy = ref(false)
const passwordError = ref('')
const passwordMsg = ref('')

const initials = computed(() => {
  if (!user.value) return '?'
  const src = user.value.display_name || user.value.email
  return src.split(/[\s@]/).map(s => s[0]).filter(Boolean).slice(0, 2).join('').toUpperCase()
})

function roleVariant(role) {
  return { admin: 'accent', evaluator: 'info', viewer: null }[role] ?? null
}

function hydrate(u) {
  form.value = {
    email: u.email,
    display_name: u.display_name || '',
    role: u.role,
    is_active: u.is_active,
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await userService.get(route.params.id)
    user.value = data
    hydrate(data)
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load user'
    user.value = null
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  if (!user.value) return
  profileBusy.value = true
  profileError.value = ''
  profileMsg.value = ''
  try {
    const { data } = await userService.update(user.value.id, {
      email: form.value.email,
      display_name: form.value.display_name || null,
      role: form.value.role,
      is_active: form.value.is_active,
    })
    user.value = data
    hydrate(data)
    profileMsg.value = 'Saved'
  } catch (e) {
    profileError.value = e?.response?.data?.detail || e?.message || 'Save failed'
  } finally {
    profileBusy.value = false
  }
}

async function savePassword() {
  if (!user.value) return
  passwordBusy.value = true
  passwordError.value = ''
  passwordMsg.value = ''
  try {
    await userService.update(user.value.id, { password: passwordForm.value.password })
    passwordForm.value = { password: '' }
    passwordMsg.value = 'Password updated'
  } catch (e) {
    passwordError.value = e?.response?.data?.detail || e?.message || 'Update failed'
  } finally {
    passwordBusy.value = false
  }
}

async function confirmDeactivate() {
  if (!user.value) return
  if (!confirm(`Deactivate ${user.value.display_name || user.value.email}?`)) return
  try {
    await userService.remove(user.value.id)
    await load()
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Deactivate failed'
  }
}

async function handleReactivate() {
  if (!user.value) return
  try {
    const { data } = await userService.reactivate(user.value.id)
    user.value = data
    hydrate(data)
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Reactivate failed'
  }
}

watch(() => route.params.id, (id) => { if (id) load() })
onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 14px; }

.page-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding: 2px 2px 6px; flex-wrap: wrap; }
.page-actions { display: flex; align-items: center; gap: 8px; }

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10.5px;
  color: var(--text-faint);
  text-decoration: none;
  margin-bottom: 10px;
  transition: color 0.1s;
}
.back-link:hover { color: var(--text); }

.page-title-row { display: flex; align-items: center; gap: 14px; }
.page-title { font-size: 22px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }
.page-sub {
  font-size: 11.5px;
  color: var(--text-dim);
  display: flex;
  gap: 6px;
  align-items: center;
  margin-top: 4px;
}
.page-sub .sep { color: var(--text-faint); }

.user-avatar-lg {
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

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
.grid > :last-child { grid-column: 1 / -1; }
@media (max-width: 900px) { .grid { grid-template-columns: 1fr; } .grid > :last-child { grid-column: auto; } }

.form { display: flex; flex-direction: column; gap: 14px; }
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

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

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

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.meta-item { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.meta-label { font-size: 9.5px; letter-spacing: 0.06em; text-transform: uppercase; }
.meta-value { font-size: 11.5px; color: var(--text); word-break: break-all; }

.btn.ghost.danger { color: var(--err); }
.btn.ghost.danger:hover { background: var(--err-dim); color: var(--err); }
.btn.ghost.success { color: var(--ok); }
.btn.ghost.success:hover { background: var(--ok-dim); color: var(--ok); }

.loading { padding: 40px; text-align: center; font-size: 12px; }

.empty-state {
  padding: 60px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.empty-title { font-size: 14px; font-weight: 500; color: var(--text-dim); }
.empty-sub { font-size: 11px; color: var(--text-faint); }
</style>
