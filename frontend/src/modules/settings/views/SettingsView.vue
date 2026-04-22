<template>
  <div class="page-shell">
    <div class="page-header">
      <h1 class="page-title">Settings</h1>
      <p class="page-subtitle">Platform configuration and preferences</p>
    </div>
    <div class="shell-empty">
      <i class="pi pi-cog shell-icon" />
      <p class="shell-empty-text">Under construction</p>
    </div>
  </div>
</template>

<style scoped>
.page-header { margin-bottom: 2rem; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text); margin-bottom: 0.25rem; }
.page-subtitle { font-size: 0.875rem; color: var(--color-text-muted); }
.shell-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 4rem;
  border: 1px dashed var(--color-border-strong);
  border-radius: var(--radius-lg);
  color: var(--color-text-subtle);
}
.shell-icon { font-size: 2rem; color: var(--color-primary); }
.shell-empty-text { font-size: 0.875rem; }
</style>
