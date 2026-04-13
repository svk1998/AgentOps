<template>
  <div class="code-wrap">
    <button v-if="copyable" class="code-copy" @click="copy" :title="copied ? 'Copied!' : 'Copy'">
      {{ copied ? '✓' : '⎘' }}
    </button>
    <pre class="code-block"><code>{{ content }}</code></pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  content:  { type: String, default: '' },
  copyable: { type: Boolean, default: true },
})

const copied = ref(false)
async function copy() {
  await navigator.clipboard.writeText(props.content)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>

<style scoped>
.code-wrap {
  position: relative;
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
}
.code-block {
  padding: 1rem;
  overflow-x: auto;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  line-height: 1.6;
  color: var(--color-text);
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}
.code-copy {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  transition: color var(--transition);
}
.code-copy:hover { color: var(--color-text); }
</style>
