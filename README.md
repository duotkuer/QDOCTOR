# QDOCTOR

QDOCTOR is an application scaffold for a doctor/patient assistant system. The repository contains a Python-based Backend and a Frontend. This README describes the overall project, how to set up both parts locally, and common housekeeping notes.

## Repository layout
- Backend/ — Python API, services, and server code (primary application logic)
- Frontend/ — Optional UI assets (React/Vue/other) if present
- vector_store/ — Local vector/cache storage

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

## Quickstart — Frontend (Next.js)
Prerequisites:
- Node.js (LTS) and npm or yarn

Development:
1. cd Frontend
2. Install packages:
   - npm install
3. Start dev server:
   - npm run dev

Production build & run (fixes the ".next" missing error):
1. cd Frontend
2. Install dependencies (if not already done):
   - npm install
3. Build the app (this creates the .next directory):
   - npm run build
4. Start the production server:
   - npm start
   - OR run: npx next start -p <PORT>

Troubleshooting the error "Could not find a production build in the '.next' directory":
- Cause: You attempted to run a production server (next start or npm start) without first running next build.
- Fix:
  1. From the Frontend folder run npm install && npm run build.
  2. Then run npm start (or npx next start).
- If you have a custom start script, ensure it runs next start (not next dev) and that build completes successfully.
- If using a CI/CD pipeline, ensure your pipeline runs npm ci/install and npm run build before starting or deploying.

Automated convenience (Windows):
- See scripts/build-frontend.ps1 (in scripts/) to build and optionally start the Frontend on Windows.

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


## Quickstart — Docker

This project provides Dockerfiles for both the Backend (Python/FastAPI) and Frontend (Next.js/TypeScript) services, along with a Docker Compose configuration for easy setup.

### Requirements
- Docker and Docker Compose installed on your system
- Backend requires Python 3.11 (handled by the Dockerfile)
- Frontend uses Node.js version 22.13.1 (set in the Dockerfile)

### Environment Variables
- The Backend service expects a `.env` file in `Backend/` (see `Backend/.env.example` for required variables)
- The Frontend service can use a `.env` file in `Frontend/` (uncomment `env_file` in the compose file if needed)

### Build and Run
1. Ensure your environment files are set up:
   - Copy `Backend/.env.example` to `Backend/.env` and fill in required values
   - (Optional) Add `Frontend/.env` if your frontend needs environment variables
2. From the project root, run:
   ```sh
   docker compose up --build
   ```
   This will build and start both services.

### Ports
- Backend (FastAPI): exposed on **8000** (`http://localhost:8000`)
- Frontend (Next.js): exposed on **3000** (`http://localhost:3000`)

### Special Configuration
- The Backend Dockerfile installs system dependencies for PDF processing (e.g., `poppler-utils`, `libjpeg-dev`)
- Both services run as non-root users for security
- The Backend mounts its `.env` file via the `env_file` directive in Compose
- Both services share a Docker network (`appnet`) for internal communication
- The Frontend depends on the Backend and will wait for it to be available

### Notes
- If you do not have a `Backend/.env` file, comment out the `env_file` line in the Compose file
- For custom database or additional services, extend the Compose file as needed

For troubleshooting and more details, see the sections above on local development and environment setup.

## License
MIT, Apache-2.0

## Contact
Email: duotkuerduot@gmail.com
