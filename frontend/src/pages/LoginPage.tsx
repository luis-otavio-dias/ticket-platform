import { useState, type FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { ApiError } from '../services/api'

export function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const [email, setEmail] = useState<string>('')
  const [password, setPassword] = useState<string>('')
  const [showPassword, setShowPassword] = useState<boolean>(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)

  const validateForm = (): boolean => {
    if (!email.trim()) {
      setErrorMessage('Por favor, informe seu e-mail.')
      return false
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email.trim())) {
      setErrorMessage('Por favor, insira um endereço de e-mail válido.')
      return false
    }

    if (!password) {
      setErrorMessage('Por favor, informe sua senha.')
      return false
    }

    return true
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setErrorMessage(null)

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    try {
      await login({
        email: email.trim(),
        password,
      })
      navigate('/')
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        if (err.statusCode === 401) {
          setErrorMessage('E-mail ou senha incorretos.')
        } else {
          setErrorMessage(err.message || 'Erro ao realizar login. Tente novamente.')
        }
      } else {
        setErrorMessage('Não foi possível conectar ao servidor. Verifique sua conexão.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col font-body-md text-body-md antialiased bg-data-pattern text-on-surface">
      {/* TopNavBar */}
      <header className="bg-background/80 backdrop-blur-xl border-b border-white/10 shadow-2xl w-full z-50">
        <nav className="max-w-[1440px] mx-auto h-20 flex justify-between items-center px-container-padding-mobile md:px-container-padding-desktop">
          <div className="font-display-lg text-2xl md:text-3xl font-black tracking-tighter text-primary">
            CINEDEV
          </div>

          <div className="hidden md:flex gap-6 items-center">
            <a
              className="font-label-sm text-sm text-on-surface-variant hover:text-on-surface hover:bg-white/5 focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none transition-all duration-300 py-2 px-3 rounded"
              href="#filmes"
            >
              Filmes
            </a>
            <a
              className="font-label-sm text-sm text-on-surface-variant hover:text-on-surface hover:bg-white/5 focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none transition-all duration-300 py-2 px-3 rounded"
              href="#cinemas"
            >
              Cinemas
            </a>
            <a
              className="font-label-sm text-sm text-on-surface-variant hover:text-on-surface hover:bg-white/5 focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none transition-all duration-300 py-2 px-3 rounded"
              href="#ofertas"
            >
              Ofertas
            </a>
            <a
              className="font-label-sm text-sm text-on-surface-variant hover:text-on-surface hover:bg-white/5 focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none transition-all duration-300 py-2 px-3 rounded"
              href="#ajuda"
            >
              Ajuda
            </a>
          </div>

          <div className="flex items-center gap-4">
            <button
              type="button"
              className="hidden md:block font-label-sm text-sm text-on-surface-variant hover:text-on-surface focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none py-2 px-3 rounded transition-colors cursor-pointer"
            >
              Ver Catálogo
            </button>
            <Link
              to="/register"
              className="font-label-sm text-sm bg-primary text-on-primary px-6 py-2 rounded-full font-bold hover:bg-primary-fixed-dim focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background focus-visible:outline-none transition-colors cursor-pointer"
            >
              Criar Conta
            </Link>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-grow flex items-center justify-center px-container-padding-mobile md:px-container-padding-desktop py-stack-lg">
        <div className="glass-card rounded-xl w-full max-w-md p-stack-md flex flex-col gap-stack-sm my-auto">
          <div className="text-center mb-2">
            <h1 className="font-headline-lg text-2xl md:text-3xl font-bold text-on-surface mb-2">
              Acessar Conta
            </h1>
            <p className="font-body-md text-sm md:text-base text-on-surface-variant">
              Entre para gerenciar seus ingressos e sessões de cinema.
            </p>
          </div>

          {errorMessage && (
            <div
              role="alert"
              aria-live="polite"
              className="bg-error-container/20 border border-error/40 text-error p-3 rounded-lg text-sm flex items-start gap-2 animate-fadeIn"
            >
              <span className="material-symbols-outlined text-lg shrink-0">error</span>
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
            <div className="flex flex-col gap-2 text-left">
              <label
                className="font-label-sm text-sm text-on-surface-variant font-medium"
                htmlFor="email"
              >
                E-mail
              </label>
              <div className="relative">
                <span
                  aria-hidden="true"
                  className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-xl pointer-events-none"
                >
                  mail
                </span>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  disabled={isSubmitting}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="seu.email@exemplo.com"
                  className="w-full bg-surface-container-low border-0 border-b border-white/20 text-on-surface font-body-md text-base py-3 pl-10 pr-4 rounded-t focus:ring-0 input-glow focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none transition-all duration-300 placeholder:text-on-surface-variant/50 disabled:opacity-50"
                />
              </div>
            </div>

            <div className="flex flex-col gap-2 text-left">
              <div className="flex justify-between items-center">
                <label
                  className="font-label-sm text-sm text-on-surface-variant font-medium"
                  htmlFor="password"
                >
                  Senha
                </label>
                <a
                  className="font-label-sm text-xs md:text-sm text-primary hover:text-primary-fixed-dim focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none rounded-sm transition-colors"
                  href="#recuperar-senha"
                >
                  Esqueceu a senha?
                </a>
              </div>
              <div className="relative">
                <span
                  aria-hidden="true"
                  className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-xl pointer-events-none"
                >
                  lock
                </span>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={password}
                  disabled={isSubmitting}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-surface-container-low border-0 border-b border-white/20 text-on-surface font-body-md text-base py-3 pl-10 pr-12 rounded-t focus:ring-0 input-glow focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none transition-all duration-300 placeholder:text-on-surface-variant/50 disabled:opacity-50"
                />
                <button
                  type="button"
                  aria-label={showPassword ? 'Ocultar senha' : 'Exibir senha'}
                  disabled={isSubmitting}
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="w-11 h-11 absolute right-1 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface hover:bg-white/5 focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none rounded-md transition-colors cursor-pointer flex items-center justify-center"
                >
                  <span className="material-symbols-outlined text-xl">
                    {showPassword ? 'visibility' : 'visibility_off'}
                  </span>
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-primary hover:bg-primary-fixed-dim text-on-primary font-title-md font-bold text-base py-3.5 px-6 rounded-lg mt-3 btn-glow focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background focus-visible:outline-none transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div
                    role="status"
                    aria-label="Carregando"
                    className="w-5 h-5 border-2 border-on-primary/30 border-t-on-primary rounded-full animate-spin"
                  />
                  <span>Entrando...</span>
                </>
              ) : (
                <span>Entrar</span>
              )}
            </button>
          </form>

          <div className="text-center mt-2">
            <p className="font-body-md text-sm text-on-surface-variant">
              Ainda não possui uma conta?{' '}
              <Link
                to="/register"
                className="text-primary hover:text-primary-fixed-dim focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none rounded-sm transition-colors font-medium"
              >
                Cadastre-se
              </Link>
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-surface-container-lowest border-t border-white/5 w-full py-stack-md px-container-padding-mobile md:px-container-padding-desktop flex flex-col md:flex-row justify-between items-center gap-4 z-10 relative">
        <div className="font-display-lg text-lg md:text-xl font-black text-primary">
          CINEDEV
        </div>
        <div className="font-body-md text-xs md:text-sm text-on-surface-variant text-center md:text-left">
          © 2024 CINEDEV. Todos os direitos reservados.
        </div>
        <div className="flex flex-wrap justify-center gap-4 font-body-md text-xs md:text-sm">
          <a
            className="text-on-surface-variant hover:text-primary focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none rounded-sm transition-colors opacity-80 hover:opacity-100"
            href="#privacidade"
          >
            Política de Privacidade
          </a>
          <a
            className="text-on-surface-variant hover:text-primary focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none rounded-sm transition-colors opacity-80 hover:opacity-100"
            href="#termos"
          >
            Termos de Uso
          </a>
          <a
            className="text-on-surface-variant hover:text-primary focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none rounded-sm transition-colors opacity-80 hover:opacity-100"
            href="#cookies"
          >
            Cookies
          </a>
          <a
            className="text-on-surface-variant hover:text-primary focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none rounded-sm transition-colors opacity-80 hover:opacity-100"
            href="#suporte"
          >
            Suporte
          </a>
        </div>
      </footer>
    </div>
  )
}
