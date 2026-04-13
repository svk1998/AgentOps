<template>
  <button
    class="base-btn"
    :class="[variant, size, { loading }]"
    :disabled="disabled || loading"
    v-bind="$attrs"
  >
    <span v-if="loading" class="spinner" />
    <slot />
  </button>
</template>

<script setup>
defineProps({
  variant:  { type: String, default: 'primary' }, // primary | secondary | danger | ghost
  size:     { type: String, default: 'md' },       // sm | md | lg
  loading:  { type: Boolean, default: false },
  disabled: { type: Boolean, default: false }
})
</script>

<style scoped>
.base-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  border: none;
  border-radius: var(--radius);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
  white-space: nowrap;
}
.base-btn:disabled { opacity: 0.55; cursor: not-allowed; }

/* Variants */
.primary   { background: var(--color-primary); color: white; }
.primary:hover:not(:disabled)   { background: var(--color-primary-hover); }
.secondary { background: #f1f5f9; color: var(--color-text); border: 1px solid var(--color-border); }
.secondary:hover:not(:disabled) { background: #e2e8f0; }
.danger    { background: var(--color-danger); color: white; }
.danger:hover:not(:disabled)    { background: #b91c1c; }
.ghost     { background: transparent; color: var(--color-primary); }
.ghost:hover:not(:disabled)     { background: #eff6ff; }

/* Sizes */
.sm { padding: 0.3rem 0.65rem; font-size: 0.8rem; }
.md { padding: 0.55rem 1rem;   font-size: 0.9rem; }
.lg { padding: 0.75rem 1.5rem; font-size: 1rem;   }

/* Spinner */
.spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
