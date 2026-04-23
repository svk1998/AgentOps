<template>
  <div class="table-wrap">
    <table class="table">
      <thead>
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            :style="col.width ? `width:${col.width}` : ''"
            :class="col.align ? `align-${col.align}` : ''"
          >
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <!-- Loading skeleton -->
        <template v-if="loading">
          <tr v-for="n in 5" :key="n" class="skeleton-row">
            <td v-for="col in columns" :key="col.key">
              <span class="skeleton-cell" />
            </td>
          </tr>
        </template>
        <!-- Empty state -->
        <tr v-else-if="!rows.length">
          <td :colspan="columns.length" class="empty-cell">
            <slot name="empty">
              <div class="empty-state">
                <span class="empty-icon">📭</span>
                <p>{{ emptyText }}</p>
              </div>
            </slot>
          </td>
        </tr>
        <!-- Data rows -->
        <tr
          v-for="(row, rowIdx) in rows"
          v-else
          :key="row.id ?? rowIdx"
          :class="{ 'row--clickable': !!onRowClick }"
          @click="onRowClick && onRowClick(row)"
        >
          <td
            v-for="col in columns"
            :key="col.key"
            :class="col.align ? `align-${col.align}` : ''"
          >
            <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
              {{ row[col.key] ?? '—' }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  columns:    { type: Array,    required: true },
  rows:       { type: Array,    default: () => [] },
  loading:    { type: Boolean,  default: false },
  emptyText:  { type: String,   default: 'No data yet' },
  onRowClick: { type: Function, default: null },
})
</script>

<style scoped>
.table-wrap { overflow-x: auto; }
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}
.table thead th {
  text-align: left;
  padding: 0.6rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-2);
  white-space: nowrap;
}
.table tbody td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
  vertical-align: middle;
}
.table tbody tr:last-child td { border-bottom: none; }
.table tbody tr.row--clickable { cursor: pointer; }
.table tbody tr.row--clickable:hover td { background: var(--color-surface-2); }

.align-right  { text-align: right; }
.align-center { text-align: center; }

/* Skeleton */
.skeleton-row td { padding: 0.75rem 1rem; border-bottom: 1px solid var(--color-border); }
.skeleton-cell {
  display: block;
  height: 16px;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--color-surface-2) 25%, var(--color-surface-3) 50%, var(--color-surface-2) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

/* Empty */
.empty-cell { text-align: center; padding: 3rem 1rem !important; }
.empty-state { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; }
.empty-icon  { font-size: 2rem; }
.empty-state p { color: var(--color-text-muted); }
</style>
