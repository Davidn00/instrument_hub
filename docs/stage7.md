# Stage 7 — Backend, Storage and Real-Time Acquisition

## 1. Objective

Stage 7 introduces the persistence and real-time backend infrastructure required to transform InstrumentHub from an acquisition and processing prototype into a persistent instrumentation platform.

The stage integrates:

* PostgreSQL
* TimescaleDB
* SQLAlchemy 2
* asyncpg
* Alembic
* WebSockets
* Persistent acquisition
* REST APIs

The architecture maintains the separation established in previous stages.

---

## 2. Architecture

The Stage 7 architecture is:

```text
                         ┌──────────────────────┐
                         │      FastAPI API      │
                         │ REST + WebSockets     │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
                    ▼                                ▼
             Acquisition Service              Query Services
                    │                                │
                    ▼                                ▼
             AcquisitionManager                 Storage
                    │                                │
                    ▼                                ▼
                Instrument                    SQLAlchemy 2
                    │                                │
                    ▼                                ▼
              Measurement ───────────────► PostgreSQL
                    │                         +
                    ├────────────────────► TimescaleDB
                    │
                    └────────────────────► WebSocket
                                               │
                                               ▼
                                            Browser
