<template>
  <component
    :is="tag"
    v-bind="bindings"
    :class="classes"
    :disabled="isDisabled || null"
    :aria-disabled="isDisabled || null"
    :aria-busy="loading || null"
    @click="handleClick"
  >
    <Loader2 v-if="loading" :size="iconSize" :stroke-width="1.75" class="btn__spin" />
    <component
      :is="iconLeft"
      v-else-if="iconLeft"
      :size="iconSize"
      :stroke-width="1.75"
      class="btn__icon"
    />
    <span v-if="$slots.default" class="btn__label"><slot /></span>
    <component
      :is="iconRight"
      v-if="iconRight"
      :size="iconSize"
      :stroke-width="1.75"
      class="btn__icon btn__icon--right"
    />
  </component>
</template>

<script setup>
import { computed } from 'vue'
import { Loader2 } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

const props = defineProps({
  variant:  { type: String,  default: 'default' }, // default | primary | ghost | danger | success
  size:     { type: String,  default: 'md' },      // sm | md | lg
  type:     { type: String,  default: 'button' },
  disabled: { type: Boolean, default: false },
  loading:  { type: Boolean, default: false },
  block:    { type: Boolean, default: false }, // full-width
  iconLeft:  { type: [Object, Function], default: null },
  iconRight: { type: [Object, Function], default: null },
  to:    { type: [String, Object], default: null }, // renders as <RouterLink>
  href:  { type: String, default: null },           // renders as <a>
})
defineEmits(['click'])

const isDisabled = computed(() => props.disabled || props.loading)

const tag = computed(() => {
  if (props.to)   return RouterLink
  if (props.href) return 'a'
  return 'button'
})

const bindings = computed(() => {
  if (props.to) return { to: props.to }
  if (props.href) return { href: props.href }
  return { type: props.type }
})

const iconSize = computed(() => ({ sm: 11, md: 12, lg: 14 }[props.size] ?? 12))

const classes = computed(() => [
  'btn',
  props.variant !== 'default' && `btn--${props.variant}`,
  `btn--${props.size}`,
  props.block && 'btn--block',
  props.loading && 'btn--loading',
])

function handleClick(e) {
  if (isDisabled.value) {
    e.preventDefault()
    e.stopImmediatePropagation()
  }
}
</script>

<style scoped>
/* Overrides / extras on top of the global .btn class in theme.css */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  text-decoration: none;
}
.btn--sm { height: 24px; padding: 0 8px;  font-size: 11px; border-radius: var(--r-sm); }
.btn--md { height: 28px; padding: 0 10px; font-size: 12px; }
.btn--lg { height: 34px; padding: 0 14px; font-size: 13px; }

.btn--block { width: 100%; }

.btn--primary { background: var(--accent); color: var(--accent-text); border-color: var(--accent); font-weight: 500; }
.btn--primary:hover:not(:disabled) { filter: brightness(1.05); }

.btn--ghost   { background: transparent; border-color: transparent; color: var(--text-dim); }
.btn--ghost:hover:not(:disabled) { background: var(--bg-hover); color: var(--text); border-color: transparent; }

.btn--danger  { background: var(--err-dim); border-color: var(--err); color: var(--err); }
.btn--danger:hover:not(:disabled) { filter: brightness(1.08); }

.btn--success { background: var(--ok-dim); border-color: var(--ok); color: var(--ok); }
.btn--success:hover:not(:disabled) { filter: brightness(1.08); }

.btn:disabled,
.btn[aria-disabled="true"] { opacity: 0.55; cursor: not-allowed; }

.btn--loading { cursor: progress; }

.btn__icon { flex-shrink: 0; }
.btn__icon--right { margin-left: 2px; }
.btn__label { line-height: 1; }

.btn__spin { flex-shrink: 0; animation: spin 1s linear infinite; }
</style>
