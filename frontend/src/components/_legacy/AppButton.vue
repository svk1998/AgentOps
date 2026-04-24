<template>
  <button
    :class="['app-btn', `app-btn--${variant}`, `app-btn--${size}`, { 'app-btn--loading': loading }]"
    :disabled="disabled || loading"
    v-bind="$attrs"
  >
    <AppSpinner v-if="loading" :size="spinnerSize" class="app-btn__spinner" />
    <slot v-else />
  </button>
</template>

<script setup>
import AppSpinner from './AppSpinner.vue'

const props = defineProps({
  variant:  { type: String, default: 'primary' }, // primary | secondary | ghost | danger | success
  size:     { type: String, default: 'md' },       // sm | md | lg
  loading:  { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
})

const spinnerSize = props.size === 'sm' ? 12 : props.size === 'lg' ? 20 : 16
</script>

<style scoped>
.app-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-weight: 500;
  border-radius: var(--radius);
  border: 1px solid transparent;
  cursor: pointer;
  transition: background var(--transition), border-color var(--transition), color var(--transition), opacity var(--transition);
  white-space: nowrap;
  line-height: 1;
}
.app-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.app-btn--loading { cursor: wait; }

/* Sizes */
.app-btn--sm { padding: 0.35rem 0.7rem;  font-size: 0.8rem;  }
.app-btn--md { padding: 0.5rem  1rem;    font-size: 0.875rem;}
.app-btn--lg { padding: 0.65rem 1.25rem; font-size: 0.95rem; }

/* Variants */
.app-btn--primary {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}
.app-btn--primary:not(:disabled):hover {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.app-btn--secondary {
  background: var(--color-surface-3);
  color: var(--color-text);
  border-color: var(--color-border);
}
.app-btn--secondary:not(:disabled):hover {
  background: var(--color-surface-2);
  border-color: var(--color-border-strong);
}

.app-btn--ghost {
  background: transparent;
  color: var(--color-text-muted);
  border-color: transparent;
}
.app-btn--ghost:not(:disabled):hover {
  background: var(--color-surface-3);
  color: var(--color-text);
}

.app-btn--danger {
  background: var(--color-danger-subtle);
  color: var(--color-danger-text);
  border-color: var(--color-danger);
}
.app-btn--danger:not(:disabled):hover {
  background: var(--color-danger);
  color: #fff;
}

.app-btn--success {
  background: var(--color-success-subtle);
  color: var(--color-success-text);
  border-color: var(--color-success);
}
.app-btn--success:not(:disabled):hover {
  background: var(--color-success);
  color: #fff;
}

.app-btn__spinner { flex-shrink: 0; }
</style>
