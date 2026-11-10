const API_URL = import.meta.env.VITE_API_URL || '/api/v1'
export const UNAUTHORIZED_EVENT = 'reqlens:unauthorized'

export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message) }
}

function errorMessage(detail: unknown): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const messages = detail.map(item => {
      if (!item || typeof item !== 'object') return ''
      const issue = item as { loc?: unknown[]; msg?: string }
      const field = issue.loc?.at(-1)
      return `${typeof field === 'string' ? `${field}: ` : ''}${issue.msg || 'Invalid value'}`
    }).filter(Boolean)
    if (messages.length) return messages.join('. ')
  }
  return 'Something went wrong'
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('reqlens_token')
  const headers = new Headers(init.headers)
  if (!(init.body instanceof FormData)) headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)
  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, { ...init, headers })
  } catch {
    throw new ApiError('Cannot reach the server. Check your connection and try again.', 0)
  }
  if (!response.ok) {
    let message = 'Something went wrong'
    try { message = errorMessage((await response.json()).detail) } catch { /* non-json response */ }
    if (response.status === 401 && token) {
      localStorage.removeItem('reqlens_token')
      window.dispatchEvent(new Event(UNAUTHORIZED_EVENT))
    }
    throw new ApiError(message, response.status)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const json = (method: string, body?: unknown): RequestInit => ({ method, body: body === undefined ? undefined : JSON.stringify(body) })

