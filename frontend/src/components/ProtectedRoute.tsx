import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import type { ReactNode } from 'react'

interface ProtectedRouteProps {
  children?: ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#0e0e0e] text-[#e5e2e1]">
        <div
          role="status"
          aria-label="Carregando"
          className="w-10 h-10 border-4 border-primary/20 border-t-primary rounded-full animate-spin mb-4"
        />
        <p className="text-sm font-label-sm text-on-surface-variant">Carregando...</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children ? <>{children}</> : <Outlet />
}
