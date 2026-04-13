<template>
  <span :class="['badge', `badge--${variant}`]">
    <span v-if="dot" :class="['badge__dot', { 'badge__dot--pulse': variant === 'running' }]" />
    <slot />
  </span>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'neutral' },
  // success | warning | danger | info | neutral | running | pending | completed | failed | cancelled
  dot: { type: Boolean, default: false },
})
</script>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.55rem;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  letter-spacing: 0.01em;
}

.badge--neutral   { background: var(--color-surface-3); color: var(--color-text-muted); }
.badge--success,
.badge--completed { background: var(--color-success-subtle); color: var(--color-success-text); }
.badge--warning   { background: var(--color-warning-subtle); color: var(--color-warning-text); }
.badge--danger,
.badge--failed    { background: var(--color-danger-subtle);  color: var(--color-danger-text);  }
.badge--info      { background: var(--color-info-subtle);    color: var(--color-info);          }
.badge--running   { background: var(--color-running-subtle); color: var(--color-running);       }
.badge--pending   { background: var(--color-surface-3);      color: var(--color-pending);       }
.badge--cancelled { background: var(--color-surface-3);      color: var(--color-cancelled);     }
.badge--primary   { background: var(--color-primary-subtle); color: var(--color-primary-light); }

.badge__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
}
.badge__dot--pulse { animation: pulse-dot 1.5s ease-in-out infinite; }
</style>
