<template>
  <div class="workflows-page">
    <div class="empty-card">
      <div class="icon-wrap">
        <i class="pi pi-sitemap" />
      </div>
      <h1>Workflows</h1>
      <p class="lead">
        Chain agents, tools, and conditions into reusable pipelines. Trigger them
        on a schedule, from an API call, or at the end of another run.
      </p>

      <div class="features">
        <div class="feature">
          <i class="pi pi-share-alt" />
          <div>
            <h3>Visual builder</h3>
            <p>Drag-and-drop DAG editor for agent-to-agent handoffs.</p>
          </div>
        </div>
        <div class="feature">
          <i class="pi pi-clock" />
          <div>
            <h3>Scheduled runs</h3>
            <p>Cron triggers with retry policy and run history.</p>
          </div>
        </div>
        <div class="feature">
          <i class="pi pi-eye" />
          <div>
            <h3>Live monitoring</h3>
            <p>Per-node status, token accounting, and failure alerts.</p>
          </div>
        </div>
      </div>

      <Tag value="Coming soon" severity="info" rounded class="status-tag" />
    </div>
  </div>
</template>

<script setup>
import Tag from 'primevue/tag'
</script>

<style scoped>
.workflows-page {
  display: grid;
  place-items: center;
  min-height: 70vh;
}
.empty-card {
  max-width: 640px;
  text-align: center;
  background: var(--p-surface-900, var(--color-surface));
  border: 1px solid var(--p-surface-800, var(--color-border));
  border-radius: var(--radius-xl);
  padding: 3rem 2.5rem;
}
.icon-wrap {
  width: 64px;
  height: 64px;
  margin: 0 auto 1.25rem;
  border-radius: 16px;
  display: grid;
  place-items: center;
  background: color-mix(in srgb, var(--p-primary-500, #6366f1) 18%, transparent);
  color: var(--p-primary-300, var(--color-primary-light));
  font-size: 28px;
}
h1 {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--p-text-color, var(--color-text));
}
.lead {
  color: var(--p-text-muted-color, var(--color-text-muted));
  line-height: 1.6;
  margin-bottom: 2rem;
}
.features {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
  text-align: left;
}
@media (min-width: 640px) {
  .features { grid-template-columns: repeat(3, 1fr); }
}
.feature {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 1rem;
  background: var(--p-surface-800, var(--color-surface-2));
  border: 1px solid var(--p-surface-700, var(--color-border-strong));
  border-radius: var(--radius);
}
.feature i {
  font-size: 18px;
  color: var(--p-primary-400, var(--color-primary-light));
}
.feature h3 {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--p-text-color, var(--color-text));
  margin-bottom: 0.15rem;
}
.feature p {
  font-size: 0.78rem;
  color: var(--p-text-muted-color, var(--color-text-muted));
  line-height: 1.5;
}
.status-tag { font-weight: 500; }
</style>
