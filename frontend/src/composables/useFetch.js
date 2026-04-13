import { ref, isRef, watchEffect } from 'vue'
import api from '@/services/api'

/**
 * Generic composable for fetching data from the API.
 * Supports reactive URLs — if url is a ref, it re-fetches on change.
 *
 * Usage:
 *   const { data, loading, error, refetch } = useFetch('/users')
 *   const { data } = useFetch(computed(() => `/users/${userId.value}`))
 */
export function useFetch(url, options = {}) {
  const data    = ref(null)
  const loading = ref(false)
  const error   = ref(null)

  async function fetch() {
    loading.value = true
    error.value   = null
    try {
      const resolvedUrl = isRef(url) ? url.value : url
      const res = await api.get(resolvedUrl, options)
      data.value = res.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
    } finally {
      loading.value = false
    }
  }

  // Re-fetch when reactive URL changes
  watchEffect(() => {
    if (isRef(url)) url.value // track dependency
    fetch()
  })

  return { data, loading, error, refetch: fetch }
}
