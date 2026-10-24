# Stage 10 — Reproducibility, CI, Documentation and Demo

## Objective

Make InstrumentHub easier to reproduce, review and demonstrate through benchmark tooling, a full local container stack, continuous integration, technical documentation and a repeatable demo. AWS deployment is explicitly deferred to a later stage.

## Part 37 — Integration validation

**Reported by the project owner as validated.** The uploaded project archive does not independently prove every run, so preserve the actual test output in release evidence.

## Part 38 — Performance benchmarks

The benchmark should report p50/p95/p99 latency, throughput, process CPU and RSS for synthetic workloads at 100 Hz, 500 Hz, 1 kHz and 5 kHz. Synthetic processing and physical IBSEN acquisition must be reported separately.

**Status in the supplied ZIP: pending.** The archive did not contain `scripts/benchmark_instrumenthub.py` or benchmark reports under `reports/benchmarks/`. Apply/verify the Part 38 implementation before calling Stage 10 complete. Never populate results with estimated values.

Required evidence:

- Machine/OS/Python and dependency versions.
- JSON and CSV outputs for each synthetic sampling-rate workload.
- Explicit workload size and benchmark configuration.
- Separate physical-device report only if an IBSEN device was actually connected.

## Part 39 — Docker and Compose

Implementation in this stage:

- Backend image with a health check.
- Separate frontend multi-stage image (Node build + Nginx static serving).
- Nginx reverse proxy for `/api/*` and WebSocket upgrades.
- Compose services for TimescaleDB, API and frontend.
- Optional Mailpit service behind the `mail` profile.
- `.env` is optional for basic Compose configuration; environment variables have local-only defaults.
- Serial hardware remains host-attached by default; no Windows COM port is falsely mapped into a Linux container.

Validation commands:

```bash
docker compose config --quiet
docker compose build api frontend
docker compose up -d
docker compose ps
curl http://localhost:8200/api/v1/health
curl http://localhost:8080/healthz
```

**Status:** files authored; runtime validation pending in the user's Docker environment.

## Part 40 — Continuous integration

CI workflow now defines three jobs:

1. Backend: locked dependency sync, Ruff lint/format, MyPy and Pytest.
2. Frontend: `npm ci`, Oxlint and production build.
3. Docker: Compose config validation and backend/frontend image builds.

AWS OIDC deployment is not configured in this stage. The future deployment job must use short-lived OIDC credentials and a least-privilege role; no long-lived AWS keys should be introduced into this CI workflow.

**Status:** workflow authored; GitHub Actions result pending.

## Part 41 — Technical documentation

Documents added/updated:

- `ARCHITECTURE.md` — component and data-flow diagrams, local topology and hardware boundary.
- `API.md` — current route groups and links to generated OpenAPI.
- `DEVICE_PROTOCOL.md` — IBSEN serial command sequence, ACK/NAK, spectrum payload and calibration limitations.
- `SIGNAL_PROCESSING.md` — filtering, FFT/PSD, input constraints and benchmark interpretation.
- `FBG_ANALYSIS.md` — peak/wavelength/shift workflow and calibration cautions.
- `DEPLOYMENT.md` — local Compose operation, optional Mailpit, hardware boundary and deferred AWS plan.

Performance values, physical measurements and external media URLs remain pending until actual evidence is generated.

## Part 42 — Demo preparation

- `scripts/generate_demo_dataset.py` produces synthetic sine, ECG and EMG data in CSV, JSON and Parquet formats under `data/examples/`.
- `docs/demo-runbook.md` describes local startup, demo narration, screenshot naming, video hygiene and an evidence log.
- README links to the technical documents and documents local Compose access.
- `docs/cloud-integration.md` defines a provider-neutral, opt-in export boundary, cost controls and acceptance criteria. This is design preparation only; no cloud resources are provisioned and no live cloud integration is claimed complete.

**Status:** demo procedure authored; screenshots/video and runtime results are not yet captured.

## Current validation record

| Check | Result |
|---|---|
| Part 37 integration tests | Reported validated by project owner |
| Part 38 benchmark reports | Pending; absent from supplied ZIP |
| Compose syntax | Pending local Docker validation |
| API/frontend container builds | Pending local Docker validation |
| Backend CI | Pending GitHub Actions run |
| Frontend lint/build | Pending local/GitHub Actions run |
| Full demo screenshots/video | Pending capture |
| Physical IBSEN benchmark | Not claimed; only record if hardware run is performed |
| AWS deployment | Deferred by scope |

## Stage 10 completion criteria

- [ ] Part 38 benchmark script and report files exist; results are actual runs, not estimates.
- [ ] `docker compose config --quiet` succeeds.
- [ ] Backend and frontend images build successfully.
- [ ] Dashboard, API health and WebSocket routes are smoke-tested from Compose.
- [ ] Backend tests, Ruff, MyPy, frontend lint/build pass locally and in GitHub Actions.
- [ ] Documentation accurately reflects the implementation and contains reviewed diagrams.
- [ ] Demo datasets generate successfully and screenshots/video are captured or explicitly marked as not published.
- [x] AWS deployment is deferred to a separate stage as requested.

Do not mark Stage 10 fully complete until the unchecked criteria are validated against the working repository and the real test output is recorded.
