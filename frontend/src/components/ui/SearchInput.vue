<template>
  <div class="search-wrap">
    <Search :size="12" :stroke-width="1.6" class="search-wrap__icon" />
    <input
      :value="modelValue"
      type="search"
      class="input search-wrap__input"
      :placeholder="placeholder"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <button
      v-if="modelValue && clearable"
      class="search-wrap__clear"
      aria-label="Clear"
      @click="$emit('update:modelValue', '')"
    >
      <X :size="11" :stroke-width="1.75" />
    </button>
  </div>
</template>

<script setup>
import { Search, X } from 'lucide-vue-next'

defineProps({
  modelValue: { type: String, default: '' },
  placeholder:{ type: String, default: 'Search…' },
  clearable:  { type: Boolean, default: true },
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.search-wrap { position: relative; display: flex; align-items: center; }
.search-wrap__icon {
  position: absolute;
  left: 10px;
  color: var(--text-faint);
  pointer-events: none;
}
.search-wrap__input { padding-left: 28px; padding-right: 28px; min-width: 200px; }
.search-wrap__input::-webkit-search-cancel-button { display: none; }
.search-wrap__clear {
  position: absolute;
  right: 6px;
  width: 18px;
  height: 18px;
  padding: 0;
  display: grid;
  place-items: center;
  color: var(--text-faint);
  border-radius: var(--r-sm);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background 0.1s, color 0.1s;
}
.search-wrap__clear:hover { background: var(--bg-hover); color: var(--text); }
</style>
