<template>
  <Teleport to="body">
    <div class="toast-stack">
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          :class="['toast', `toast--${t.type}`]"
          @click="remove(t.id)"
        >
          <span class="toast__icon">
            {{ { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' }[t.type] ?? 'ℹ' }}
          </span>
          <span class="toast__msg">{{ t.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToast } from '@/composables/useToast'
const { toasts, remove } = useToast()
</script>

<style scoped>
.toast-stack {
  position: fixed;
  top: 1.25rem;
  right: 1.25rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  pointer-events: none;
}
.toast {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 1rem;
  border-radius: var(--radius);
  border: 1px solid var(--color-border);
  background: var(--color-surface-2);
  box-shadow: var(--shadow-md);
  font-size: 0.875rem;
  max-width: 360px;
  pointer-events: all;
  cursor: pointer;
}
.toast--success { border-color: var(--color-success); }
.toast--error   { border-color: var(--color-danger);  }
.toast--warning { border-color: var(--color-warning); }
.toast--info    { border-color: var(--color-info);    }

.toast__icon {
  font-size: 0.9rem;
  flex-shrink: 0;
  width: 20px;
  text-align: center;
}
.toast--success .toast__icon { color: var(--color-success-text); }
.toast--error   .toast__icon { color: var(--color-danger-text);  }
.toast--warning .toast__icon { color: var(--color-warning-text); }
.toast--info    .toast__icon { color: var(--color-info);          }

.toast-enter-active { transition: all 0.2s ease; }
.toast-leave-active { transition: all 0.15s ease; }
.toast-enter-from   { opacity: 0; transform: translateX(20px); }
.toast-leave-to     { opacity: 0; transform: translateX(20px); }
</style>
