# Stage 6 — Análisis FBG

## 1. Objetivo

La Etapa 6 transforma el espectro óptico obtenido en la Etapa 5 en una cadena de análisis específica para sensores Fiber Bragg Grating (FBG).

El flujo principal es:

```text
Spectrum
   │
   ▼
Noise reduction
   │
   ▼
Peak detection
   │
   ▼
Peak refinement
   │
   ▼
λB
   │
   ├───────────────┐
   ▼               ▼
Δλ             Temporal tracking
   │
   ├───────────────┐
   ▼               ▼
Strain         Temperature
   │              │
   └──────┬───────┘
          ▼
      Calibration
