<template>
  <div class="app-shell">
    <!-- ── Sidebar ── -->
    <aside class="sidebar" :class="{ 'sidebar--collapsed': collapsed }">

      <!-- Brand -->
      <div class="sidebar-brand">
        <div class="brand-inner">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" class="brand-logo">
            <rect x="1" y="1" width="16" height="16" rx="3" fill="var(--accent)" />
            <path d="M5 12 L9 5 L13 12 M6.5 10 H11.5"
              stroke="var(--accent-text)" stroke-width="1.5"
              stroke-linecap="round" stroke-linejoin="round" fill="none" />
          </svg>
          <span v-show="!collapsed" class="brand-name">agentops</span>
        </div>
        <button
          class="btn ghost collapse-btn"
          :title="collapsed ? 'Expand' : 'Collapse'"
          @click="collapsed = !collapsed"
        >
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
            <path v-if="!collapsed" d="M10 4L6 8l4 4" />
            <path v-else d="M6 4l4 4-4 4" />
          </svg>
        </button>
      </div>

      <!-- Nav -->
      <nav class="sidebar-nav">
        <template v-for="section in navSections" :key="section.label">
          <div v-show="!collapsed" class="nav-section-label">{{ section.label }}</div>
          <RouterLink
            v-for="item in section.items"
            :key="item.to"
            :to="item.to"
            class="nav-row"
            active-class="nav-row--active"
            :title="collapsed ? item.label : undefined"
          >
            <component :is="item.icon" class="nav-icon" />
            <span v-show="!collapsed" class="nav-label">{{ item.label }}</span>
            <span v-if="!collapsed && item.shortcut" class="kbd nav-shortcut">{{ item.shortcut }}</span>
          </RouterLink>
        </template>
      </nav>

      <!-- Footer -->
      <div class="sidebar-footer">
        <div v-show="!collapsed" class="user-row">
          <div class="user-avatar">{{ initials }}</div>
          <div class="user-info">
            <div class="user-name">{{ auth.user?.full_name || auth.user?.email }}</div>
            <div class="user-role mono">{{ auth.user?.is_superuser ? 'admin' : 'member' }}</div>
          </div>
        </div>
        <button class="btn ghost icon-btn" title="Sign out" @click="auth.logout">
          <IconSignOut />
        </button>
      </div>
    </aside>

    <!-- ── Main ── -->
    <div class="main-wrapper">
      <!-- Topbar -->
      <header class="topbar">
        <div class="breadcrumb">
          <RouterLink to="/dashboard" class="crumb-link">
            <IconHome />
          </RouterLink>
          <template v-for="(crumb, i) in breadcrumbs" :key="i">
            <span class="crumb-sep">›</span>
            <RouterLink v-if="crumb.to" :to="crumb.to" class="crumb-link">{{ crumb.label }}</RouterLink>
            <span v-else class="crumb-current">{{ crumb.label }}</span>
          </template>
        </div>
        <div class="topbar-right">
          <span class="chip">v0.1.0</span>
        </div>
      </header>

      <!-- Page content -->
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

const auth = useAuthStore()
const route = useRoute()
const collapsed = ref(false)

