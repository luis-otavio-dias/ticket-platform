# CineDev — Plataforma de Gestão e Venda de Ingressos

Monorepo fullstack para gestão e venda de ingressos de cinema, integrando catálogo externo de filmes via TMDb (The Movie Database).

---

## 🛠️ Tecnologias e Arquitetura

- **Backend**: Python 3.12+, Django 5+, Django REST Framework, SimpleJWT com HttpOnly cookies, UV como gerenciador de pacotes e PostgreSQL.
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, React Router 7, Vitest e Testing Library.
- **Infraestrutura**: Docker Compose com serviços para PostgreSQL e backend em modo watch.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- [uv](https://docs.astral.sh/uv/) (gerenciador rápido de pacotes Python)
- [Node.js](https://nodejs.org/) (v20+) e npm
- [Docker](https://www.docker.com/) e Docker Compose (opcional para ambiente conteinerizado)

### 1. Via Docker Compose (Recomendado)
Para iniciar o banco de dados PostgreSQL e o backend:
```bash
cd backend
docker compose up -d
```
O backend estará disponível em `http://localhost:8001`.

### 2. Execução Local Manual

#### Backend
```bash
cd backend
uv sync
cp .env.example .env  # configure suas variáveis de ambiente
uv run python manage.py migrate
uv run python manage.py runserver 8001
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```
O frontend estará acessível em `http://localhost:5173`. O proxy do Vite redireciona chamadas `/api` automaticamente para `http://localhost:8001`.

---

## 🧪 Testes e Qualidade de Código

### Backend
```bash
cd backend
uv run pytest             # Suíte de testes unitários e de integração
uv run ruff check .       # Linter
uv run ruff format --check # Verificação de formatação
```

### Frontend
```bash
cd frontend
npm test -- --run         # Testes unitários e de componentes (Vitest)
npm run lint              # ESLint
```

---

## 🤖 Ferramentas de IA & Agentes (Opcional)

Este repositório suporta fluxos de trabalho assistidos por inteligência artificial (como Google Antigravity, OpenCode e Skills CLI). 

Para manter o repositório focado no código da aplicação e evitar poluição no histórico do Git com centenas de scripts auxiliares, dependências locais e caches de ferramentas, todas as pastas de agentes são **estritamente ignoradas pelo `.gitignore` na raiz**.

### Principais Agentes e Skills Utilizados:
- **Mentor**: Subagente técnico focado em questionar decisões de arquitetura e incentivar raciocínio crítico sem entregar respostas prontas.
- **Impeccable**: Especialista em auditoria visual, acessibilidade (WCAG), microinterações, tokens de design e refinamento de interfaces.
- **Grill-with-docs**: Validação rigorosa de especificações e planos de implementação contra documentações oficiais.
- **Implement**: Execução de passos técnicos baseados em planos estruturados.

### Como instalar/configurar localmente:
Caso clone o repositório em uma nova máquina ou deseje reproduzir o ecossistema de skills no seu ambiente:

```bash
# Instalação de skills via CLI
npx skills add mattpocock/skills/grill-with-docs
npx skills add mattpocock/skills/implement
```

As pastas locais geradas (`.agent/`, `.agents/`, `.opencode/`, `.impeccable/`, `skills-lock.json`) permanecerão disponíveis para os agentes no seu computador sem interferir no controle de versão.
