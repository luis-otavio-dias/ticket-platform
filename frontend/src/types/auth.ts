export type UserRole = 'ORGANIZER' | 'CUSTOMER' | 'RECEPTIONIST'

export interface User {
  id: number
  email: string
  name: string
  role: UserRole
}

export interface AuthResponse {
  user: User
}

export interface LoginCredentials {
  email: string
  password: string
  [key: string]: string
}

export interface RefreshResponse {
  detail: string
}

export interface ApiFieldError {
  [key: string]: string | string[]
}

