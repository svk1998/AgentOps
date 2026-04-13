<template>
  <div class="app-shell">
    <!-- ── Sidebar ──────────────────────────────────────────────────── -->
    <aside class="sidebar" :class="{ 'sidebar--collapsed': collapsed }">
      <!-- Brand -->
      <div class="sidebar-brand">
        <RouterLink to="/dashboard" class="brand-link">
          <img src="/logo.svg" alt="AgentOps" class="brand-logo" />
          <span v-show="!collapsed" class="brand-name">
            Agent<span class="brand-accent">Ops</span>
          </span>
        </RouterLink>
        <button
          class="collapse-btn"
          :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
          @click="collapsed = !collapsed"
        >
          <i :class="['pi', collapsed ? 'pi-angle-right' : 'pi-angle-left']" />
        </button>
      </div>

      <!-- Nav -->
      <nav class="sidebar-nav">
        <div v-for="section in navSections" :key="section.label" class="nav-section">
          <p v-show="!collapsed" class="nav-section-label">{{ section.label }}</p>
          <RouterLink
            v-for="item in section.items"
            :key="item.to || item.label"
            v-tooltip.right="collapsed ? item.label : null"
            :to="item.to"
            :class="['nav-item', { 'nav-item--disabled': item.disabled }]"
            active-class="nav-item--active"
            @click="item.disabled && $event.preventDefault()"
          >
            <i :class="['nav-icon pi', item.icon]" />
            <span v-show="!collapsed" class="nav-label">{{ item.label }}</span>
            <Tag
              v-if="!collapsed && item.badge"
              :value="item.badge"
              severity="secondary"
              class="nav-badge"
            />
          </RouterLink>
        </div>
      </nav>

      <!-- Footer -->
      <div class="sidebar-footer">
        <div v-show="!collapsed" class="user-block">
          <Avatar
            :label="initials"
            shape="circle"
            class="user-avatar"
          />
          <div class="user-info">
            <p class="user-name">{{ auth.user?.full_name || auth.user?.email }}</p>
            <p class="user-role">{{ auth.user?.is_superuser ? 'Admin' : 'Member' }}</p>
          </div>
        </div>
        <Button
          v-tooltip.right="'Sign out'"
          icon="pi pi-sign-out"
          severity="secondary"
          text
          rounded
          aria-label="Sign out"
          @click="auth.logout"
        />
      </div>
    </aside>

    <!-- ── Main ─────────────────────────────────────────────────────── -->
    <div class="main-wrapper">
      <header class="topbar">
        <Breadcrumb :home="breadcrumbHome" :model="breadcrumbItems" class="topbar-crumbs">
          <template #item="{ item }">
            <RouterLink v-if="item.to" :to="item.to" class="crumb-link">
              <i v-if="item.icon" :class="['pi', item.icon]" />
              <span>{{ item.label }}</span>
            </RouterLink>
            <span v-else class="crumb-current">{{ item.label }}</span>
          </template>
        </Breadcrumb>

        <div class="topbar-right">
          <Tag value="v0.1.0" severity="secondary" rounded />
        </div>
      </header>

      <main class="page-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import Avatar from 'primevue/avatar'
import Breadcrumb from 'primevue/breadcrumb'
import Button from 'primevue/button'
import Tag from 'primevue/tag'

const auth = useAuthStore()
const route = useRoute()
const collapsed = ref(false)

const initials = computed(() => {
  const name = auth.user?.full_name || auth.user?.email || ''
  return (
    name.split(/[\s@]/).map((s) => s[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() ||
    '?'
  )
})

// ── Navigation model ───────────────────────────────────────────────────────
// Structured so each section is rendered once; add/remove items here rather
// than duplicating the sidebar markup.
const navSections = computed(() => [
  {
    label: 'Overview',
    items: [{ to: '/dashboard', icon: 'pi-th-large', label: 'Dashboard' }],
  },
  {
    label: 'Orchestration',
    items: [
      { to: '/agents',    icon: 'pi-sparkles', label: 'Agents' },
      { to: '/runs',      icon: 'pi-play',     label: 'Runs' },
      { to: '/workflows', icon: 'pi-sitemap',  label: 'Workflows', badge: 'Preview' },
    ],
  },
  {
    label: 'AI',
    items: [
      { to: '/prompt-optimizer', icon: 'pi-bolt',      label: 'Prompt Optimizer' },
      { to: '/tools',            icon: 'pi-wrench',    label: 'Tools' },
      { to: '/models',           icon: 'pi-microchip', label: 'Models' },
    ],
  },
  ...(auth.user?.is_superuser
    ? [{ label: 'Admin', items: [{ to: '/users', icon: 'pi-users', label: 'Users' }] }]
    : []),
])

// ── Breadcrumbs ────────────────────────────────────────────────────────────
const ROUTE_LABELS = {
  dashboard: 'Dashboard',
  agents: 'Agents',
  runs: 'Runs',
  tools: 'Tools',
  models: 'Models',
  users: 'Users',
  workflows: 'Workflows',
  'prompt-optimizer': 'Prompt Optimizer',
  history: 'History',
}

const breadcrumbHome = computed(() => ({
  icon: 'pi pi-home',
  to: '/dashboard',
}))

const breadcrumbItems = computed(() => {
  const parts = route.path.split('/').filter(Boolean)
  if (!parts.length || parts[0] === 'dashboard') return []
  return parts.map((p, i) => ({
    label: ROUTE_LABELS[p] || route.meta.title || p,
    to: i < parts.length - 1 ? '/' + parts.slice(0, i + 1).join('/') : null,
  }))
})
</script>

<style scoped>
/* ── Shell ───────────────────────────────────────────────────────────────── */
.app-shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--p-surface-950, var(--color-bg));
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
.sidebar {
  width: var(--sidebar-width);
  background: var(--p-surface-900, var(--color-surface));
  border-right: 1px solid var(--p-surface-800, var(--color-border));
  display: flex;
  flex-direction: column;
  transition: width var(--transition-slow);
  flex-shrink: 0;
  overflow: hidden;
}
.sidebar--collapsed { width: 64px; }

/* Brand */
.sidebar-brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0.75rem;
  height: var(--topbar-height);
  border-bottom: 1px solid var(--p-surface-800, var(--color-border));
  flex-shrink: 0;
  gap: 0.25rem;
}
.brand-link {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  overflow: hidden;
  flex: 1;
}
.brand-logo {
  width: 30px;
  height: 30px;
  border-radius: 7px;
  flex-shrink: 0;
}
.brand-name {
  font-size: 1rem;
  font-weight: 700;
  color: var(--p-text-color, var(--color-text));
  white-space: nowrap;
  letter-spacing: -0.01em;
}
.brand-accent { color: var(--p-primary-400, var(--color-primary-light)); }

