<template>
  <span
    class="tooltip"
    @mouseenter="open"
    @mouseleave="close"
    @focusin="open"
    @focusout="close"
  >
    <slot />
    <Teleport to="body">
      <Transition name="tt">
        <span
          v-if="shown && content"
          ref="tipRef"
          class="tooltip__content mono"
          :class="`tooltip__content--${placement}`"
          role="tooltip"
          :style="positionStyle"
        >{{ content }}</span>
      </Transition>
    </Teleport>
  </span>
</template>

<script setup>
import { ref, nextTick, onBeforeUnmount } from 'vue'

const props = defineProps({
  content:   { type: String, required: true },
  placement: { type: String, default: 'top' }, // top | bottom | left | right
  delay:     { type: Number, default: 250 },
  offset:    { type: Number, default: 8 },     // gap between trigger and tip
})

const shown = ref(false)
const tipRef = ref(null)
const positionStyle = ref({})
let openTimer = null

function open(e) {
  clearTimeout(openTimer)
  const trigger = e.currentTarget
  openTimer = setTimeout(async () => {
    shown.value = true
    await nextTick()
    position(trigger)
  }, props.delay)
}

function close() {
  clearTimeout(openTimer)
  shown.value = false
}

function position(trigger) {
  if (!trigger || !tipRef.value) return
  const r = trigger.getBoundingClientRect()
  const t = tipRef.value.getBoundingClientRect()
  let top, left
  switch (props.placement) {
    case 'bottom':
      top  = r.bottom + props.offset
      left = r.left + r.width / 2 - t.width / 2
      break
    case 'left':
      top  = r.top + r.height / 2 - t.height / 2
      left = r.left - t.width - props.offset
      break
    case 'right':
      top  = r.top + r.height / 2 - t.height / 2
      left = r.right + props.offset
      break
    case 'top':
    default:
      top  = r.top - t.height - props.offset
      left = r.left + r.width / 2 - t.width / 2
  }
  // Keep within viewport
  left = Math.max(8, Math.min(left, window.innerWidth - t.width - 8))
  top  = Math.max(8, Math.min(top,  window.innerHeight - t.height - 8))
  positionStyle.value = { top: `${top}px`, left: `${left}px` }
}

onBeforeUnmount(() => clearTimeout(openTimer))
</script>

<style scoped>
.tooltip { display: inline-flex; }

.tooltip__content {
  position: fixed;
  z-index: 2000;
  background: var(--bg-elev-2);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  padding: 4px 8px;
  font-size: 11px;
  line-height: 1.3;
  max-width: 240px;
  pointer-events: none;
  box-shadow: 0 6px 18px rgba(0,0,0,0.35);
  white-space: pre-wrap;
}

/* Transition */
.tt-enter-active, .tt-leave-active { transition: opacity 0.1s, transform 0.1s; }
.tt-enter-from, .tt-leave-to { opacity: 0; transform: translateY(2px); }
</style>
