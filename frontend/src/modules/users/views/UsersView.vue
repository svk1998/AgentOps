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
          <svg class="search-icon" width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round">
            <circle cx="7" cy="7" r="4.5" /><path d="M10.5 10.5L14 14" />
          </svg>
          <input v-model="search" class="input search-input" placeholder="Search users…" />
        </div>
        <select v-model="filters.role" class="input">
          <option value="">All roles</option>
          <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
        </select>
        <button class="btn ghost" :disabled="loading" @click="load">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" :class="loading ? 'spin' : ''"><path d="M14 8a6 6 0 1 1-6-6c1.9 0 3.6 0.9 4.7 2.3"/><path d="M14 2v3h-3"/></svg>
          Refresh
        </button>
        <button class="btn primary" @click="openCreate">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M8 3v10M3 8h10"/></svg>
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
            <span class="mono" style="color:var(--text)">{{ row.display_name || row.email.split('@')[0] }}</span>
          </div>
        </template>
        <template #cell-email="{ value }">
          <span class="mono faint" style="font-size:11.5px">{{ value }}</span>
        </template>
        <template #cell-role="{ value }">
          <Chip :variant="roleVariant(value)">{{ value }}</Chip>
        </template>
        <template #cell-actions="{ row }">
          <div class="row-actions" @click.stop>
            <button class="btn ghost" style="height:24px; font-size:11px" @click="openEdit(row)">Edit</button>
            <button
              v-if="row.id !== auth.user?.id"
              class="btn ghost danger"
              style="height:24px; font-size:11px"
              :disabled="!row.is_active"
              @click="confirmDeactivate(row)"
            >
              {{ row.is_active ? 'Deactivate' : 'Inactive' }}
            </button>
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
              <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M4 4l8 8M12 4l-8 8"/></svg>
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
              <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                <circle cx="8" cy="8" r="6.5"/><path d="M8 5v3.5"/><circle cx="8" cy="11" r="0.6" fill="currentColor"/>
              </svg>
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
import { ref, computed, onMounted } from 'vue'
import { userService } from '@/services/userService'
import { useAuthStore } from '@/stores/auth'

import Panel from '@/components/primitives/Panel.vue'
import Chip from '@/components/primitives/Chip.vue'
import StatusDot from '@/components/primitives/StatusDot.vue'
import DataTable from '@/components/primitives/DataTable.vue'

const ROLES = ['admin', 'evaluator', 'viewer']

const auth = useAuthStore()
const users = ref([])
const loading = ref(false)
const error = ref('')
const search = ref('')
const filters = ref({ role: '' })

// ── Modal state ──
const modalOpen = ref(false)
const editing = ref(null) // user being edited; null for create
const form = ref(newForm())
const modalError = ref('')
const submitting = ref(false)

function newForm() {
  return { email: '', display_name: '', role: 'viewer', is_active: true, password: '' }
}

const cols = [
  { key: 'status',       label: 'Status', width: '120px' },
  { key: 'display_name', label: 'Name',   width: '2fr' },
  { key: 'email',        label: 'Email',  width: '2fr' },
  { key: 'role',         label: 'Role',   width: '120px' },
  { key: 'actions',      label: '',       width: '180px', align: 'right' },
]

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter(u =>
    u.email?.toLowerCase().includes(q) ||
    u.display_name?.toLowerCase().includes(q),
  )
})

const counts = computed(() => {
  const c = { active: 0, inactive: 0, admin: 0, evaluator: 0, viewer: 0 }
  for (const u of users.value) {
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
  return { admin: 'accent', evaluator: 'info', viewer: null }[role]
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.value.role) params.role = filters.value.role
    const { data } = await userService.list(params)
    users.value = Array.isArray(data) ? data : (data?.items ?? [])
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load users'
    users.value = []
  } finally {
    loading.value = false
  }
}

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
    } else {
      await userService.create({
        email: form.value.email,
        password: form.value.password,
        display_name: form.value.display_name || null,
        role: form.value.role,
      })
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
    await load()
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Deactivate failed'
  }
}

onMounted(load)
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
.btn.ghost.danger { color: var(--err); }
.btn.ghost.danger:hover { background: var(--err-dim); color: var(--err); }

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
