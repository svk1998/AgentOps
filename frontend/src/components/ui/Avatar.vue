<template>
  <div
    class="avatar"
    :class="`avatar--${size}`"
    :style="{ background: bg, color: fg }"
    :title="name"
    role="img"
    :aria-label="name"
  >
    <img v-if="src && !imgError" :src="src" :alt="name" class="avatar__img" @error="imgError = true" />
    <span v-else class="avatar__initials">{{ initials }}</span>
    <span v-if="status" class="avatar__status" :class="`avatar__status--${status}`" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  name:   { type: String, default: '' },
  src:    { type: String, default: null },
  size:   { type: String, default: 'md' }, // xs | sm | md | lg | xl
  tone:   { type: String, default: 'accent' }, // accent | info | ok | err | neutral
  /** Optional status pip at the bottom-right: ok | warn | err | info */
  status: { type: String, default: null },
})

const imgError = ref(false)

const initials = computed(() => {
  const src = props.name || ''
  return (
    src.split(/[\s@]/).map(s => s[0]).filter(Boolean).slice(0, 2).join('').toUpperCase()
    || '?'
  )
})

const TONES = {
  accent:  { bg: 'var(--accent-dim)', fg: 'var(--accent)' },
  info:    { bg: 'var(--info-dim)',   fg: 'var(--info)' },
  ok:      { bg: 'var(--ok-dim)',     fg: 'var(--ok)' },
  err:     { bg: 'var(--err-dim)',    fg: 'var(--err)' },
  neutral: { bg: 'var(--bg-elev-2)',  fg: 'var(--text-dim)' },
}
const bg = computed(() => TONES[props.tone]?.bg ?? TONES.accent.bg)
const fg = computed(() => TONES[props.tone]?.fg ?? TONES.accent.fg)
</script>

<style scoped>
.avatar {
  position: relative;
  display: inline-grid;
  place-items: center;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  font-family: var(--mono);
  font-weight: 700;
  user-select: none;
}

.avatar--xs { width: 18px; height: 18px; font-size: 8px; }
.avatar--sm { width: 22px; height: 22px; font-size: 9.5px; }
.avatar--md { width: 28px; height: 28px; font-size: 11px; }
.avatar--lg { width: 40px; height: 40px; font-size: 14px; }
.avatar--xl { width: 52px; height: 52px; font-size: 18px; }

.avatar__img { width: 100%; height: 100%; object-fit: cover; }
.avatar__initials { line-height: 1; }

.avatar__status {
  position: absolute;
  right: -1px;
  bottom: -1px;
  width: 28%;
  height: 28%;
  min-width: 6px;
  min-height: 6px;
  border-radius: 50%;
  border: 2px solid var(--panel);
  background: var(--text-faint);
}
.avatar__status--ok   { background: var(--ok); }
.avatar__status--warn { background: var(--warn); }
.avatar__status--err  { background: var(--err); }
.avatar__status--info { background: var(--info); }
</style>
