import { ref } from 'vue'

/**
 * Wraps any async function with loading + error state.
 * Great for form submissions, delete actions, etc.
 *
 * Usage:
 *   const { execute, loading, error } = useAsync(userStore.deleteUser)
 *   await execute(userId)
 */
export function useAsync(fn) {
  const loading = ref(false)
  const error   = ref(null)

  async function execute(...args) {
    loading.value = true
    error.value   = null
    try {
      return await fn(...args)
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return { execute, loading, error }
}
