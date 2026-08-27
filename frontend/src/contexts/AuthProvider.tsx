import { useEffect, useState, type ReactNode } from 'react'
import { authService } from '../services/auth'
import { AuthContext, type AuthContextType } from './AuthContext'
import type { LoginCredentials, User } from '../types/auth'

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    let isMounted = true

    async function checkAuthSession() {
      try {
        const currentUser = await authService.getMe()
        if (isMounted) {
          setUser(currentUser)
        }
      } catch {
        if (isMounted) {
          setUser(null)
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void checkAuthSession()

    return () => {
      isMounted = false
    }
  }, [])

  const login = async (credentials: LoginCredentials): Promise<void> => {
    const response = await authService.login(credentials)
    setUser(response.user)
  }

  const logout = async (): Promise<void> => {
    try {
      await authService.logout()
    } finally {
      setUser(null)
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: Boolean(user),
    isLoading,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