.collapse-btn {
  background: none;
  border: none;
  color: var(--p-text-muted-color, var(--color-text-subtle));
  cursor: pointer;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
  display: grid;
  place-items: center;
  font-size: 12px;
  transition: color var(--transition), background var(--transition);
}
.collapse-btn:hover {
  color: var(--p-text-color, var(--color-text));
  background: var(--p-surface-800, var(--color-surface-2));
}

/* Nav */
.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 0.5rem;
}
.nav-section + .nav-section { margin-top: 0.75rem; }
.nav-section-label {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: var(--p-text-muted-color, var(--color-text-subtle));
  padding: 0.35rem 0.75rem;
  white-space: nowrap;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.55rem 0.7rem;
  margin: 0.1rem 0;
  border-radius: var(--radius);
  color: var(--p-text-muted-color, var(--color-text-muted));
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background var(--transition), color var(--transition);
  white-space: nowrap;
  cursor: pointer;
  position: relative;
}
.nav-item:hover {
  background: var(--p-surface-800, var(--color-surface-2));
  color: var(--p-text-color, var(--color-text));
}
.nav-item--active {
  background: color-mix(in srgb, var(--p-primary-500, #6366f1) 14%, transparent);
  color: var(--p-primary-300, var(--color-primary-light));
  font-weight: 600;
}
.nav-item--active::before {
  content: '';
  position: absolute;
  left: -0.5rem;
  top: 0.4rem;
  bottom: 0.4rem;
  width: 3px;
  background: var(--p-primary-500, var(--color-primary));
  border-radius: 0 3px 3px 0;
}
.nav-item--disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.nav-item--disabled:hover {
  background: transparent;
  color: var(--p-text-muted-color, var(--color-text-muted));
}
.nav-icon {
  width: 18px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  font-size: 15px;
}
.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}
.nav-badge {
  font-size: 0.62rem !important;
  padding: 0.1rem 0.4rem !important;
}

/* Footer */
.sidebar-footer {
  border-top: 1px solid var(--p-surface-800, var(--color-border));
  padding: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}
.user-block {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}
.user-avatar {
  background: color-mix(in srgb, var(--p-primary-500, #6366f1) 22%, transparent) !important;
  color: var(--p-primary-300, var(--color-primary-light)) !important;
  font-weight: 700;
  font-size: 0.72rem;
  width: 32px !important;
  height: 32px !important;
  flex-shrink: 0;
}
.user-info { min-width: 0; flex: 1; }
.user-name {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--p-text-color, var(--color-text));
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-role {
  font-size: 0.7rem;
  color: var(--p-text-muted-color, var(--color-text-subtle));
}

/* ── Main ────────────────────────────────────────────────────────────────── */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  height: var(--topbar-height);
  background: var(--p-surface-900, var(--color-surface));
  border-bottom: 1px solid var(--p-surface-800, var(--color-border));
  flex-shrink: 0;
}

:deep(.topbar-crumbs),
:deep(.topbar-crumbs .p-breadcrumb) {
  background: transparent;
  border: none;
  padding: 0;
}
:deep(.topbar-crumbs .p-breadcrumb-list) { gap: 0.35rem; }
:deep(.crumb-link) {
  color: var(--p-text-muted-color, var(--color-text-muted));
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.82rem;
  transition: color var(--transition);
}
:deep(.crumb-link:hover) { color: var(--p-text-color, var(--color-text)); }
:deep(.crumb-current) {
  color: var(--p-text-color, var(--color-text));
  font-weight: 500;
  font-size: 0.82rem;
}

.topbar-right { display: flex; align-items: center; gap: 0.75rem; }

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.75rem 2rem;
}
</style>
