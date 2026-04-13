<template>
  <span class="badge" :class="status">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true } // active | idle | error | stopped
})

const label = computed(() => ({
  active:  'Active',
  idle:    'Idle',
  error:   'Error',
  stopped: 'Stopped',
}[props.status] ?? props.status))
</script>

<style scoped>
.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 600;
}
.active  { background: #dcfce7; color: #15803d; }
.idle    { background: #f1f5f9; color: #475569; }
.error   { background: #fee2e2; color: #dc2626; }
.stopped { background: #fef9c3; color: #92400e; }
</style>
