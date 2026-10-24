# InstrumentHub — Local Deployment and Operations

## Scope

This document covers local development and a Docker Compose deployment pattern. AWS deployment is intentionally deferred to a separate stage. This is not a production security review.

## Prerequisites

- Python version compatible with `pyproject.toml` (project baseline: Python 3.12 or later as configured).
- `uv` for Python dependency management.
- Node.js and npm for local frontend development.
- Docker Engine and Docker Compose plugin for container deployment.
- Optional physical instrument and the correct vendor driver/protocol documentation.

## Run the backend locally

From the repository root:

```bash
uv sync --all-groups
uv run uvicorn app.main:app --reload
```

Check the health endpoint configured in the current code. The project baseline has used:

```bash
curl -i http://127.0.0.1:8000/api/v1/health
```

Open `http://127.0.0.1:8000/docs` to inspect the running API contract.

## Run the frontend locally

```bash
cd frontend
npm ci
npm run dev
```

Use the frontend's configured environment variables and API base URL. If the frontend is served by Nginx in Compose, the browser should normally call a same-origin `/api` path and let Nginx proxy it to FastAPI.

## Docker Compose

First inspect `.env.example` and create a local `.env` with values suitable for development:

```bash
cp .env.example .env
docker compose config --quiet
docker compose up --build -d
docker compose ps
docker compose logs -f api frontend
```

The actual service names and published ports are defined by the checked-out `docker-compose.yml`. In the Stage 10 plan, the intended local endpoints are frontend `http://localhost:8080` and API `http://localhost:8200`; verify these values in the current Compose configuration before relying on them.

Stop services with:

```bash
docker compose down
```

Use `docker compose down -v` only if you intentionally want to delete named volumes and their stored database data.

## Optional Mailpit

Mailpit is a local SMTP sink for testing notification emails. It should be optional and should not deliver mail to real recipients. If the Compose file defines the `mail` profile:

```bash
docker compose --profile mail up -d mailpit
```

Set the API's SMTP host to the Compose service name, typically `mailpit`, and use the SMTP port exposed inside the Compose network (commonly `1025`). Disable TLS for the local sink only if the application settings support that option. Check the actual settings names in `app/core/config.py`.

## Serial hardware and COM ports

The serial instrument is attached to the host, not automatically to the container.

- Windows device names such as `COM3` are not directly usable inside a standard Linux container.
- For native Windows development, run the API on the host when direct COM access is required unless a tested device passthrough solution is in place.
- On Linux, a serial device may appear as `/dev/ttyUSB0` or `/dev/ttyACM0`; permissions and container device mappings must be explicitly configured.
- Do not publish serial ports to the network.
- Test simulator mode separately from physical hardware mode.

## Configuration and secrets

- Keep `.env` out of version control.
- Use non-production credentials locally.
- Never put passwords, tokens, private keys or cloud credentials into the image or repository.
- Do not expose PostgreSQL to untrusted networks.
- Use least-privilege database accounts and restrict CORS/allowed hosts for any public deployment.
- Set production debug mode off and configure logging/retention deliberately.

## Validation checklist

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy app
uv run pytest -q

cd frontend
npm ci
npm run lint
npm run build
```

Also validate Docker build and startup in an environment with Docker installed:

```bash
docker compose config --quiet
docker compose build
docker compose up -d
docker compose ps
```

A successful image build does not by itself prove that database migrations, WebSockets, serial hardware or all application workflows operate correctly.

## Demo data and benchmark results

Label generated data as synthetic and keep it separate from physical measurement artifacts. Save benchmark JSON/CSV output with machine, OS, software version, parameters and git commit. Do not fill documentation tables with illustrative values and call them real results.

## Deferred cloud stage

AWS deployment is intentionally out of scope here. A later stage should define architecture and budget limits, choose hosting/storage, configure secrets, logging and backups, and use GitHub Actions OIDC with narrowly scoped IAM roles rather than long-lived AWS access keys. Cloud deployment must be separately tested and documented before it is described as live.
