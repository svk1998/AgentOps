<template>
  <div class="iteration-card" :class="{ reached: iteration.isGoalReached, latest: isLatest }">
    <!-- Header -->
    <div class="card-header" @click="expanded = !expanded">
      <div class="header-left">
        <span class="iteration-num">#{{ iteration.number }}</span>
        <span v-if="iteration.isGoalReached" class="goal-badge">Goal Reached</span>
        <span v-else class="score-badge" :class="scoreClass">{{ iteration.score }}%</span>
      </div>
      <div class="header-right">
        <span class="toggle-icon">{{ expanded ? '▲' : '▼' }}</span>
      </div>
    </div>

    <!-- Score bar -->
    <div class="score-bar-wrap">
      <div class="score-bar" :style="{ width: iteration.score + '%' }" :class="scoreClass" />
    </div>

    <!-- Body (collapsible) -->
    <div v-if="expanded" class="card-body">
      <div class="section">
        <p class="section-label">Prompt Used</p>
        <pre class="text-block">{{ iteration.prompt }}</pre>
      </div>
      <div class="section">
        <p class="section-label">Generated Output</p>
        <pre class="text-block output">{{ iteration.output }}</pre>
      </div>
      <div v-if="iteration.feedback && !iteration.isGoalReached" class="section">
        <p class="section-label">Improvement Notes</p>
        <p class="feedback-text">{{ iteration.feedback }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  iteration: { type: Object, required: true },
  isLatest:  { type: Boolean, default: false }
})

const expanded = ref(props.isLatest || props.iteration.isGoalReached)

const scoreClass = computed(() => {
  if (props.iteration.score >= 80) return 'high'
  if (props.iteration.score >= 50) return 'mid'
  return 'low'
})
</script>

<style scoped>
.iteration-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  overflow: hidden;
  transition: box-shadow 0.15s;
}
.iteration-card.reached { border-color: #86efac; background: #f0fdf4; }
.iteration-card.latest  { box-shadow: 0 0 0 2px var(--color-primary); }

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  cursor: pointer;
  user-select: none;
}
.header-left { display: flex; align-items: center; gap: 0.6rem; }

.iteration-num {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--color-text-muted);
}

.goal-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  background: #dcfce7;
  color: #15803d;
}

.score-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
}
.score-badge.high { background: #dcfce7; color: #15803d; }
.score-badge.mid  { background: #fef9c3; color: #92400e; }
.score-badge.low  { background: #fee2e2; color: #dc2626; }

.toggle-icon { font-size: 0.7rem; color: var(--color-text-muted); }

.score-bar-wrap {
  height: 3px;
  background: #f1f5f9;
}
.score-bar {
  height: 100%;
  border-radius: 0 2px 2px 0;
  transition: width 0.4s ease;
}
.score-bar.high { background: var(--color-success); }
.score-bar.mid  { background: var(--color-warning); }
.score-bar.low  { background: var(--color-danger); }

.card-body {
  padding: 0.75rem 1rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.section { display: flex; flex-direction: column; gap: 0.3rem; }
.section-label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.text-block {
  background: #f8fafc;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  padding: 0.65rem 0.75rem;
  font-size: 0.85rem;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--font-sans);
  line-height: 1.6;
  max-height: 180px;
  overflow-y: auto;
}
.text-block.output { background: #f0f9ff; border-color: #bae6fd; }

.feedback-text {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  line-height: 1.6;
  font-style: italic;
}
</style>
