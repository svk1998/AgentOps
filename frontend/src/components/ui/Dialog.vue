<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div
        v-if="modelValue"
        class="dialog-overlay"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        @click.self="onBackdrop"
      >
        <div ref="cardRef" class="dialog-card" :class="`dialog-card--${size}`" @keydown.esc.stop="close">
          <!-- Header -->
          <div v-if="title || eyebrow || $slots.header" class="dialog-head">
            <div class="dialog-head__title">
              <div v-if="eyebrow" class="page-eyebrow mono faint">{{ eyebrow }}</div>
              <h2 v-if="title" :id="titleId" class="dialog-title">{{ title }}</h2>
              <slot name="header" />
            </div>
            <button class="btn ghost dialog-close" aria-label="Close" @click="close">
              <X :size="13" :stroke-width="1.75" />
            </button>
          </div>

          <!-- Body -->
          <div class="dialog-body">
            <slot />
          </div>

          <!-- Footer -->
          <div v-if="$slots.footer" class="dialog-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick, onBeforeUnmount, useId } from 'vue'
import { X } from 'lucide-vue-next'

const props = defineProps({
  modelValue:       { type: Boolean, required: true },
  title:            { type: String, default: null },
  eyebrow:          { type: String, default: null },
  size:             { type: String, default: 'md' }, // sm | md | lg
  closeOnBackdrop:  { type: Boolean, default: true },
  closeOnEsc:       { type: Boolean, default: true },
  persistent:       { type: Boolean, default: false }, // ignore backdrop + esc
})
const emit = defineEmits(['update:modelValue', 'close'])

const titleId = `dlg-${useId()}`
const cardRef = ref(null)

function close() {
  if (props.persistent) return
  emit('update:modelValue', false)
  emit('close')
}
function onBackdrop() {
  if (props.closeOnBackdrop) close()
}

function onDocKey(e) {
  if (!props.modelValue) return
  if (e.key === 'Escape' && props.closeOnEsc && !props.persistent) close()
}

watch(() => props.modelValue, async (open) => {
  if (open) {
    document.addEventListener('keydown', onDocKey)
    document.body.style.overflow = 'hidden'
    // Auto-focus the first focusable element in the card
    await nextTick()
    const el = cardRef.value?.querySelector(
      'input:not([type=hidden]), select, textarea, button:not([aria-label=Close])',
    )
    el?.focus?.()
  } else {
    document.removeEventListener('keydown', onDocKey)
    document.body.style.overflow = ''
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onDocKey)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(2px);
  display: grid;
  place-items: center;
  z-index: 1000;
  padding: 20px;
}

.dialog-card {
  width: 100%;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 80px);
  overflow: hidden;
}
.dialog-card--sm { max-width: 380px; }
.dialog-card--md { max-width: 460px; }
.dialog-card--lg { max-width: 680px; }

.dialog-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 18px 20px 10px;
}
.dialog-head__title { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.page-eyebrow {
  font-size: 10.5px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.dialog-title {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--text);
}
.dialog-close {
  width: 26px;
  height: 26px;
  padding: 0;
  justify-content: center;
  flex-shrink: 0;
}

.dialog-body {
  padding: 4px 20px 20px;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  padding: 10px 20px 18px;
  border-top: 1px solid var(--border);
  background: var(--bg-elev);
}

/* Transition */
.dialog-enter-active, .dialog-leave-active { transition: opacity 0.15s; }
.dialog-enter-active .dialog-card,
.dialog-leave-active .dialog-card { transition: transform 0.15s, opacity 0.15s; }
.dialog-enter-from, .dialog-leave-to { opacity: 0; }
.dialog-enter-from .dialog-card,
.dialog-leave-to .dialog-card { transform: translateY(8px); opacity: 0; }
</style>
