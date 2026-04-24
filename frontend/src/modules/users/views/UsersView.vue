<template>
  <div class="page">
    <!-- Header -->
    <div class="page-head">
      <div>
        <div class="page-eyebrow mono faint">admin</div>
        <h1 class="page-title">Users</h1>
        <div class="page-sub mono">
          <span>{{ users.length }} user{{ users.length === 1 ? '' : 's' }}</span>
          <span class="sep">·</span>
          <span class="text-success">{{ counts.active }} active</span>
          <span class="sep">·</span>
          <span class="text-muted">{{ counts.inactive }} inactive</span>
          <span class="sep">·</span>
          <span class="text-accent">{{ counts.admin }} admin</span>
        </div>
      </div>
      <div class="page-actions">
        <div class="search-wrap">
          <Search :size="12" :stroke-width="1.6" class="search-icon" />
          <input v-model="search" class="input search-input" placeholder="Search users…" />
        </div>
        <select v-model="filters.role" class="input">
          <option value="">All roles</option>
          <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
        </select>
        <select v-model="filters.is_active" class="input">
          <option value="">Any status</option>
          <option value="true">Active only</option>
          <option value="false">Inactive only</option>
        </select>
        <button class="btn ghost" :disabled="loading" @click="load">
          <RefreshCw :size="12" :stroke-width="1.75" :class="loading ? 'spin' : ''" />
          Refresh
        </button>
        <button class="btn primary" @click="openCreate">
          <Plus :size="12" :stroke-width="2" />
          New user
        </button>
      </div>
    </div>

    <!-- Table -->
    <Panel :padding="false">
      <DataTable
        :columns="cols"
        :rows="filtered"
        :on-row-click="openEdit"
        :empty-text="search ? `no users match “${search}”` : 'no users found'"
      >
        <template #cell-status="{ row }">
          <div class="cell-status">
            <StatusDot :status="row.is_active ? 'ok' : 'pending'" />
            <span class="mono faint" style="font-size:11px">{{ row.is_active ? 'active' : 'inactive' }}</span>
          </div>
        </template>
        <template #cell-display_name="{ row }">
          <div class="cell-name">
            <div class="user-avatar">{{ initials(row) }}</div>
            <div class="cell-name-text">
              <span class="mono" style="color:var(--text)">{{ row.display_name || row.email.split('@')[0] }}</span>
              <span v-if="row.id === auth.user?.id" class="mono faint self-tag">you</span>
            </div>
          </div>
        </template>
        <template #cell-email="{ value }">
          <span class="mono faint" style="font-size:11.5px">{{ value }}</span>
        </template>
        <template #cell-role="{ value }">
          <Chip :variant="roleVariant(value)">{{ value }}</Chip>
        </template>
        <template #cell-last_login_at="{ value }">
          <span v-if="value" class="mono faint" style="font-size:11px" :title="formatDateTime(value)">
            {{ formatRelativeTime(value) }}
          </span>
          <span v-else class="mono" style="color:var(--text-faint); font-size:11px">never</span>
        </template>
        <template #cell-created_at="{ value }">
          <span class="mono faint" style="font-size:11px" :title="formatDateTime(value)">
            {{ formatRelativeTime(value) }}
          </span>
        </template>
        <template #cell-actions="{ row }">
          <div class="row-actions" @click.stop>
            <button class="btn ghost row-btn" @click="openEdit(row)">Edit</button>
            <button
              v-if="row.is_active && row.id !== auth.user?.id"
              class="btn ghost row-btn danger"
              @click="confirmDeactivate(row)"
            >Deactivate</button>
            <button
              v-else-if="!row.is_active"
              class="btn ghost row-btn success"
              @click="reactivate(row)"
            >Reactivate</button>
          </div>
        </template>
      </DataTable>
    </Panel>

    <div v-if="error" class="error-banner mono">{{ error }}</div>

    <!-- ── Modal: Create / Edit ── -->
    <Teleport to="body">
      <div v-if="modalOpen" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card" role="dialog" aria-modal="true">
          <div class="modal-head">
            <div>
              <div class="page-eyebrow mono faint">{{ editing ? 'edit user' : 'new user' }}</div>
              <h2 class="modal-title">{{ editing ? (editing.display_name || editing.email) : 'Create user' }}</h2>
            </div>
            <button class="btn ghost icon-btn" aria-label="Close" @click="closeModal">
              <X :size="13" :stroke-width="1.75" />
            </button>
          </div>

          <form class="modal-form" @submit.prevent="submitForm">
            <div class="field">
              <label class="field-label mono">Email</label>
              <input v-model="form.email" type="email" class="input" required autofocus />
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
              <div v-if="editing" class="field">
                <label class="field-label mono">Status</label>
                <select v-model="form.is_active" class="input">
                  <option :value="true">active</option>
                  <option :value="false">inactive</option>
                </select>
              </div>
            </div>

            <div class="field">
              <label class="field-label mono">
                <span>{{ editing ? 'Reset password' : 'Password' }}</span>
                <span class="field-hint mono">{{ editing ? 'leave blank to keep current' : 'min 8 chars' }}</span>
              </label>
              <input
                v-model="form.password"
                type="password"
                class="input"
                :required="!editing"
                :minlength="!editing ? 8 : undefined"
                placeholder="••••••••"
              />
            </div>

            <div v-if="modalError" class="form-error mono">
              <CircleAlert :size="12" :stroke-width="1.75" />
              {{ modalError }}
            </div>

            <div class="modal-actions">
              <button type="button" class="btn ghost" :disabled="submitting" @click="closeModal">Cancel</button>
              <button type="submit" class="btn primary" :disabled="submitting">
                {{ submitting ? (editing ? 'Saving…' : 'Creating…') : (editing ? 'Save changes' : 'Create user') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Search, RefreshCw, Plus, X, CircleAlert } from 'lucide-vue-next'

import { userService } from '@/services/userService'
import { useAuthStore } from '@/stores/auth'
import { useApi } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import { formatRelativeTime, formatDateTime } from '@/utils/format'
import { USER_ROLES, USER_ROLE_CHIP } from '@/constants/enums'

import Panel from '@/components/ui/Panel.vue'
import Chip from '@/components/ui/Chip.vue'
import StatusDot from '@/components/ui/StatusDot.vue'
import DataTable from '@/components/ui/DataTable.vue'

const ROLES = USER_ROLES

const auth = useAuthStore()
const toast = useToast()
const search = ref('')
const filters = ref({ role: '', is_active: '' })

// Standard data-fetching pattern — see src/composables/useApi.js
const { data: users, error, loading, refetch: load } = useApi(
  () => userService.list(buildParams(filters.value)),
  { initialData: [], watchDeps: [() => filters.value.role, () => filters.value.is_active] },
)

function buildParams(f) {
  const p = {}
  if (f.role) p.role = f.role
  if (f.is_active !== '') p.is_active = f.is_active
  return p
}

// ── Modal state ──
const modalOpen = ref(false)
const editing = ref(null)
const form = ref(newForm())
const modalError = ref('')
const submitting = ref(false)

function newForm() {
  return { email: '', display_name: '', role: 'viewer', is_active: true, password: '' }
}

const cols = [
  { key: 'status',         label: 'Status',     width: '120px' },
  { key: 'display_name',   label: 'Name',       width: '1.5fr' },
  { key: 'email',          label: 'Email',      width: '1.8fr' },
  { key: 'role',           label: 'Role',       width: '110px' },
  { key: 'last_login_at',  label: 'Last login', width: '110px', align: 'right' },
  { key: 'created_at',     label: 'Joined',     width: '100px', align: 'right' },
  { key: 'actions',        label: '',           width: '200px', align: 'right' },
]

const filtered = computed(() => {
  const list = users.value || []
  const q = search.value.trim().toLowerCase()
  if (!q) return list
  return list.filter(u =>
    u.email?.toLowerCase().includes(q) ||
    u.display_name?.toLowerCase().includes(q),
  )
})

const counts = computed(() => {
  const c = { active: 0, inactive: 0, admin: 0, evaluator: 0, viewer: 0 }
  for (const u of (users.value || [])) {
    c[u.is_active ? 'active' : 'inactive']++
    c[u.role] = (c[u.role] || 0) + 1
  }
  return c
})

function initials(u) {
  const src = u.display_name || u.email || ''
  return src.split(/[\s@]/).map(s => s[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() || '?'
}

function roleVariant(role) {
  return USER_ROLE_CHIP[role] ?? null
}

// Surface any load errors in a toast (the error banner stays for detail)
watch(error, (e) => { if (e) toast.error(e) })

function openCreate() {
  editing.value = null
  form.value = newForm()
  modalError.value = ''
  modalOpen.value = true
}

function openEdit(u) {
  editing.value = u
  form.value = {
    email: u.email,
    display_name: u.display_name || '',
    role: u.role,
    is_active: u.is_active,
    password: '',
  }
  modalError.value = ''
  modalOpen.value = true
}

function closeModal() {
  if (submitting.value) return
  modalOpen.value = false
  editing.value = null
  form.value = newForm()
  modalError.value = ''
}

async function submitForm() {
  submitting.value = true
  modalError.value = ''
  try {
    if (editing.value) {
      const payload = {
        email: form.value.email,
        display_name: form.value.display_name || null,
        role: form.value.role,
        is_active: form.value.is_active,
      }
      if (form.value.password) payload.password = form.value.password
      await userService.update(editing.value.id, payload)
      toast.success(`Updated ${form.value.email}`)
    } else {
      await userService.create({
        email: form.value.email,
        password: form.value.password,
        display_name: form.value.display_name || null,
        role: form.value.role,
      })
      toast.success(`Created ${form.value.email}`)
    }
    closeModal()
    await load()
  } catch (e) {
    modalError.value = e?.response?.data?.detail || e?.message || 'Save failed'
  } finally {
    submitting.value = false
  }
}

async function confirmDeactivate(u) {
  if (!confirm(`Deactivate ${u.display_name || u.email}? They will no longer be able to sign in.`)) return
  try {
    await userService.remove(u.id)
    toast.success(`Deactivated ${u.display_name || u.email}`)
    await load()
  } catch (e) {
    toast.error(e?.response?.data?.detail || e?.message || 'Deactivate failed')
  }
}

async function reactivate(u) {
  try {
    await userService.reactivate(u.id)
    toast.success(`Reactivated ${u.display_name || u.email}`)
    await load()
  } catch (e) {
    toast.error(e?.response?.data?.detail || e?.message || 'Reactivate failed')
  }
}
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 14px; }

.page-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; padding: 2px 2px 6px; flex-wrap: wrap; }
.page-eyebrow { font-size: 10.5px; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }
.page-title { font-size: 22px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }
.page-sub { font-size: 11.5px; color: var(--text-dim); display: flex; gap: 6px; align-items: center; margin-top: 2px; }
.page-sub .sep { color: var(--text-faint); }

.page-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

.search-wrap { position: relative; display: flex; align-items: center; }
.search-icon { position: absolute; left: 10px; color: var(--text-faint); pointer-events: none; }
.search-input { padding-left: 28px; min-width: 200px; }

select.input { cursor: pointer; }

.cell-status { display: flex; align-items: center; gap: 8px; }
.cell-name { display: inline-flex; align-items: center; gap: 10px; }
.cell-name-text { display: inline-flex; align-items: baseline; gap: 6px; }
.self-tag {
  font-size: 9.5px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 1px 5px;
  border: 1px solid var(--border);
  border-radius: 3px;
  color: var(--text-faint);
}

.user-avatar {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--accent-dim);
  color: var(--accent);
  font-size: 9.5px;
  font-weight: 700;
  font-family: var(--mono);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.row-actions { display: flex; gap: 4px; justify-content: flex-end; }
.row-btn { height: 24px; font-size: 11px; padding: 0 8px; }
.btn.ghost.danger { color: var(--err); }
.btn.ghost.danger:hover { background: var(--err-dim); color: var(--err); }
.btn.ghost.success { color: var(--ok); }
.btn.ghost.success:hover { background: var(--ok-dim); color: var(--ok); }

.error-banner {
  background: var(--err-dim);
  color: var(--err);
  border: 1px solid var(--err);
  border-radius: var(--r);
  padding: 10px 14px;
  font-size: 12px;
}

.spin { animation: spin 1s linear infinite; }

/* ── Modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(2px);
  display: grid;
  place-items: center;
  z-index: 1000;
  padding: 20px;
  animation: overlayIn 0.15s ease;
}
@keyframes overlayIn { from { opacity: 0; } to { opacity: 1; } }

.modal-card {
  width: 100%;
  max-width: 460px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  animation: cardIn 0.2s ease;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0);   }
}

.modal-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.modal-title { font-size: 18px; font-weight: 600; letter-spacing: -0.01em; color: var(--text); }
.icon-btn { width: 26px; height: 26px; padding: 0; justify-content: center; }

.modal-form { display: flex; flex-direction: column; gap: 14px; }
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

.form-error {
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

.modal-actions { display: flex; justify-content: flex-end; gap: 6px; }
</style>
