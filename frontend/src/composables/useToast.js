import { useToast as usePrimeToast } from 'primevue/usetoast'

/**
 * App-wide toast notification system.
 *
 * Thin facade over PrimeVue's `useToast()` that keeps the original
 * `toast.success / error / info / warning(msg)` API, so the migration
 * to PrimeVue doesn't force every caller to relearn signatures.
 *
 * Must be called inside a component's `setup()` / `<script setup>`
 * (PrimeVue's toast service is injected at that point).
 */
export function useToast() {
  const toast = usePrimeToast()

  const show = (severity, message) =>
    toast.add({ severity, summary: message, life: 3500 })

  return {
    success: (msg) => show('success', msg),
    error:   (msg) => show('error',   msg),
    info:    (msg) => show('info',    msg),
    warning: (msg) => show('warn',    msg),
  }
}
