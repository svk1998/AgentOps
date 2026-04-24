import { ref, shallowRef, onMounted, watch } from 'vue'

/**
 * Standard data-fetching composable for all resource views.
 *
 *   const { data, error, loading, refetch } = useApi(
 *     () => agentService.list({ status: 'active' }),
 *   )
 *
 * Options:
 *   immediate   — run the fetcher on mount (default true). Set false if
 *                 you want the view to trigger manually.
 *   watchDeps   — reactive sources (refs / getter fns) that should
 *                 refetch when changed. Array of refs/getters.
 *   initialData — seed `data.value` so the view can render a skeleton
 *                 before the first response lands.
 *
 * The fetcher must return the raw axios response OR a Promise that
 * resolves to `{ data: ... }`. Both shapes work because resource
 * services (agentService, datasetService, etc.) return the axios
 * response directly.
 *
 * Errors are unwrapped to `error.value` as a string — FastAPI's
 * `detail` field is preferred, falling back to `message` / status.
 *
 * `refetch()` returns the fetched data for callers that want to await
 * it inline (e.g. after a successful mutation).
 */
export function useApi(fetcher, { immediate = true, watchDeps = [], initialData = null } = {}) {
  const data = shallowRef(initialData)
  const error = ref('')
  const loading = ref(false)

  async function refetch() {
    loading.value = true
    error.value = ''
    try {
      const res = await fetcher()
      // Accept both `axiosResponse` and already-unwrapped payloads.
      data.value = (res && Object.prototype.hasOwnProperty.call(res, 'data')) ? res.data : res
      return data.value
    } catch (e) {
      error.value =
        e?.response?.data?.detail ||
        e?.message ||
        `Request failed (HTTP ${e?.response?.status ?? '???'})`
      data.value = initialData
      throw e
    } finally {
      loading.value = false
    }
  }

  if (immediate) onMounted(refetch)

  if (watchDeps.length) {
    watch(watchDeps, () => { refetch() }, { deep: false })
  }

  return { data, error, loading, refetch }
}
