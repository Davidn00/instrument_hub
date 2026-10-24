# InstrumentHub Demo Runbook

## Purpose

This runbook defines a repeatable portfolio demo using generated signals and the local Docker stack. It is not a physical-instrument validation report. Replace the evidence placeholders with captures and measurements produced on the machine used for the demo.

## 1. Build reproducible sample datasets

From the repository root:

```bash
uv sync --locked --all-groups
uv run python scripts/generate_demo_dataset.py
```

The script writes CSV, JSON and Parquet files under `data/examples/` for a 2 Hz sine signal at 100 Hz, synthetic ECG at 500 Hz, and synthetic EMG at 1 kHz. The files are generated locally and are ignored by Git by default. If a small curated demo dataset should be committed, review its size, provenance and licensing first, then add only those specific files deliberately.

## 2. Start the application

```bash
cp .env.example .env  # PowerShell: Copy-Item .env.example .env
docker compose config --quiet
docker compose up --build -d
docker compose ps
```

Open `http://localhost:8080` for the dashboard and `http://localhost:8200/docs` for the API schema. Verify `GET /api/v1/health` and, once the database is initialized, `/api/v1/health/ready`.

## 3. Recommended walkthrough (4–6 minutes)

1. **Opening (0:00–0:20):** describe InstrumentHub as a local-first platform for acquisition, signal processing, persistence and visualization.
2. **Dashboard (0:20–0:50):** show navigation and current service status; avoid claiming live data if no simulator/device is running.
3. **Devices and experiments (0:50–1:40):** show the available device list and experiment lifecycle/result records. Explain that creating an experiment does not itself guarantee acquisition has started.
4. **Live measurements / spectrum (1:40–2:30):** use a simulator or known sample data. Label the source clearly as synthetic.
5. **FFT (2:30–3:10):** show a generated sine signal and compare the expected frequency with the computed dominant frequency. State the sampling rate and sample count.
6. **FBG analysis (3:10–4:10):** show raw and processed spectra, detected peaks and wavelength shift. Explain that strain/temperature interpretation requires correct calibration.
7. **Alerts (4:10–4:50):** show a rule and an alert event; use a controlled test input, not a claim of an unobserved physical alarm.
8. **Architecture and quality (4:50–5:30):** show the architecture diagram, tests/CI and Docker Compose topology.
9. **Limitations (last 20 seconds):** distinguish tested software behavior from physical hardware performance and cloud deployment, which is deferred.

## 4. Screenshot checklist

Save reviewed screenshots in a separate portfolio-assets folder (not under `frontend/src`). Suggested filenames:

- `01-dashboard.png`
- `02-devices.png`
- `03-experiments.png`
- `04-live-signal.png`
- `05-fft-analysis.png`
- `06-fbg-analysis.png`
- `07-alerts.png`
- `08-api-openapi.png`
- `09-compose-topology.png` (a diagram export, not a terminal screenshot)

Before publishing, hide credentials, local usernames, host paths, email addresses, serial numbers and any personal/customer data. Capture at a readable resolution and ensure all charts show axis units and the source type.

## 5. Video checklist

- Record at 1920×1080 or the highest stable display resolution.
- Use a clean browser profile and close unrelated windows/notifications.
- Keep narration factual; label simulator data as synthetic.
- Avoid showing `.env`, passwords, API keys, GitHub tokens, device serial numbers or unreviewed logs.
- Export an MP4 and inspect playback/audio before sharing.
- Add the public video URL to the README only after it exists and has been reviewed.

## 6. Evidence log (fill after execution)

| Evidence | Actual result / location |
|---|---|
| OS, CPU, RAM | Pending capture |
| Git commit | Pending capture |
| Backend pytest summary | Pending run |
| Frontend lint/build | Pending run |
| Compose build and health | Pending run |
| Dataset generation | Pending run |
| Screenshot directory/link | Not captured yet |
| Video URL | Not recorded yet |
| Physical IBSEN validation | Not run / only report if performed |

Do not replace `Pending` with estimated values. Keep the actual terminal output and report files with the release evidence.
