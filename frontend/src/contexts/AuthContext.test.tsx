import { render, screen, waitFor, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { AuthProvider, useAuth } from './index'
import { authService } from '../services/auth'
import type { User } from '../types/auth'

vi.mock('../services/auth', () => ({
  authService: {
    getMe: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
  },
}))

function ConsumerComponent() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth()

  return (
    <div>
      <div data-testid="loading">{String(isLoading)}</div>
      <div data-testid="auth">{String(isAuthenticated)}</div>
      <div data-testid="user-email">{user?.email || 'none'}</div>
      <button
        onClick={() => void login({ email: 'user@example.com', password: 'password123' })}
      >
        Trigger Login
      </button>
      <button onClick={() => void logout()}>Trigger Logout</button>
    </div>
  )
}

describe('AuthContext', () => {
  const mockUser: User = {
    id: 1,
    email: 'user@example.com',
    name: 'Alice',
    role: 'CUSTOMER',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('hydrates user on mount when getMe succeeds', async () => {
    vi.mocked(authService.getMe).mockResolvedValue(mockUser)

    render(
      <AuthProvider>
        <ConsumerComponent />
      </AuthProvider>
    )

    expect(screen.getByTestId('loading')).toHaveTextContent('true')

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false')
      expect(screen.getByTestId('auth')).toHaveTextContent('true')
      expect(screen.getByTestId('user-email')).toHaveTextContent('user@example.com')
    })
  })

  it('sets user to null and isLoading to false when getMe fails', async () => {
    vi.mocked(authService.getMe).mockRejectedValue(new Error('Unauthorized'))

    render(
      <AuthProvider>
        <ConsumerComponent />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false')
      expect(screen.getByTestId('auth')).toHaveTextContent('false')
      expect(screen.getByTestId('user-email')).toHaveTextContent('none')
    })
  })

  it('updates user state on successful login', async () => {
    vi.mocked(authService.getMe).mockRejectedValue(new Error('Unauthorized'))
    vi.mocked(authService.login).mockResolvedValue({ user: mockUser })

    render(
      <AuthProvider>
        <ConsumerComponent />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false')
    })

    const loginButton = screen.getByRole('button', { name: /trigger login/i })
    await act(async () => {
      loginButton.click()
    })

    await waitFor(() => {
      expect(screen.getByTestId('auth')).toHaveTextContent('true')
      expect(screen.getByTestId('user-email')).toHaveTextContent('user@example.com')
    })
  })

  it('clears user state on logout', async () => {
    vi.mocked(authService.getMe).mockResolvedValue(mockUser)
    vi.mocked(authService.logout).mockResolvedValue(undefined)

    render(
      <AuthProvider>
        <ConsumerComponent />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('auth')).toHaveTextContent('true')
    })

    const logoutButton = screen.getByRole('button', { name: /trigger logout/i })
    await act(async () => {
      logoutButton.click()
    })

    await waitFor(() => {
      expect(screen.getByTestId('auth')).toHaveTextContent('false')
      expect(screen.getByTestId('user-email')).toHaveTextContent('none')
    })
  })

  it('throws an error when useAuth is used outside AuthProvider', () => {
    expect(() => render(<ConsumerComponent />)).toThrow(
      'useAuth must be used within an AuthProvider'
    )
  })
})
