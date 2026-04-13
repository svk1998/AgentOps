<template>
  <div class="users-page">
    <div class="page-header">
      <h2>User Management</h2>
      <button class="btn-primary" @click="showCreateModal = true">+ Add User</button>
    </div>

    <!-- Filters -->
    <div class="filters">
      <input
        v-model="search"
        type="text"
        placeholder="Search users..."
        class="search-input"
      />
    </div>

    <!-- Table -->
    <div class="card">
      <p v-if="loading" class="muted">Loading users...</p>
      <p v-else-if="error" class="danger">{{ error }}</p>

      <table v-else class="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in userStore.users" :key="user.id">
            <td>{{ user.firstName }} {{ user.lastName }}</td>
            <td>{{ user.email }}</td>
            <td><span class="badge" :class="user.role">{{ user.role }}</span></td>
            <td class="actions">
              <button class="btn-sm" @click="editUser(user)">Edit</button>
              <button
                class="btn-sm danger"
                :disabled="deleteLoading"
                @click="handleDelete(user.id)"
              >
                Delete
              </button>
            </td>
          </tr>
          <tr v-if="userStore.users.length === 0">
            <td colspan="4" class="empty">No users found.</td>
          </tr>
        </tbody>
      </table>

      <p class="table-footer">Total: {{ userStore.total }} users</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useAsync } from '@/composables/useAsync'
import { useToast } from '@/composables/useToast'

const userStore = useUserStore()
const toast     = useToast()

const search          = ref('')
const showCreateModal = ref(false)
const loading         = ref(false)
const error           = ref(null)

const { execute: handleDelete, loading: deleteLoading } = useAsync(async (id) => {
  await userStore.deleteUser(id)
  toast.success('User deleted successfully')
})

onMounted(async () => {
  loading.value = true
  try {
    await userStore.loadUsers()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})

function editUser(user) {
  // Open edit modal — extend as needed
  console.log('Edit user:', user)
}
</script>

<style scoped>
.users-page { display: flex; flex-direction: column; gap: 1.25rem; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.page-header h2 { font-size: 1.1rem; font-weight: 600; }

.filters { display: flex; gap: 0.75rem; }
.search-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 0.9rem;
  width: 280px;
  outline: none;
}
.search-input:focus { border-color: var(--color-primary); }

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  overflow: hidden;
}

.table { width: 100%; border-collapse: collapse; }
.table th, .table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.9rem;
}
.table th { background: #f8fafc; font-weight: 600; font-size: 0.8rem; color: var(--color-text-muted); text-transform: uppercase; }
.table tbody tr:hover { background: #f8fafc; }

.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 600;
  background: #e2e8f0;
  color: #475569;
}
.badge.admin { background: #dbeafe; color: #1d4ed8; }

.actions { display: flex; gap: 0.5rem; }

.btn-sm {
  padding: 0.3rem 0.65rem;
  font-size: 0.8rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: white;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-sm:hover { background: #f1f5f9; }
.btn-sm.danger { color: var(--color-danger); border-color: #fecaca; }
.btn-sm.danger:hover { background: #fef2f2; }
.btn-sm:disabled { opacity: 0.5; cursor: not-allowed; }

.table-footer { padding: 0.75rem 1rem; font-size: 0.8rem; color: var(--color-text-muted); }
.empty { text-align: center; color: var(--color-text-muted); padding: 2rem !important; }
.muted  { padding: 1rem; color: var(--color-text-muted); font-size: 0.9rem; }
.danger { padding: 1rem; color: var(--color-danger); font-size: 0.9rem; }

.btn-primary {
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-primary:hover { background: var(--color-primary-hover); }
</style>
