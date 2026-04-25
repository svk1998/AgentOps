<template>
  <div class="filter-bar">
    <!-- Search input — only render if v-model:search is bound -->
    <SearchInput
      v-if="search !== undefined"
      :model-value="search"
      :placeholder="searchPlaceholder"
      class="filter-bar__search"
      @update:model-value="emit('update:search', $event)"
    />

    <!-- Filter slot — pages drop their selects/chip groups here -->
    <div v-if="$slots.filters" class="filter-bar__filters">
      <slot name="filters" />
    </div>

    <!-- Active-filter chip indicator (count of applied filters) -->
    <div v-if="appliedCount > 0" class="filter-bar__count mono">
      <Filter :size="11" :stroke-width="1.6" />
      <span>{{ appliedCount }} filter{{ appliedCount === 1 ? '' : 's' }}</span>
      <button v-if="resettable" class="filter-bar__reset" @click="emit('reset')">clear</button>
    </div>

    <!-- Spacer — pushes actions slot to the right -->
    <div class="spacer" />

    <!-- Actions slot — refresh, new-X buttons, etc. -->
    <div v-if="$slots.actions" class="filter-bar__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
import { Filter } from 'lucide-vue-next'
import SearchInput from './SearchInput.vue'

defineProps({
  search:            { type: String, default: undefined },
  searchPlaceholder: { type: String, default: 'Search…' },
  /** Number of applied filters — pass `Object.values(filters).filter(Boolean).length` */
  appliedCount:      { type: Number, default: 0 },
  /** Show "clear" button when any filter is applied. Emits @reset. */
  resettable:        { type: Boolean, default: true },
})
const emit = defineEmits(['update:search', 'reset'])
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.filter-bar__search { flex-shrink: 0; }

.filter-bar__filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-bar__count {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 10.5px;
  color: var(--text-faint);
  padding: 0 8px;
  height: 22px;
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: 999px;
}
.filter-bar__reset {
  margin-left: 2px;
  padding: 0;
  font-size: 10.5px;
  color: var(--accent);
  background: transparent;
  border: none;
  cursor: pointer;
}
.filter-bar__reset:hover { text-decoration: underline; }

.spacer { flex: 1; }

.filter-bar__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
