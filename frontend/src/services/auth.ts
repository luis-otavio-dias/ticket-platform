import { apiFetch } from './api'
import type { AuthResponse, LoginCredentials, RefreshResponse, User } from '../types/auth'

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    return apiFetch<AuthResponse>('/api/auth/login/', {
      method: 'POST',
      body: credentials,
      skipAuthRefresh: true,
    })
  },

  async getMe(): Promise<User> {
    return apiFetch<User>('/api/auth/me/', {
      method: 'GET',
    })
  },

  async refreshToken(): Promise<RefreshResponse> {
    return apiFetch<RefreshResponse>('/api/auth/refresh/', {
      method: 'POST',
      skipAuthRefresh: true,
    })
  },

  async logout(): Promise<void> {
    return apiFetch<void>('/api/auth/logout/', {
      method: 'POST',
      skipAuthRefresh: true,
    })
  },
}
