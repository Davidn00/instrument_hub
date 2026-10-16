
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


## 10. Part 29C — REST API integration

### Objective

Connect the React frontend to the existing FastAPI backend through
a centralized HTTP client and typed data contracts.

### Backend endpoints used

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/health` | API health |
| GET | `/api/v1/health/ready` | Database and TimescaleDB readiness |
| GET | `/api/v1/devices` | Device records |
| GET | `/api/v1/measurements` | Persisted measurements |
| GET | `/api/v1/spectra` | Persisted spectra |
| GET | `/api/v1/experiments` | Experiment records |

### Frontend files

- `src/api/types.ts`
  - TypeScript contracts corresponding to backend response schemas.
- `src/api/client.ts`
  - Centralized fetch client and HTTP error handling.
- `src/api/queries.ts`
  - TanStack Query hooks, cache keys and refresh policies.
- `src/components/Header.tsx`
  - API health and database readiness indicators.
- `src/pages/DashboardPage.tsx`
  - API-backed metrics and recent measurements.

### Development networking

The frontend uses a Vite development proxy for `/api` requests.

`VITE_API_BASE_URL` defaults to `/api/v1`.

`VITE_DEV_PROXY_TARGET` identifies the backend origin.

Docker Compose must map the host port to the container port where
Uvicorn actually listens. The supplied Dockerfile runs Uvicorn on
port 8000; a host port of 8001 should therefore map to `8001:8000`.

### Query behavior

- Health status refreshes periodically.
- Database readiness is checked independently.
- Devices and experiments use cached REST queries.
- Recent measurements refresh through periodic HTTP polling.
- HTTP errors are surfaced in the dashboard.

Polling is not equivalent to a WebSocket data stream.

### Known limitations

- Device and experiment management interfaces are not implemented
  in this part.
- Spectrum data is available through the client but is not yet
  visualized.
- WebSocket event handling is not implemented in the frontend.
- Alert persistence exists, but the inspected API router does not
  expose a REST endpoint for querying alerts.
- TypeScript interfaces describe expected JSON structures but do
  not validate server responses at runtime.

### Validation checklist

- [ ] FastAPI health endpoint responds successfully.
- [ ] Database readiness endpoint confirms PostgreSQL and TimescaleDB.
- [ ] Vite proxy forwards requests to FastAPI.
- [ ] Device, experiment and measurement queries return JSON arrays.
- [ ] Dashboard displays returned data and handles empty responses.
- [ ] API failures are visible to the user.
- [ ] TypeScript compilation and Vite production build succeed.
- [ ] Previous backend tests continue to pass.


## Parte 29D — Devices y Experiments funcionales

### Objetivo

Convertir las pantallas de dispositivos y experimentos en módulos
conectados a la API REST de InstrumentHub.

### Archivos implementados

- `frontend/src/api/types.ts`
  - Tipos de creación `ChannelCreate`, `DeviceCreate` y `ExperimentCreate`.
- `frontend/src/api/queries.ts`
  - Mutaciones para crear dispositivos y experimentos.
  - Invalidación de las consultas correspondientes después de crear registros.
- `frontend/src/pages/DevicesPage.tsx`
  - Tabla de dispositivos.
  - Formulario de creación de dispositivos y canales.
  - Validación de campos y metadatos JSON.
- `frontend/src/pages/ExperimentsPage.tsx`
  - Tabla de experimentos.
  - Formulario de creación.
  - Validación y presentación de errores.
- `frontend/src/App.tsx`
  - Integración de las rutas de Devices y Experiments.

### Contratos REST

| Operación | Endpoint |
|---|---|
| Listar dispositivos | `GET /api/v1/devices` |
| Crear dispositivo | `POST /api/v1/devices` |
| Listar experimentos | `GET /api/v1/experiments` |
| Crear experimento | `POST /api/v1/experiments` |

Los payloads respetan los esquemas `DeviceCreate`, `ChannelCreate`
y `ExperimentCreate` del backend.

### Validación

- Los campos obligatorios se validan en el frontend.
- Los metadatos deben ser objetos JSON válidos.
- Los errores HTTP se muestran en la interfaz.
- Los botones de envío se deshabilitan durante las operaciones.
- Las tablas se actualizan mediante invalidación de caché de TanStack Query.

### Limitaciones

- La validación del frontend complementa, pero no sustituye, la
  validación de FastAPI.
- Los valores admitidos para `device_type` deben coincidir con el modelo
  y el esquema reales del backend.
- La edición y eliminación de registros no forman parte de esta entrega.
- La finalización de la parte requiere pruebas contra la API real.


## Parte 30 — Visualización de espectros y adquisición en vivo

### Objetivo

Visualizar espectros ópticos y controlar la adquisición desde el frontend
utilizando la API REST y los eventos WebSocket de FastAPI.

### Dependencias

- `plotly.js-dist-min`
- `react-plotly.js`
- `@types/react-plotly.js`

### Archivos implementados

- `frontend/src/api/types.ts`
  - Tipos de eventos de espectro y medición.
  - Estados de conexión WebSocket.
- `frontend/src/hooks/useSpectrumStream.ts`
  - Gestión de la conexión WebSocket.
  - Validación básica del evento de espectro.
  - Reconexión progresiva y limpieza de recursos.
- `frontend/src/components/SpectrumChart.tsx`
  - Gráfico de longitud de onda frente a intensidad.
- `frontend/src/pages/SpectrumPage.tsx`
  - Visualización del último espectro disponible.
  - Respaldo inicial mediante REST.
- `frontend/src/pages/LiveAcquisitionPage.tsx`
  - Selección de dispositivo.
  - Inicio y detención de adquisición.
  - Estado de conexión y visualización en vivo.
- `frontend/src/App.tsx`
  - Rutas funcionales para Spectrum y Live Acquisition.

### Contratos utilizados

| Operación | Endpoint |
|---|---|
| Espectros almacenados | `GET /api/v1/spectra` |
| Iniciar adquisición | `POST /api/v1/acquisition/start` |
| Detener adquisición | `POST /api/v1/acquisition/stop` |
| Eventos en vivo | `WS /api/v1/ws/measurements` |

### Eventos WebSocket

El frontend reconoce eventos de tipo `spectrum` y extrae las propiedades
`wavelength`, `intensity`, `wavelength_unit`, `intensity_unit`,
`device_id` y `timestamp`.

Los arrays de longitud de onda e intensidad deben ser numéricos,
no vacíos y tener la misma longitud.

### Limitaciones

- La visualización en vivo depende de que el backend publique eventos
  `spectrum` con un formato compatible.
- La conexión WebSocket no inicia por sí misma la adquisición.
- El estado local de inicio o detención no constituye una confirmación
  independiente del hardware.
- La reconexión no garantiza la recuperación de eventos perdidos.
- El último espectro recibido se conserva en memoria; no constituye
  un historial completo.
- La estructura real de los mensajes debe contrastarse con el publicador
  WebSocket del backend.

### Validación

- Compilación TypeScript y build de Vite.
- Consulta de espectros históricos.
- Conexión WebSocket y recepción de un evento `spectrum`.
- Actualización de la curva con nuevos espectros.
- Inicio y detención mediante los endpoints REST.
- Manejo de desconexión y errores de la API.

## Parte 31 — Live sensor data

### Objetivo

Visualizar mediciones de varios dispositivos y canales en tiempo real
utilizando el endpoint WebSocket existente.

### Implementación

- `useMeasurementStream.ts`: recibe, valida y almacena eventos `measurement`.
- `measurementSeries.ts`: agrupa mediciones por dispositivo, canal y unidad,
  y estima la frecuencia de muestreo mediante sus marcas temporales.
- `MeasurementTimeSeriesChart.tsx`: representa varias series temporales.
- `TimeSeriesPage.tsx`: selecciona dispositivos y controla su adquisición.

### Limitaciones

- El buffer de 5.000 mediciones se conserva en memoria del navegador.
- Cada serie muestra hasta 600 puntos en la Parte 31.
- Los datos históricos persistidos no se cargan automáticamente en el buffer.
- Las distintas unidades físicas no comparten necesariamente una escala comparable.
- La recepción de eventos no garantiza que todos los dispositivos estén adquiriendo.

### Validación

- [ ] Build de TypeScript y Vite.
- [ ] Recepción de eventos `measurement`.
- [ ] Visualización de varias series simultáneas.
- [ ] Inicio y detención de varios dispositivos.
- [ ] Comprobación de reconexión WebSocket.

## Parte 32 — FFT dashboard

### Objetivo

Comparar una señal en el dominio temporal con su representación frecuencial
mediante una FFT calculada en el backend.

### Implementación

- `app/api/v1/schemas/analysis.py`: contratos de petición y respuesta.
- `app/api/v1/routes/analysis.py`: endpoint de análisis FFT.
- `app/api/v1/router.py`: registro del router de análisis.
- `app/devices/simulators/waveform.py`: generación de una señal sinusoidal variable.
- `app/services/acquisition.py`: configuración de parámetros del simulador.
- `frontend/src/pages/FFTPage.tsx`: selección de serie y visualización de ambos dominios.

### Endpoint

`POST /api/v1/analysis/fft`

La petición incluye las muestras, la frecuencia de muestreo estimada y la opción
de eliminar la media. La respuesta incluye el eje temporal relativo, los valores
originales, las frecuencias, las amplitudes y la frecuencia dominante.

### Consideraciones de procesamiento

- Se requieren al menos 16 muestras y se admiten hasta 4.096 por petición.
- El cálculo usa la función `fft_spectrum` existente.
- La resolución frecuencial depende de la duración de la ventana y de la
  frecuencia de muestreo.
- La FFT presupone un muestreo aproximadamente uniforme.
- La frecuencia dominante excluye la componente DC.
- La frecuencia de muestreo estimada puede variar por la temporización del sistema.

### Validación

- [ ] Pruebas unitarias y de API para FFT.
- [ ] Detección de una senoide de frecuencia conocida.
- [ ] Validación de peticiones incorrectas.
- [ ] Visualización de la señal temporal.
- [ ] Visualización del espectro frecuencial.
- [ ] Build de frontend y suite completa de backend.

## Parte 32 — FFT dashboard y FBG Analysis

### Objetivo

Completar las herramientas de análisis científico del frontend con
análisis FFT y análisis de espectros de redes de Bragg.

### FBG Analysis: arquitectura

El frontend selecciona un dispositivo y un espectro persistido.
El backend consulta `SpectrumRepository` y reutiliza las funciones
existentes en `app.processing.fbg`.

### Operaciones de análisis

- Reducción de ruido mediante Savitzky–Golay.
- Detección de picos con `scipy.signal.find_peaks`.
- Refinamiento cuadrático de la longitud de onda del pico.
- Cálculo del pico más fuerte y de métricas RMS.
- Seguimiento de λB en el historial disponible.
- Cálculo de Δλ = λB(t) − λ0.
- Respuesta con parámetros de detección y metadata del espectro.

### API

`POST /api/v1/fbg/analyze`

El cuerpo identifica el dispositivo y, opcionalmente, la marca temporal
del espectro. También permite configurar el límite de historial, la
prominencia mínima, la reducción de ruido, el refinamiento y la
longitud de onda de referencia.

La API devuelve el espectro seleccionado, la intensidad filtrada,
los picos detectados, las métricas y los puntos de seguimiento.

### Frontend

`frontend/src/pages/FBGAnalysisPage.tsx` reemplaza la página provisional
de `ModulePage` en `/fbg-analysis`.

La página proporciona:
- Selección de dispositivo y espectro histórico.
- Comparación de espectro original y filtrado.
- Marcadores y tabla de picos.
- Longitud de onda de Bragg e intensidad máxima.
- Métrica RMS.
- Gráficas temporales de λB y Δλ.
- Visualización de metadata y parámetros del análisis.

### Limitaciones

- El análisis se basa en los espectros almacenados que devuelve la API.
- El historial de seguimiento está limitado por `history_limit`.
- La detección de picos depende de la calidad del espectro y de sus parámetros.
- La calibración a temperatura o deformación requiere coeficientes
  físicos del sensor; no se infiere únicamente a partir de Δλ.
- Los resultados sintéticos validan el algoritmo y la integración, pero
  no sustituyen la validación con datos de un interrogador óptico real.

### Validación

- [ ] Prueba de integración de `POST /api/v1/fbg/analyze`.
- [ ] Detección de una longitud de onda conocida en espectros sintéticos.
- [ ] Seguimiento temporal de varios espectros.
- [ ] Respuesta correcta cuando no hay espectros almacenados.
- [ ] Manejo de parámetros inválidos.
- [ ] Build de Vite y TypeScript.
- [ ] Suite completa de pruebas del backend.


### Status

Stage 8 completed.
