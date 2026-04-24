/**
 * Shared enum values — keep in sync with the backend Pydantic enums
 * defined in `backend/app/models/*.py`. Centralizing here prevents
 * drift between multiple views that surface the same dropdowns.
 *
 * Each enum ships three shapes:
 *  - The raw tuple of backend values (for <option :value="v">)
 *  - A human-readable label map (for display text)
 *  - A status-tone map (for StatusDot / Chip variants)
 */

// ── Agent Registry ──────────────────────────────────────────────────────────
export const AGENT_TYPES = ['llm', 'rag', 'vision', 'multi_step_chain', 'tool_use', 'custom']

export const AGENT_TYPE_LABELS = {
  llm:              'LLM',
  rag:              'RAG',
  vision:           'Vision',
  multi_step_chain: 'Multi-step chain',
  tool_use:         'Tool use',
  custom:           'Custom',
}

export const AGENT_STATUSES = ['draft', 'active', 'deprecated', 'archived']

export const AGENT_STATUS_DOT = {
  draft:      'pending',
  active:     'ok',
  deprecated: 'warn',
  archived:   'pending',
}

// ── Eval Runs ───────────────────────────────────────────────────────────────
export const RUN_STATUSES = ['pending', 'running', 'completed', 'failed', 'cancelled']

export const RUN_STATUS_DOT = {
  pending:   'pending',
  running:   'info',
  completed: 'ok',
  failed:    'err',
  cancelled: 'pending',
}

// ── Users ──────────────────────────────────────────────────────────────────
export const USER_ROLES = ['admin', 'evaluator', 'viewer']

export const USER_ROLE_CHIP = {
  admin:     'accent',
  evaluator: 'info',
  viewer:    null,
}

// ── Manual Eval ────────────────────────────────────────────────────────────
export const MANUAL_VERDICTS = ['pass', 'partial', 'fail']
export const MANUAL_SEVERITIES = ['critical', 'major', 'minor']

export const MANUAL_VERDICT_DOT = {
  pass:    'ok',
  partial: 'warn',
  fail:    'err',
}
