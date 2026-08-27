import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { LoginPage } from './LoginPage'
import { AuthContext, type AuthContextType } from '../contexts/AuthContext'
import { ApiError } from '../services/api'

const mockNavigate = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

function renderLoginPage(authContextOverrides: Partial<AuthContextType> = {}) {
  const mockAuthContext: AuthContextType = {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    login: vi.fn().mockResolvedValue(undefined),
    logout: vi.fn().mockResolvedValue(undefined),
    ...authContextOverrides,
  }

  const result = render(
    <MemoryRouter>
      <AuthContext.Provider value={mockAuthContext}>
        <LoginPage />
      </AuthContext.Provider>
    </MemoryRouter>
  )

  return {
    ...result,
    mockAuthContext,
  }
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders all form elements, labels and CINEDEV brand', () => {
    renderLoginPage()

    expect(screen.getAllByText('CINEDEV')).toHaveLength(2)
    expect(screen.getByRole('heading', { name: /acessar conta/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/e-mail/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^senha$/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /^entrar$/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /exibir senha/i })).toBeInTheDocument()
  })

  it('toggles password input type between "password" and "text"', async () => {
    const user = userEvent.setup()
    renderLoginPage()

    const passwordInput = screen.getByLabelText(/^senha$/i) as HTMLInputElement
    expect(passwordInput.type).toBe('password')

    const toggleButton = screen.getByRole('button', { name: /exibir senha/i })
    await user.click(toggleButton)

    expect(passwordInput.type).toBe('text')
    expect(screen.getByRole('button', { name: /ocultar senha/i })).toBeInTheDocument()

    await user.click(toggleButton)
    expect(passwordInput.type).toBe('password')
  })

  it('shows validation error when submitting with empty email', async () => {
    const user = userEvent.setup()
    const { mockAuthContext } = renderLoginPage()

    const submitButton = screen.getByRole('button', { name: /^entrar$/i })
    await user.click(submitButton)

    expect(screen.getByRole('alert')).toHaveTextContent('Por favor, informe seu e-mail.')
    expect(mockAuthContext.login).not.toHaveBeenCalled()
  })

  it('shows validation error when submitting with an invalid email format', async () => {
    const user = userEvent.setup()
    const { mockAuthContext } = renderLoginPage()

    const emailInput = screen.getByLabelText(/e-mail/i)
    const passwordInput = screen.getByLabelText(/^senha$/i)
    const submitButton = screen.getByRole('button', { name: /^entrar$/i })

    await user.type(emailInput, 'usuario.com')
    await user.type(passwordInput, 'secret123')
    await user.click(submitButton)

    expect(screen.getByRole('alert')).toHaveTextContent('Por favor, insira um endereço de e-mail válido.')
    expect(mockAuthContext.login).not.toHaveBeenCalled()
  })

  it('shows validation error when submitting with empty password', async () => {
    const user = userEvent.setup()
    const { mockAuthContext } = renderLoginPage()

    const emailInput = screen.getByLabelText(/e-mail/i)
    const submitButton = screen.getByRole('button', { name: /^entrar$/i })

    await user.type(emailInput, 'user@example.com')
    await user.click(submitButton)

    expect(screen.getByRole('alert')).toHaveTextContent('Por favor, informe sua senha.')
    expect(mockAuthContext.login).not.toHaveBeenCalled()
  })

  it('calls login and navigates to / upon successful submission', async () => {
    const user = userEvent.setup()
    const loginMock = vi.fn().mockResolvedValue(undefined)
    renderLoginPage({ login: loginMock })

    const emailInput = screen.getByLabelText(/e-mail/i)
    const passwordInput = screen.getByLabelText(/^senha$/i)
    const submitButton = screen.getByRole('button', { name: /^entrar$/i })

    await user.type(emailInput, 'user@example.com')
    await user.type(passwordInput, 'ValidPassword123!')
    await user.click(submitButton)

    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 'ValidPassword123!',
      })
      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })

  it('allows submitting the form via Enter key on the password input', async () => {
    const user = userEvent.setup()
    const loginMock = vi.fn().mockResolvedValue(undefined)
    renderLoginPage({ login: loginMock })

    const emailInput = screen.getByLabelText(/e-mail/i)
    const passwordInput = screen.getByLabelText(/^senha$/i)

    await user.type(emailInput, 'user@example.com')
    await user.type(passwordInput, 'ValidPassword123!{Enter}')

    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 'ValidPassword123!',
      })
      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })

  it('displays generic error message when API returns 401 unauthorized', async () => {
    const user = userEvent.setup()
    const loginMock = vi.fn().mockRejectedValue(new ApiError(401, 'No active account found with the given credentials'))
    renderLoginPage({ login: loginMock })

    const emailInput = screen.getByLabelText(/e-mail/i)
    const passwordInput = screen.getByLabelText(/^senha$/i)
    const submitButton = screen.getByRole('button', { name: /^entrar$/i })

    await user.type(emailInput, 'wrong@example.com')
    await user.type(passwordInput, 'wrongpassword')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('E-mail ou senha incorretos.')
    })
  })

  it('displays connection error message when request fails unexpectedly', async () => {
    const user = userEvent.setup()
    const loginMock = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'))
    renderLoginPage({ login: loginMock })

    const emailInput = screen.getByLabelText(/e-mail/i)
    const passwordInput = screen.getByLabelText(/^senha$/i)
    const submitButton = screen.getByRole('button', { name: /^entrar$/i })

    await user.type(emailInput, 'user@example.com')
    await user.type(passwordInput, 'password123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Não foi possível conectar ao servidor. Verifique sua conexão.')
    })
  })

  it('disables submit button and fields while submitting', async () => {
    const user = userEvent.setup()
    let resolveLogin: () => void = () => {}
    const loginMock = vi.fn().mockReturnValue(
      new Promise<void>((resolve) => {
        resolveLogin = resolve
      })
    )

    renderLoginPage({ login: loginMock })

    const emailInput = screen.getByLabelText(/e-mail/i)
    const passwordInput = screen.getByLabelText(/^senha$/i)
    const submitButton = screen.getByRole('button', { name: /^entrar$/i })

    await user.type(emailInput, 'user@example.com')
    await user.type(passwordInput, 'password123')
    await user.click(submitButton)

    expect(screen.getByText('Entrando...')).toBeInTheDocument()
    expect(emailInput).toBeDisabled()
    expect(passwordInput).toBeDisabled()

    resolveLogin()

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })
})
