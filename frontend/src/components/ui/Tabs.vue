<template>
  <div class="tabs">
    <div class="tabs__bar" role="tablist">
      <button
        v-for="t in tabs"
        :key="t.id"
        type="button"
        role="tab"
        :aria-selected="t.id === active"
        :aria-controls="`tab-panel-${t.id}`"
        :disabled="t.disabled"
        class="tabs__tab"
        :class="{ 'tabs__tab--active': t.id === active, 'tabs__tab--disabled': t.disabled }"
        @click="select(t.id)"
      >
        <component
          :is="t.icon"
          v-if="t.icon"
          :size="13"
          :stroke-width="1.75"
          class="tabs__tab-icon"
        />
        <span>{{ t.label }}</span>
        <span v-if="t.badge" class="tabs__tab-badge mono">{{ t.badge }}</span>
      </button>
    </div>

    <div
      :id="`tab-panel-${active}`"
      class="tabs__panel"
      role="tabpanel"
      :aria-labelledby="`tab-${active}`"
    >
      <slot :active="active" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  /**
   * Array of tab descriptors:
   *   { id, label, icon?, badge?, disabled? }
   */
  tabs:       { type: Array, required: true },
  modelValue: { type: String, default: null },
})
const emit = defineEmits(['update:modelValue', 'change'])

const active = computed({
  get: () => props.modelValue ?? props.tabs[0]?.id,
  set: (v) => emit('update:modelValue', v),
})

function select(id) {
  const tab = props.tabs.find(t => t.id === id)
  if (!tab || tab.disabled) return
  active.value = id
  emit('change', id)
}
</script>

<style scoped>
.tabs { display: flex; flex-direction: column; gap: 12px; min-width: 0; }

.tabs__bar {
  display: flex;
  gap: 2px;
  border-bottom: 1px solid var(--border);
  margin: -2px -2px 0;
  padding: 0 2px;
}

.tabs__tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-dim);
  font-size: 12.5px;
  cursor: pointer;
  transition: color 0.1s, border-color 0.1s;
  margin-bottom: -1px;
}
.tabs__tab:hover:not(:disabled) { color: var(--text); }
.tabs__tab--active {
  color: var(--text);
  border-bottom-color: var(--accent);
  font-weight: 500;
}
.tabs__tab--disabled { opacity: 0.45; cursor: not-allowed; }
.tabs__tab-icon { flex-shrink: 0; opacity: 0.85; }

.tabs__tab-badge {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 3px;
  background: var(--bg-elev);
  color: var(--text-faint);
  border: 1px solid var(--border);
  line-height: 1;
}
.tabs__tab--active .tabs__tab-badge { background: var(--accent-dim); color: var(--accent); border-color: transparent; }

.tabs__panel { min-width: 0; }
</style>
