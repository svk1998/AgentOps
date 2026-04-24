<template>
  <span class="status-dot" :class="`status-dot--${resolved}`" :title="status" />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: 'ok' }, // ok | healthy | warn | degraded | err | incident | failed | info | running | pending
})

const MAP = {
  ok: 'ok', healthy: 'ok', completed: 'ok', pass: 'ok',
  warn: 'warn', warning: 'warn', degraded: 'warn', partial: 'warn',
  err: 'err', error: 'err', incident: 'err', failed: 'err', fail: 'err',
  info: 'info', running: 'info', in_progress: 'info',
  pending: 'pending', waiting: 'pending', cancelled: 'pending',
}

const resolved = computed(() => MAP[props.status?.toLowerCase()] || 'pending')
</script>

<style scoped>
.status-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
  background: var(--text-faint);
}
.status-dot--ok    { background: var(--ok);    box-shadow: 0 0 0 2px var(--ok-dim); }
.status-dot--warn  { background: var(--warn);  box-shadow: 0 0 0 2px var(--warn-dim); }
.status-dot--err   { background: var(--err);   box-shadow: 0 0 0 2px var(--err-dim); }
.status-dot--info  { background: var(--info);  box-shadow: 0 0 0 2px var(--info-dim); }
.status-dot--pending { background: var(--text-faint); }
</style>
