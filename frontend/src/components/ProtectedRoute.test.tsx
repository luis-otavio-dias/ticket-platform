import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { ProtectedRoute } from './ProtectedRoute'
import { AuthContext, type AuthContextType } from '../contexts/AuthContext'

function renderWithAuth(
  ui: React.ReactNode,
  authValues: Partial<AuthContextType>,
  initialRoute = '/dashboard'
) {
  const mockAuthContext: AuthContextType = {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    ...authValues,
  }

  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <AuthContext.Provider value={mockAuthContext}>
        <Routes>
          <Route path="/login" element={<div>Tela de Login</div>} />
          <Route path="/dashboard" element={ui} />
        </Routes>
      </AuthContext.Provider>
    </MemoryRouter>
  )
}

describe('ProtectedRoute', () => {
  it('renders loading state when isLoading is true', () => {
    renderWithAuth(
      <ProtectedRoute>
        <div>Conteúdo Protegido</div>
      </ProtectedRoute>,
      { isLoading: true, isAuthenticated: false }
    )

    expect(screen.getByRole('status', { name: /carregando/i })).toBeInTheDocument()
    expect(screen.queryByText('Conteúdo Protegido')).not.toBeInTheDocument()
  })

  it('redirects to /login when unauthenticated and not loading', () => {
    renderWithAuth(
      <ProtectedRoute>
        <div>Conteúdo Protegido</div>
      </ProtectedRoute>,
      { isLoading: false, isAuthenticated: false }
    )

    expect(screen.getByText('Tela de Login')).toBeInTheDocument()
    expect(screen.queryByText('Conteúdo Protegido')).not.toBeInTheDocument()
  })

  it('renders protected content when authenticated', () => {
    renderWithAuth(
      <ProtectedRoute>
        <div>Conteúdo Protegido</div>
      </ProtectedRoute>,
      {
        isLoading: false,
        isAuthenticated: true,
        user: { id: 1, email: 'test@example.com', name: 'User', role: 'CUSTOMER' },
      }
    )

    expect(screen.getByText('Conteúdo Protegido')).toBeInTheDocument()
  })
})
