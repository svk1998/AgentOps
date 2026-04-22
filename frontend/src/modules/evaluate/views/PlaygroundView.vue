<template>
  <div class="page-shell">
    <div class="page-header">
      <div class="page-header-meta mono faint">evaluate</div>
      <h1 class="page-title">Playground</h1>
      <p class="page-desc">Human-in-the-loop manual review — side-by-side input, output, verdict</p>
    </div>
    <div class="shell-empty card">
      <svg width="32" height="32" viewBox="0 0 16 16" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.8">
        <path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z"/>
        <circle cx="8" cy="8" r="2"/>
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
