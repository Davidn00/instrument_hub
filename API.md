# InstrumentHub — API Reference

## Status and scope

This is a practical map of the API surface, not a substitute for the running application's OpenAPI schema. Route names, HTTP methods and request models can change as the project evolves. **The live API at `/docs` and `/openapi.json` is authoritative.** Do not invent an endpoint in client code just because it appears in a planning document.

## Base URLs

| Mode | Base URL |
|---|---|
| Local API (typical) | `http://127.0.0.1:8000` |
| Docker Compose configuration described in the Stage 10 plan | `http://localhost:8200` |
| OpenAPI UI | `/docs` |
| OpenAPI JSON | `/openapi.json` |

The host port depends on the current `docker-compose.yml` and environment variables.

## Health and API discovery

- `GET /api/v1/health` — expected health endpoint in the project baseline; confirm the exact response model in the running app.
- `GET /docs` — interactive Swagger UI provided by FastAPI.
- `GET /openapi.json` — machine-readable API schema.

Example:

```bash
curl -i http://127.0.0.1:8000/api/v1/health
```

For a Compose setup exposing the API on port `8200`, use `http://127.0.0.1:8200` instead.

## Functional groups

The project has been developed around the following functional areas. Use `/openapi.json` to obtain the exact paths and schemas in the current checkout.

| Area | Intended responsibility |
|---|---|
| Devices and channels | Register and inspect instruments and their channels. |
| Experiments | Organise acquisition configuration, devices, processing and results. |
| Acquisition and simulation | Start or configure supported simulated or physical acquisition sources. |
| Measurements and spectra | Retrieve recorded measurements and spectral data. |
| Signal analysis | Statistical analysis, FFT/spectral analysis and FBG analysis. |
| Alerts | Configure rules and inspect generated alerts. |
| Storage and exports | Persist records and export supported result formats. |
| WebSockets | Push supported measurement or spectrum updates to connected clients. |

## WebSocket considerations

The frontend/backend contract has previously distinguished measurement messages from spectrum messages. A temperature simulator may publish measurement events, while a spectrum-producing source publishes wavelength/intensity arrays. A client should not assume every message contains spectral arrays.

When connecting through a reverse proxy:
- forward the `/api/` prefix unchanged;
- enable HTTP/1.1 upstream connections;
- pass `Upgrade` and `Connection` headers;
- test reconnect behaviour and error handling;
- validate message types and payloads before updating charts.

Example client-side pseudocode:

```javascript
const socket = new WebSocket("ws://localhost:8200/api/v1/ws/...");
socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  switch (message.type) {
    case "measurement":
      // Validate measurement fields before appending to the time-series buffer.
      break;
    case "spectrum":
      // Validate wavelength and intensity arrays before drawing a spectrum.
      break;
    default:
      // Ignore or log unknown message types safely.
  }
});
```

Replace the illustrative WebSocket URL with the exact route shown by the running application's OpenAPI schema or route definitions.

## Discover the exact contract

1. Start the backend.
2. Open `/docs`.
3. Inspect each route and its request/response schemas.
4. Export `/openapi.json` if you need a stable reference.
5. Check WebSocket routes in the source code; FastAPI's OpenAPI schema does not normally document WebSockets.
6. Keep this document in sync with tests and the frontend API client.

## Error handling and security

- Treat 4xx responses as client/configuration errors and 5xx responses as server errors.
- Do not expose secrets, serial command payloads containing sensitive data, or internal stack traces in public API responses.
- Apply authentication/authorisation to sensitive operations if configured in the current deployment.
- Do not expose the database port publicly in a production deployment.
