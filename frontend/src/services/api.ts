import type { ApiFieldError } from '../types/auth'

export class ApiError extends Error {
  readonly statusCode: number
  readonly fieldErrors?: ApiFieldError

  constructor(statusCode: number, message: string, fieldErrors?: ApiFieldError) {
    super(message)
    this.name = 'ApiError'
    this.statusCode = statusCode
    this.fieldErrors = fieldErrors
  }
}

export type JsonPrimitive = string | number | boolean | null | undefined

export interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: BodyInit | Record<string, JsonPrimitive | JsonPrimitive[]> | null
  skipAuthRefresh?: boolean
}


let isRefreshing = false
let refreshPromise: Promise<boolean> | null = null

async function performTokenRefresh(): Promise<boolean> {
  if (isRefreshing && refreshPromise) {
    return refreshPromise
  }

  isRefreshing = true
  refreshPromise = (async () => {
    try {
      const res = await fetch('/api/auth/refresh/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      })
      return res.ok
    } catch {
      return false
    } finally {
      isRefreshing = false
      refreshPromise = null
    }
  })()

  return refreshPromise
}

export async function apiFetch<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { body, headers, skipAuthRefresh, ...customConfig } = options

  const requestHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    ...headers,
  }

  const config: RequestInit = {
    ...customConfig,
    headers: requestHeaders,
    credentials: 'include',
  }

  if (body !== undefined && body !== null) {
    if (
      typeof body === 'string' ||
      body instanceof FormData ||
      body instanceof URLSearchParams ||
      body instanceof Blob
    ) {
      config.body = body
    } else {
      config.body = JSON.stringify(body)
    }
  }

  let response = await fetch(endpoint, config)

  if (
    response.status === 401 &&
    !skipAuthRefresh &&
    !endpoint.includes('/api/auth/login/') &&
    !endpoint.includes('/api/auth/refresh/')
  ) {
    const refreshed = await performTokenRefresh()
    if (refreshed) {
      response = await fetch(endpoint, config)
    }
  }

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`
    let fieldErrors: ApiFieldError | undefined

    try {
      const errorData = (await response.json()) as Record<string, string | string[]>
      if (typeof errorData.detail === 'string') {
        message = errorData.detail
      } else if (typeof errorData.message === 'string') {
        message = errorData.message
      } else if (errorData) {
        fieldErrors = errorData
        const firstKey = Object.keys(errorData)[0]
        if (firstKey) {
          const val = errorData[firstKey]
          message = Array.isArray(val) ? val.join(', ') : String(val)
        }
      }
    } catch {
      // Non-JSON response body
    }

    throw new ApiError(response.status, message, fieldErrors)
  }

  if (response.status === 204) {
    return {} as T
  }

  return (await response.json()) as T
}
