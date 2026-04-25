<template>
  <div class="select" :class="{ 'select--block': block }">
    <select
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      class="input select__input"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option v-if="placeholder" value="">{{ placeholder }}</option>
      <!-- Array of strings OR array of { value, label } -->
      <template v-if="options.length">
        <option
          v-for="opt in normalizedOptions"
          :key="opt.value"
          :value="opt.value"
          :disabled="opt.disabled"
        >{{ opt.label }}</option>
      </template>
      <slot v-else />
    </select>
    <ChevronDown :size="12" :stroke-width="1.75" class="select__chevron" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ChevronDown } from 'lucide-vue-next'

const props = defineProps({
  modelValue: { type: [String, Number, Boolean], default: '' },
  options:     { type: Array,  default: () => [] }, // string[] or { value, label, disabled? }[]
  placeholder: { type: String, default: null },
  disabled:    { type: Boolean, default: false },
  required:    { type: Boolean, default: false },
  block:       { type: Boolean, default: false },
})
defineEmits(['update:modelValue'])

const normalizedOptions = computed(() =>
  props.options.map(o => typeof o === 'object' ? o : { value: o, label: o })
)
</script>

<style scoped>
.select { position: relative; display: inline-flex; }
.select--block { width: 100%; }
.select--block .select__input { width: 100%; }

.select__input {
  appearance: none;
  -webkit-appearance: none;
  padding-right: 26px;
  cursor: pointer;
}

.select__chevron {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-faint);
  pointer-events: none;
}
</style>
