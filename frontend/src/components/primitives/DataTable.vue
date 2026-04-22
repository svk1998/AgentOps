<template>
  <div class="dt">
    <div class="dt__head" :style="gridStyle">
      <div
        v-for="col in columns"
        :key="col.key"
        class="dt__th"
        :class="`dt__th--${col.align || 'left'}`"
      >{{ col.label }}</div>
    </div>

    <div v-if="!rows.length" class="dt__empty">
      <slot name="empty">{{ emptyText }}</slot>
    </div>

    <div v-else class="dt__body">
      <div
        v-for="(row, i) in rows"
        :key="row.id ?? i"
        class="dt__row"
        :class="{ 'dt__row--clickable': !!onRowClick }"
        :style="gridStyle"
        @click="onRowClick && onRowClick(row)"
      >
        <div
          v-for="col in columns"
          :key="col.key"
          class="dt__td"
          :class="`dt__td--${col.align || 'left'}`"
        >
          <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
            {{ row[col.key] ?? '—' }}
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] },
  emptyText: { type: String, default: 'No data' },
  onRowClick: { type: Function, default: null },
})

const gridStyle = computed(() => ({
  gridTemplateColumns: props.columns.map(c => c.width || '1fr').join(' '),
}))
</script>

<style scoped>
.dt { font-size: 12px; }
.dt__head {
  display: grid;
  padding: 0 14px;
  height: 32px;
  align-items: center;
  border-bottom: 1px solid var(--border);
  background: var(--bg-elev);
}
.dt__th {
  font-size: 10.5px;
  color: var(--text-faint);
  font-family: var(--mono);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 500;
}
.dt__th--right  { text-align: right; }
.dt__th--center { text-align: center; }

.dt__body { display: flex; flex-direction: column; }

.dt__row {
  display: grid;
  padding: 0 14px;
  min-height: 36px;
  align-items: center;
  border-bottom: 1px solid var(--border);
  transition: background 0.1s;
}
.dt__row:last-child { border-bottom: none; }
.dt__row--clickable { cursor: pointer; }
.dt__row--clickable:hover { background: var(--bg-hover); }

.dt__td {
  font-size: 12px;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.dt__td--right  { text-align: right; }
.dt__td--center { text-align: center; }

.dt__empty {
  padding: 32px 14px;
  text-align: center;
  color: var(--text-faint);
  font-size: 12px;
  font-family: var(--mono);
}
</style>
