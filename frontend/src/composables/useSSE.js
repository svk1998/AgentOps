/**
 * Composable for Server-Sent Events.
 * Handles connection lifecycle, auto-cleanup on unmount, and reconnect logic.
 *
 * Usage:
 *   const { connect, disconnect, connected } = useSSE()
 *   connect(url, (data) => handleMessage(data), (err) => handleError(err))
 */
import { ref, onUnmounted } from 'vue'

export function useSSE() {
  const connected = ref(false)
  const error = ref(null)
  let es = null
  let retries = 0
  const MAX_RETRIES = 3

  function connect(url, onMessage, onError) {
    disconnect()
    error.value = null

    es = new EventSource(url)

    es.onopen = () => {
      connected.value = true
      retries = 0
    }

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch {
        onMessage(event.data)
      }
    }

    es.onerror = () => {
      connected.value = false
      if (retries < MAX_RETRIES) {
        retries++
        const delay = Math.min(1000 * 2 ** retries, 10000)
        setTimeout(() => connect(url, onMessage, onError), delay)
      } else {
        error.value = 'Connection lost'
        onError?.('Connection lost after retries')
        disconnect()
      }
    }
  }

  function disconnect() {
    if (es) {
      es.close()
      es = null
    }
    connected.value = false
  }

  onUnmounted(disconnect)

  return { connect, disconnect, connected, error }
}
