const BASE = ''

function getToken(): string | null {
  return localStorage.getItem('bm_token')
}

export function clearToken(): void {
  localStorage.removeItem('bm_token')
  localStorage.removeItem('bm_user')
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, { ...options, headers })

  if (res.status === 401) {
    clearToken()
    window.location.href = '/login'
    throw new Error('Unauthenticated')
  }
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(detail?.detail || res.statusText)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}
