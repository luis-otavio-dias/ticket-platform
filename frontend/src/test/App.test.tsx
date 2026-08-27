import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import App from '../App'
import { authService } from '../services/auth'

vi.mock('../services/auth', () => ({
  authService: {
    getMe: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
  },
}))

describe('App Integration', () => {
  it('renders loading state and then redirects to /login when user is unauthenticated', async () => {
    vi.mocked(authService.getMe).mockRejectedValue(new Error('Unauthorized'))

    render(<App />)

    // Initial loading indicator
    expect(screen.getByRole('status', { name: /carregando/i })).toBeInTheDocument()

    // Redirects to /login
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /acessar conta/i })).toBeInTheDocument()
      expect(screen.getAllByText('CINEDEV').length).toBeGreaterThanOrEqual(1)
    })
  })
})

