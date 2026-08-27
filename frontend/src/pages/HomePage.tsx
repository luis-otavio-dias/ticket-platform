import { useAuth } from '../contexts/AuthContext'

export function HomePage() {
  const { user, logout } = useAuth()

  const roleLabels: Record<string, string> = {
    ORGANIZER: 'Organizador',
    RECEPTIONIST: 'Portaria',
    CUSTOMER: 'Cliente',
  }

  const formattedRole = user?.role ? (roleLabels[user.role] || user.role) : '-'

  return (
    <div className="min-h-screen flex flex-col font-body-md text-on-surface bg-background antialiased">
      {/* TopNavBar */}
      <header className="bg-background/80 backdrop-blur-xl border-b border-white/10 shadow-2xl w-full z-50">
        <nav className="max-w-[1440px] mx-auto h-20 flex justify-between items-center px-container-padding-mobile md:px-container-padding-desktop">
          <div className="font-display-lg text-2xl md:text-3xl font-black tracking-tighter text-primary">
            CINEDEV
          </div>

          <div className="flex items-center gap-4">
            <span className="text-sm font-label-sm text-on-surface-variant hidden sm:inline">
              Olá, <strong className="text-on-surface">{user?.name || user?.email}</strong> (
              <span className="text-primary font-medium">{formattedRole}</span>)
            </span>
            <button
              type="button"
              onClick={() => void logout()}
              className="font-label-sm text-sm border border-white/20 text-on-surface px-4 py-2 rounded-full hover:bg-white/10 focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none transition-colors cursor-pointer"
            >
              Sair
            </button>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-grow flex items-center justify-center px-container-padding-mobile md:px-container-padding-desktop py-stack-lg bg-data-pattern">
        <div className="glass-card rounded-xl w-full max-w-lg p-stack-md flex flex-col gap-6 text-center my-auto shadow-2xl">
          <div>
            <h1 className="font-headline-lg text-2xl md:text-3xl font-bold text-on-surface mb-2">
              Bem-vindo ao CINEDEV
            </h1>
            <p className="font-body-md text-sm md:text-base text-on-surface-variant">
              Você está autenticado no sistema.
            </p>
          </div>

          <div className="bg-surface-container/70 border border-white/10 rounded-xl p-5 text-left flex flex-col gap-3">
            <div className="flex justify-between items-center text-sm border-b border-white/5 pb-2">
              <span className="text-on-surface-variant font-medium">Nome:</span>
              <span className="font-semibold text-on-surface">{user?.name || '-'}</span>
            </div>
            <div className="flex justify-between items-center text-sm border-b border-white/5 pb-2">
              <span className="text-on-surface-variant font-medium">E-mail:</span>
              <span className="font-semibold text-on-surface">{user?.email}</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-on-surface-variant font-medium">Perfil de Acesso:</span>
              <span className="font-semibold text-primary px-2.5 py-1 bg-primary/10 border border-primary/20 rounded-md text-xs tracking-wide uppercase">
                {formattedRole}
              </span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-surface-container-lowest border-t border-white/5 w-full py-stack-md px-container-padding-mobile md:px-container-padding-desktop flex flex-col md:flex-row justify-between items-center gap-4 z-10">
        <div className="font-display-lg text-lg md:text-xl font-black text-primary">CINEDEV</div>
        <div className="font-body-md text-xs md:text-sm text-on-surface-variant">
          © 2024 CINEDEV. Todos os direitos reservados.
        </div>
      </footer>
    </div>
  )
}
