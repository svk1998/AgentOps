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

      // Dashboard
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/modules/dashboard/views/DashboardView.vue'),
        meta: { requiresAuth: true, title: 'Dashboard' }
      },

      // Agents
      {
        path: 'agents',
        name: 'Agents',
        component: () => import('@/modules/agents/views/AgentsView.vue'),
        meta: { requiresAuth: true, title: 'Agents' }
      },
      {
        path: 'agents/:id',
        name: 'AgentDetail',
        component: () => import('@/modules/agents/views/AgentDetailView.vue'),
        meta: { requiresAuth: true, title: 'Agent Detail' }
      },

      // Runs
      {
        path: 'runs',
        name: 'Runs',
        component: () => import('@/modules/runs/views/RunsView.vue'),
        meta: { requiresAuth: true, title: 'Runs' }
      },
      {
        path: 'runs/:id',
        name: 'RunDetail',
        component: () => import('@/modules/runs/views/RunDetailView.vue'),
        meta: { requiresAuth: true, title: 'Run Detail' }
      },

      // Workflows (placeholder — full editor coming soon)
      {
        path: 'workflows',
        name: 'Workflows',
        component: () => import('@/modules/workflows/views/WorkflowsView.vue'),
        meta: { requiresAuth: true, title: 'Workflows' }
      },

      // Tools
      {
        path: 'tools',
        name: 'Tools',
        component: () => import('@/modules/tools/views/ToolsView.vue'),
        meta: { requiresAuth: true, title: 'Tools' }
      },

      // Models
      {
        path: 'models',
        name: 'Models',
        component: () => import('@/modules/models/views/ModelsView.vue'),
        meta: { requiresAuth: true, title: 'Models' }
      },

      // Prompt Optimizer
      {
        path: 'prompt-optimizer',
        name: 'PromptOptimizer',
        component: () => import('@/modules/prompt-optimizer/views/PromptOptimizerView.vue'),
        meta: { requiresAuth: true, title: 'Prompt Optimizer' }
      },
      {
        path: 'prompt-optimizer/history',
        name: 'PromptOptimizerHistory',
        component: () => import('@/modules/prompt-optimizer/views/RunHistoryView.vue'),
        meta: { requiresAuth: true, title: 'Optimizer History' }
      },

      // Users (admin)
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/modules/users/views/UsersView.vue'),
        meta: { requiresAuth: true, requiresRole: 'admin', title: 'Users' }
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
