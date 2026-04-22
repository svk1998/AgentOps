export const routes = [
  // ── Auth ──
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/modules/auth/views/LoginView.vue'),
    meta: { guestOnly: true }
  },

  // ── App (DefaultLayout) ──
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      { path: '', redirect: '/dashboard' },

      // Overview
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/modules/dashboard/views/DashboardView.vue'),
        meta: { requiresAuth: true, title: 'Dashboard' }
      },

      // Registry
      {
        path: 'registry/agents',
        name: 'RegistryAgents',
        component: () => import('@/modules/registry/views/AgentsView.vue'),
        meta: { requiresAuth: true, title: 'Agents' }
      },

      // Evaluate
      {
        path: 'evaluate/datasets',
        name: 'Datasets',
        component: () => import('@/modules/evaluate/views/DatasetsView.vue'),
        meta: { requiresAuth: true, title: 'Datasets' }
      },
      {
        path: 'evaluate/runs',
        name: 'EvalRuns',
        component: () => import('@/modules/evaluate/views/EvalRunsView.vue'),
        meta: { requiresAuth: true, title: 'Eval Runs' }
      },
      {
        path: 'evaluate/playground',
        name: 'Playground',
        component: () => import('@/modules/evaluate/views/PlaygroundView.vue'),
        meta: { requiresAuth: true, title: 'Playground' }
      },

      // Observe
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('@/modules/analytics/views/AnalyticsView.vue'),
        meta: { requiresAuth: true, title: 'Analytics' }
      },

      // Admin
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/modules/users/views/UsersView.vue'),
        meta: { requiresAuth: true, requiresRole: 'admin', title: 'Users' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/modules/settings/views/SettingsView.vue'),
        meta: { requiresAuth: true, requiresRole: 'admin', title: 'Settings' }
      },
    ]
  },

  // ── 404 ──
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/components/shared/NotFoundView.vue')
  }
]
