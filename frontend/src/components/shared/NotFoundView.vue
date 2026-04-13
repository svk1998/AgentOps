<template>
  <div class="not-found">
    <h1>404</h1>
    <p>Page not found</p>
    <RouterLink to="/dashboard">← Back to Dashboard</RouterLink>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: grid;
  place-items: center;
  text-align: center;
  gap: 0.5rem;
}
h1 { font-size: 5rem; font-weight: 800; color: var(--color-primary); line-height: 1; }
p  { color: var(--color-text-muted); margin-bottom: 1rem; }
a  { color: var(--color-primary); font-weight: 500; }
</style>
