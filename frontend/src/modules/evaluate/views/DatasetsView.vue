<template>
  <div class="page-shell">
    <div class="page-header">
      <div class="page-header-meta mono faint">evaluate</div>
      <h1 class="page-title">Datasets</h1>
      <p class="page-desc">Create, version and manage evaluation datasets for your agents</p>
    </div>
    <div class="shell-empty card">
      <svg width="32" height="32" viewBox="0 0 16 16" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.8">
        <ellipse cx="8" cy="4" rx="6" ry="2"/>
        <path d="M2 4v4c0 1.1 2.7 2 6 2s6-.9 6-2V4"/>
        <path d="M2 8v4c0 1.1 2.7 2 6 2s6-.9 6-2V8"/>
      </svg>
      <p class="shell-empty-label">Under construction</p>
      <p class="dim mono" style="font-size:11px">Coming in Phase 1</p>
    </div>
  </div>
</template>

<style scoped>
.page-shell { display: flex; flex-direction: column; gap: 20px; height: 100%; }
.page-header-meta { font-size: 10.5px; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }
.page-title  { font-size: 20px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }
.page-desc   { font-size: 12px; color: var(--text-dim); margin-top: 4px; font-family: var(--mono); }
.shell-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-style: dashed;
}
.shell-empty-label { font-size: 13px; font-weight: 500; color: var(--text-dim); }
</style>
