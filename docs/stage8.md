
# Stage 8 — Professional Frontend Dashboard

## 1. Objective

Stage 8 introduces a separate web frontend for InstrumentHub.

The objective is to provide a professional interface for device
management, real-time acquisition, scientific visualization,
experiments, alerts and data export.

The frontend complements the existing FastAPI backend. It does not
replace the Python acquisition, processing or persistence layers.

## 2. Part 29A — Frontend foundation

The initial frontend is built with:

- React
- TypeScript
- Vite
- React Router
- TanStack Query
- Tailwind CSS
- Plotly.js

The frontend lives in the `frontend/` directory at the repository root.

## 3. Architecture

```text
React + TypeScript
       |
       +---- REST API (HTTP/JSON)
       |
       +---- WebSocket
                  |
                  v
                FastAPI
                  |
        +---------+----------+
        |         |          |
    Acquisition Processing Storage
        |         |          |
        +---------+----------+
                  |
          PostgreSQL/TimescaleDB
```

React is responsible for the user interface and visualization.
FastAPI remains responsible for API operations, acquisition,
processing and access to persisted data.

## 4. Configuration

The local frontend environment uses:

`VITE_API_BASE_URL`

Example:

`http://127.0.0.1:8000/api/v1`

The URL must match the port where FastAPI is actually accessible
from the browser.

Frontend environment variables prefixed with `VITE_` must not
contain secrets or private credentials.

## 5. Development commands

From the `frontend/` directory:

```bash
npm install
npm run dev
npm run build
```

The Vite development server uses port 5173.

## 6. Initial validation

Part 29A is considered complete when:

- [ ] Node.js and npm are available.
- [ ] Frontend dependencies install successfully.
- [ ] The Vite development server starts.
- [ ] The initial InstrumentHub screen renders.
- [ ] `npm run build` completes successfully.
- [ ] The backend files remain unchanged by frontend scaffolding.

## 7. Planned implementation

- 29B — Application layout and navigation.
- 29C — REST client, TypeScript contracts and API error handling.
- 29D — Devices and experiments.
- 30 — Live spectrum visualization.
- 31 — Time-series visualization.
- 32 — FFT dashboard.
- 33 — FBG analysis, alerts and export.
- 34 — Testing, security, documentation and deployment.


## 9. Part 29B — Layout and navigation

### Objective

Build the shared application layout and establish navigation between
the dashboard and the InstrumentHub functional modules.

### Implemented components

- `src/components/AppLayout.tsx`
  - Shared layout, sidebar state and page content outlet.
  - Responsive navigation overlay for small screens.
- `src/components/Sidebar.tsx`
  - Navigation groups and active route highlighting.
  - Responsive sidebar behavior.
- `src/components/Header.tsx`
  - Dynamic page title based on the current route.
  - Mobile navigation control.
- `src/pages/DashboardPage.tsx`
  - Initial dashboard overview.
  - Metric placeholders and quick-access links.
- `src/pages/ModulePage.tsx`
  - Reusable presentation component for module pages.
- `src/App.tsx`
  - Application routes and not-found page.
- `src/index.css`
  - Global styles, dark color scheme and focus indicators.

### Routes

| Route | Module |
|---|---|
| `/` | Dashboard |
| `/devices` | Devices |
| `/live-acquisition` | Live Acquisition |
| `/spectrum` | Spectrum |
| `/time-series` | Time Series |
| `/fft` | FFT Analysis |
| `/fbg-analysis` | FBG Analysis |
| `/experiments` | Experiments |
| `/alerts` | Alerts |
| `/export` | Export |

### Design decisions

- The frontend remains independent from the Python backend.
- React Router provides client-side navigation.
- The shared layout is rendered through nested routes and `Outlet`.
- Tailwind CSS provides responsive styling.
- Lucide React provides consistent interface icons.
- Placeholder metrics do not represent real instrument data.
- Backend connectivity is not considered verified in this part.

### Validation checklist

- [ ] All navigation links open the corresponding page.
- [ ] The active navigation item matches the current route.
- [ ] The mobile menu opens and closes correctly.
- [ ] The layout remains usable on small and large screens.
- [ ] Unknown routes display the not-found page.
- [ ] The frontend compiles successfully with `npm run build`.
- [ ] The original backend remains unchanged.

### Status

Part 29B implementation is complete when all validation
checks pass.

The overall Stage 8 remains in progress.
REST integration and functional scientific visualization are
scheduled for subsequent parts.
