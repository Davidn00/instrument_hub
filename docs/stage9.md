# Stage 9 — Automation, Alerts and Advanced Analysis

## 1. Objective

Stage 9 introduces structured experiment management, configurable alert rules and notification delivery.

The implementation builds on the existing FastAPI backend, SQLAlchemy persistence layer, PostgreSQL/TimescaleDB database and React frontend.

## 2. Part 33 — Experiments

### Implemented capabilities

- Create and list experiments.
- Store device references and sensor/channel selections.
- Store acquisition and processing configuration.
- Track experiment lifecycle states.
- Append processing results without replacing earlier results.
- Validate referenced devices before creating an experiment.

### Lifecycle

- `CREATED`
- `RUNNING`
- `COMPLETED`
- `FAILED`
- `CANCELLED`

The domain service validates allowed state transitions and records execution timestamps.

Experiment configuration and results are stored in the existing JSONB metadata column for backward compatibility.

### API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/experiments` | List experiments |
| POST | `/api/v1/experiments` | Create an experiment |
| GET | `/api/v1/experiments/{id}` | Retrieve an experiment |
| PATCH | `/api/v1/experiments/{id}/status` | Update lifecycle state |
| POST | `/api/v1/experiments/{id}/results` | Append a result |

Creating an experiment does not automatically start instrument acquisition. Multi-device orchestration is a future extension.

## 3. Part 34 — Alert engine

### Supported metrics

- `temperature`
- `strain`
- `wavelength_drift`
- `signal_quality`

### Comparison operators

- `gt`
- `gte`
- `lt`
- `lte`

Rules can be enabled or disabled and optionally restricted to a device and channel.

The alert engine is separated from the API and persistence layers so its numerical comparison logic can be tested independently.

Wavelength drift requires a computed `delta_wavelength_nm` value. Signal quality requires an explicit numeric score; categorical quality labels are not interpreted as numerical measurements.

### Persistence

- `alert_rules`: configurable rules.
- `alerts`: generated alert events.

The existing alert table is retained. Alembic revision `0002_stage9_alert_rules` adds the new rule table without rewriting the Stage 7 migration.

### API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/alerts` | List alert events |
| GET | `/api/v1/alerts?active_only=true` | List unacknowledged events |
| POST | `/api/v1/alerts/rules` | Create a rule |
| GET | `/api/v1/alerts/rules` | List rules |
| PATCH | `/api/v1/alerts/{id}/acknowledge` | Acknowledge or reopen an event |

## 4. Part 35 — Notifications

### WebSocket

The existing WebSocket manager is reused for alert delivery.

- `/api/v1/ws/measurements`: existing measurement and spectrum stream.
- `/api/v1/ws/notifications`: alert notification stream.

Alert messages use the event type `alert`, keeping existing measurement and spectrum contracts intact.

### Email

Email delivery uses Python's standard SMTP library.

SMTP is optional and configured using environment variables:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `ALERT_EMAIL_TO`
- `SMTP_STARTTLS`

Credentials must remain outside source control.

### Dashboard

The React alert center displays alert severity, event time, device, channel, value and acknowledgement state.

The initial implementation refreshes alert history using REST polling. A fully WebSocket-driven dashboard notification experience can be added subsequently.

## 5. Architecture

```text
Instrument / Simulator
        |
        v
AcquisitionService
        |
        v
Measurement persistence
        |
        v
AlertingService
        |
        v
AlertEngine
        |
        +------> Alert persistence
        |
        +------> WebSocket notification
        |
        +------> Optional SMTP email
        |
        v
React Alert Center
```

## 6. Validation

Run:

```bash
uv run alembic upgrade head
uv run pytest tests/services -q
uv run pytest -q
uv run ruff check .
uv run mypy app
uv run uvicorn app.main:app --reload
```

Build the frontend:

```bash
cd frontend
npm run build
```

Check the API using `/docs` and verify alert events against actual acquisition data.

## 7. Known limitations

- Experiment creation does not automatically orchestrate multi-device acquisition.
- Experiment results are stored in JSONB rather than dedicated relational result tables.
- Alert delivery is direct rather than backed by a durable notification outbox.
- Automatic alert resolution and hysteresis are not implemented.
- Signal quality requires a numeric score from the processing pipeline.
- FBG drift alerts require the processing pipeline to provide the computed wavelength delta.
- SMTP delivery requires a reachable and correctly configured mail server.
- The alert dashboard initially uses REST polling.
- Authentication, authorization and recipient-level notification policies must be enforced before exposing these endpoints to untrusted users.

## 8. Completion criteria

Stage 9 is complete after the following are verified in the target environment:

- [ ] Experiment creation, retrieval, lifecycle transitions and result storage.
- [ ] Configurable alert rule creation and listing.
- [ ] Threshold evaluation for supported metrics.
- [ ] Alert persistence during real acquisition.
- [ ] WebSocket alert delivery.
- [ ] SMTP email delivery when configured.
- [ ] Dashboard alert history and acknowledgement.
- [ ] Alembic migration applied successfully.
- [ ] Unit tests, complete test suite, Ruff and MyPy pass.
- [ ] Frontend production build passes.
- [ ] README and stage documentation updated.
