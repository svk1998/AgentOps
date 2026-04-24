import { useConfirm as usePrimeConfirm } from 'primevue/useconfirm'

/**
 * App-wide confirmation dialog.
 *
 *   const confirm = useConfirm()
 *
 *   confirm.danger({
 *     message: 'Deactivate this user? They will no longer be able to sign in.',
 *     accept:  () => userService.remove(id),
 *   })
 *
 *   await confirm.ask({ message: '...' }) // promise form
 *
 * Thin facade over PrimeVue's `useConfirm()` so callers don't need to
 * remember the full `confirm.require({...})` API and we can swap the
 * underlying dialog for a custom amber-themed one in the future
 * without touching call sites.
 *
 * Must be called inside a component's `setup()` / `<script setup>`.
 */
export function useConfirm() {
  const primeConfirm = usePrimeConfirm()

  /** Present a confirmation dialog and run `accept` if the user confirms. */
  function show({
    message,
    header = 'Confirm',
    accept = () => {},
    reject = () => {},
    acceptLabel = 'Confirm',
    rejectLabel = 'Cancel',
    severity = 'info', // info | danger | warn
  } = {}) {
    primeConfirm.require({
      message,
      header,
      accept,
      reject,
      acceptLabel,
      rejectLabel,
      acceptProps: severity === 'danger' ? { severity: 'danger' } : undefined,
      rejectProps: { text: true },
    })
  }

  /** Convenience: present destructive confirm, returns Promise<boolean>. */
  function ask(opts) {
    return new Promise((resolve) => {
      show({
        ...opts,
        accept: () => { opts.accept?.(); resolve(true) },
        reject: () => { opts.reject?.(); resolve(false) },
      })
    })
  }

  /** Shortcut for destructive actions (delete / deactivate). */
  function danger(opts) {
    return show({
      severity: 'danger',
      header: 'Are you sure?',
      acceptLabel: 'Delete',
      ...opts,
    })
  }

  return { show, ask, danger }
}
