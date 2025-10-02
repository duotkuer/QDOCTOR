# QDOCTOR

QDOCTOR is an application scaffold for a doctor/patient assistant system. The repository contains a Python-based Backend and a Frontend. This README describes the overall project, how to set up both parts locally, and common housekeeping notes.

## Repository layout
- Backend/ — Python API, services, and server code (primary application logic)
- Frontend/ — Optional UI assets (React/Vue/other) if present
- vector_store/ — Local vector/cache storage (ignored by git)

## Goals
- Provide a minimal, production-approachable backend for clinical assistant features.
- Optionally serve a frontend UI that interacts with the backend API.
- Keep secrets out of source control and provide clear local development steps.

## Quickstart — Backend (Python)
Prerequisites:
- Python 3.9+
- pip

Steps:
1. Open a terminal and change directory:
   - cd Backend
2. Create and activate a virtual environment:
   - Windows: python -m venv .venv && .\.venv\Scripts\Activate
   - macOS/Linux: python -m venv .venv && source .venv/bin/activate
3. Install dependencies:
   - pip install -r requirements.txt
4. Configure environment:
   - Copy `.env.example` to `.env` and fill required values.
   - Do NOT commit `.env`.
5. Start the backend:
   - Follow Backend's entrypoint (e.g., uvicorn app.main:app --reload) or the command documented in Backend.
6. Verify:
   - Open the API URL (e.g., http://localhost:8000) or run provided health checks.

## Quickstart — Frontend (if present)
Prerequisites:
- Node.js (LTS) and npm/yarn

Steps:
1. cd Frontend
2. Install packages:
   - npm install or yarn
3. Set any frontend environment variables (see Frontend/.env.example)
4. Start the dev server:
   - npm start or yarn start
5. The frontend should proxy to the backend or be configured to call backend API endpoints.

## Environment & Secrets
- All environment files are ignored by .gitignore. Use `.env.example` as a template.
- Never commit secrets, API keys, or private credentials.
- For CI, use your provider's secret management.

## Common housekeeping
- If there is an accidental nested git repository at Backend/.git, remove it to avoid problems:
  - Delete the Backend/.git directory (or use any provided script, e.g., scripts/remove-backend-git.ps1).
- The vector_store/ directory is ignored; clear it locally if you need to reset caches.
- Keep the top-level .git repository as the single source of truth.

## Testing & Linting
- Run backend tests where provided (e.g., pytest in Backend).
- Run frontend tests via npm/yarn test if applicable.
- Use linters (flake8, black for Python; ESLint/Prettier for JS) as configured.

## Development workflow
- Branch from main for features/fixes.
- Open pull requests with clear descriptions and tests where appropriate.
- Keep commits focused and atomic.

## Troubleshooting
- Backend won't start: verify Python version, virtualenv activation, and .env variables.
- Frontend can't reach backend: check CORS settings, proxy configuration, and backend port.
- Unexpected nested .git: remove Backend/.git and reinitialize only if you intend a sub-repo.

## Contributing
- Add issues for changes and link design/behavior proposals.
- Follow coding standards used in Backend and Frontend.
- Include tests for new features and document behavior.

## License
Add your project license here (e.g., MIT, Apache-2.0). Replace this section with the chosen license text or a link to LICENSE.

## Contact
For questions or help, add maintainer contact information or link to your issue tracker.