const initials = computed(() => {
  const name = auth.user?.full_name || auth.user?.email || ''
  return name.split(/[\s@]/).map(s => s[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() || '?'
})

// ── Inline SVG icon components ───────────────────────────────────────────────
const IconFleet = {
  template: `<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="5" height="5" rx="1"/><rect x="9" y="2" width="5" height="5" rx="1"/><rect x="2" y="9" width="5" height="5" rx="1"/><rect x="9" y="9" width="5" height="5" rx="1"/></svg>`
}
const IconEval = {
  template: `<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3 13l2-3 3 1 5-7"/><path d="M13 4h1v1"/></svg>`
}
const IconDatabase = {
  template: `<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="8" cy="4" rx="6" ry="2"/><path d="M2 4v4c0 1.1 2.7 2 6 2s6-.9 6-2V4"/><path d="M2 8v4c0 1.1 2.7 2 6 2s6-.9 6-2V8"/></svg>`
}
const IconPlay = {
  template: `<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6"/><path d="M6.5 5.5l4 2.5-4 2.5z" fill="currentColor" stroke="none"/></svg>`
}
const IconEye = {
  template: `<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z"/><circle cx="8" cy="8" r="2"/></svg>`
}
const IconChart = {
  template: `<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12l3-4 3 2 4-6"/><path d="M2 14h12"/></svg>`
}
const IconUsers = {
  template: `<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="5" r="2.5"/><path d="M1 14c0-2.8 2.2-5 5-5s5 2.2 5 5"/><path d="M11 3.5c1.4 0 2.5 1.1 2.5 2.5S12.4 8.5 11 8.5M15 14c0-2.2-1.8-4-4-4"/></svg>`
}
const IconSettings = {
  template: `<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="2"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.1 3.1l1.4 1.4M11.5 11.5l1.4 1.4M3.1 12.9l1.4-1.4M11.5 4.5l1.4-1.4"/></svg>`
}
const IconHome = {
  template: `<svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M2 6.5L8 2l6 4.5V14a1 1 0 01-1 1H3a1 1 0 01-1-1z"/><path d="M6 15V9h4v6"/></svg>`
}
const IconSignOut = {
  template: `<svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3H3a1 1 0 00-1 1v8a1 1 0 001 1h3"/><path d="M10 11l4-3-4-3"/><path d="M6 8h8"/></svg>`
}

// ── Navigation ────────────────────────────────────────────────────────────────
const navSections = computed(() => [
  {
    label: 'Platform',
    items: [
      { to: '/dashboard',       icon: IconFleet,    label: 'Dashboard',  shortcut: '1' },
      { to: '/registry/agents', icon: IconEval,     label: 'Agents',     shortcut: '2' },
    ],
  },
  {
    label: 'Evaluate',
    items: [
      { to: '/evaluate/datasets',   icon: IconDatabase, label: 'Datasets',   shortcut: '3' },
      { to: '/evaluate/runs',       icon: IconPlay,     label: 'Eval Runs',  shortcut: '4' },
      { to: '/evaluate/playground', icon: IconEye,      label: 'Playground', shortcut: '5' },
    ],
  },
  {
    label: 'Observe',
    items: [
      { to: '/analytics', icon: IconChart, label: 'Analytics', shortcut: '6' },
    ],
  },
  ...(auth.user?.is_superuser ? [{
    label: 'Admin',
    items: [
      { to: '/users',    icon: IconUsers,    label: 'Users',    shortcut: '7' },
      { to: '/settings', icon: IconSettings, label: 'Settings', shortcut: '8' },
    ],
  }] : []),
])

// ── Breadcrumbs ───────────────────────────────────────────────────────────────
const LABELS = {
  dashboard: 'Dashboard', registry: 'Registry', agents: 'Agents',
  evaluate: 'Evaluate', datasets: 'Datasets', runs: 'Eval Runs',
  playground: 'Playground', analytics: 'Analytics',
  settings: 'Settings', users: 'Users',
}

const breadcrumbs = computed(() => {
  const parts = route.path.split('/').filter(Boolean)
  if (!parts.length || parts[0] === 'dashboard') return []
  return parts.map((p, i) => ({
    label: LABELS[p] || route.meta.title || p,
    to: i < parts.length - 1 ? '/' + parts.slice(0, i + 1).join('/') : null,
  }))
})
</script>

<style scoped>
/* ── Shell ── */
.app-shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--bg);
}

/* ── Sidebar ── */
.sidebar {
  width: var(--sidebar-width);
  background: var(--panel);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width 0.2s ease;
  overflow: hidden;
}
.sidebar--collapsed { width: 52px; }

/* Brand */
.sidebar-brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 12px 10px;
  flex-shrink: 0;
  gap: 4px;
  border-bottom: 1px solid var(--border);
}
.brand-inner {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
  flex: 1;
}
.brand-logo { flex-shrink: 0; }
.brand-name {
  font-family: var(--mono);
  font-size: 12.5px;
  font-weight: 600;
  letter-spacing: 0.01em;
  white-space: nowrap;
  color: var(--text);
}
.collapse-btn {
  width: 24px;
  height: 24px;
  padding: 0;
  justify-content: center;
  flex-shrink: 0;
}

/* Nav */
.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 6px 8px;
}
.nav-section-label {
  padding: 12px 10px 4px;
  font-size: 10.5px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-faint);
  font-family: var(--mono);
  white-space: nowrap;
}
.nav-row {
  display: flex;
  align-items: center;
  gap: 9px;
  width: 100%;
  padding: 6px 8px;
  border-radius: var(--r);
  font-size: 12.5px;
  color: var(--text-dim);
  text-decoration: none;
  font-weight: 400;
  border-left: 2px solid transparent;
  margin-left: -2px;
  transition: background 0.1s, color 0.1s;
  white-space: nowrap;
  cursor: pointer;
}
.nav-row:hover { background: var(--bg-hover); color: var(--text); }
.nav-row--active {
  background: var(--bg-elev-2);
  color: var(--text);
  font-weight: 500;
  border-left-color: var(--accent);
}
.nav-icon { flex-shrink: 0; opacity: 0.8; }
.nav-row--active .nav-icon { opacity: 1; }
.nav-label { flex: 1; }
.nav-shortcut { margin-left: auto; flex-shrink: 0; }

/* Footer */
.sidebar-footer {
  border-top: 1px solid var(--border);
  padding: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.user-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}
.user-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--accent-dim);
  color: var(--accent);
  font-size: 10px;
  font-weight: 700;
  font-family: var(--mono);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.user-info { min-width: 0; flex: 1; }
.user-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-role {
  font-size: 10.5px;
  color: var(--text-faint);
}
.icon-btn {
  width: 26px;
  height: 26px;
  padding: 0;
  justify-content: center;
  flex-shrink: 0;
}

/* ── Main ── */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

/* Topbar */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--topbar-height);
  padding: 0 18px;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-family: var(--mono);
  color: var(--text-faint);
}
.crumb-link {
  color: var(--text-dim);
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: color 0.1s;
  text-decoration: none;
}
.crumb-link:hover { color: var(--text); }
.crumb-sep { color: var(--text-faint); }
.crumb-current { color: var(--text); font-weight: 500; }
.topbar-right { display: flex; align-items: center; gap: 8px; }

/* Page */
.page-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--pad);
  background: var(--bg);
}
</style>
