
import { useEffect, useMemo, useState } from "react";
import Plot from "react-plotly.js";
import {
  Activity,
  ChartNoAxesCombined,
  RefreshCw,
  ScanSearch,
} from "lucide-react";

import { ApiError, apiRequest } from "../api/client";
import { useDevicesQuery, useSpectraQuery } from "../api/queries";
import type {
  FBGAnalysisResponse,
  FBGAnalysisRequest,
} from "../api/types";

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return `HTTP ${error.status}: ${error.message}`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "No se pudo ejecutar el análisis FBG.";
}

function FBGAnalysisPage() {
  const devicesQuery = useDevicesQuery();
  const spectraQuery = useSpectraQuery(100);

  const devices = devicesQuery.data ?? [];
  const spectra = spectraQuery.data ?? [];

  const [deviceId, setDeviceId] = useState("");
  const [spectrumTimestamp, setSpectrumTimestamp] = useState("");
  const [prominenceInput, setProminenceInput] = useState("");
  const [noiseReduction, setNoiseReduction] = useState(true);
  const [result, setResult] = useState<FBGAnalysisResponse | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const deviceSpectra = useMemo(
    () =>
      spectra
        .filter((spectrum) => spectrum.device_id === deviceId)
        .sort(
          (a, b) =>
            Date.parse(b.timestamp) - Date.parse(a.timestamp),
        ),
    [spectra, deviceId],
  );

  useEffect(() => {
    if (deviceId) return;

    const preferredDevice = devices.find((device) =>
      /fbg|ibsen|optical|spectrometer|interrogator/i.test(
        `${device.device_type} ${device.name}`,
      ),
    );

    const firstSpectrumDevice = spectra[0]?.device_id;

    setDeviceId(
      preferredDevice?.device_id ??
        firstSpectrumDevice ??
        devices[0]?.device_id ??
        "",
    );
  }, [deviceId, devices, spectra]);

  useEffect(() => {
    const timestampIsAvailable = deviceSpectra.some(
      (spectrum) => spectrum.timestamp === spectrumTimestamp,
    );

    if (!timestampIsAvailable) {
      setSpectrumTimestamp(deviceSpectra[0]?.timestamp ?? "");
      setResult(null);
    }
  }, [deviceSpectra, spectrumTimestamp]);

  async function runAnalysis() {
    if (!deviceId) {
      setError("Selecciona un dispositivo.");
      return;
    }

    if (deviceSpectra.length === 0) {
      setError(
        "Este dispositivo no tiene espectros almacenados. Ejecuta una adquisición FBG y vuelve a cargar los espectros.",
      );
      return;
    }

    const prominence = prominenceInput.trim() === ""
      ? null
      : Number(prominenceInput);

    if (
      prominence !== null &&
      (!Number.isFinite(prominence) || prominence < 0)
    ) {
      setError("La prominencia debe ser un número mayor o igual a cero.");
      return;
    }

    const payload: FBGAnalysisRequest = {
      device_id: deviceId,
      spectrum_timestamp: spectrumTimestamp || null,
      history_limit: 100,
      prominence,
      noise_reduction: noiseReduction,
      noise_window_length: 11,
      noise_polyorder: 3,
      refinement: "quadratic",
    };

    setPending(true);
    setError(null);

    try {
      const analysis = await apiRequest<FBGAnalysisResponse>(
        "fbg/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        },
      );

      setResult(analysis);
    } catch (cause) {
      setError(getErrorMessage(cause));
    } finally {
      setPending(false);
    }
  }

  const spectrumPlotData = result
    ? [
        {
          type: "scatter" as const,
          mode: "lines" as const,
          name: "Original",
          x: result.spectrum.wavelength,
          y: result.spectrum.intensity,
          line: { color: "#64748b", width: 1.3 },
        },
        {
          type: "scatter" as const,
          mode: "lines" as const,
          name: "Filtrado",
          x: result.spectrum.wavelength,
          y: result.filtered_intensity,
          line: { color: "#22d3ee", width: 2 },
        },
        {
          type: "scatter" as const,
          mode: "markers" as const,
          name: "Picos detectados",
          x: result.peaks.map((peak) => peak.wavelength_nm),
          y: result.peaks.map((peak) => peak.intensity),
          marker: {
            color: "#fb7185",
            size: 10,
            symbol: "diamond",
          },
        },
      ]
    : [];

  return (
    <div className="space-y-6">
      <section>
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-cyan-400">
          InstrumentHub / Optical Analysis
        </p>

        <div className="mt-3 flex items-start gap-4">
          <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-slate-800 bg-slate-900 text-cyan-300">
            <ChartNoAxesCombined size={24} />
          </span>

          <div>
            <h2 className="text-3xl font-bold tracking-tight text-white">
              FBG Analysis
            </h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Inspecciona espectros ópticos, detecta picos de Bragg y
              analiza el desplazamiento de la longitud de onda a lo largo
              del tiempo.
            </p>
          </div>
        </div>
      </section>

      {error && (
        <div
          role="alert"
          className="rounded-lg border border-red-900 bg-red-950/40 p-4 text-sm text-red-300"
        >
          {error}
        </div>
      )}

      {(devicesQuery.isError || spectraQuery.isError) && (
        <div
          role="alert"
          className="rounded-lg border border-amber-900 bg-amber-950/30 p-4 text-sm text-amber-200"
        >
          No se pudieron cargar todos los datos de la API. Comprueba la
          conexión con el backend e inténtalo de nuevo.
        </div>
      )}

      <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-white">
            Configuración del análisis
          </h3>
          <p className="mt-1 text-sm text-slate-400">
            Los espectros se obtienen de la base de datos mediante la API REST.
          </p>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <label className="block text-sm font-medium text-slate-300">
            Dispositivo
            <select
              value={deviceId}
              onChange={(event) => {
                setDeviceId(event.target.value);
                setSpectrumTimestamp("");
                setResult(null);
                setError(null);
              }}
              disabled={devicesQuery.isPending}
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-slate-100 outline-none focus:border-cyan-500"
            >
              <option value="">Seleccionar dispositivo</option>
              {devices.map((device) => (
                <option key={device.device_id} value={device.device_id}>
                  {device.name} ({device.device_id})
                </option>
              ))}
            </select>
          </label>

          <label className="block text-sm font-medium text-slate-300">
            Espectro almacenado
            <select
              value={spectrumTimestamp}
              onChange={(event) => {
                setSpectrumTimestamp(event.target.value);
                setResult(null);
              }}
              disabled={deviceSpectra.length === 0}
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-slate-100 outline-none focus:border-cyan-500"
            >
              <option value="">Seleccionar espectro</option>
              {deviceSpectra.map((spectrum) => (
                <option
                  key={`${spectrum.device_id}-${spectrum.timestamp}`}
                  value={spectrum.timestamp}
                >
                  {new Date(spectrum.timestamp).toLocaleString()} ·{" "}
                  {spectrum.wavelength.length} puntos
                </option>
              ))}
            </select>
          </label>

          <label className="block text-sm font-medium text-slate-300">
            Prominencia mínima (opcional)
            <input
              type="number"
              min="0"
              step="any"
              value={prominenceInput}
              onChange={(event) => setProminenceInput(event.target.value)}
              placeholder="Automática"
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-slate-100 outline-none focus:border-cyan-500"
            />
          </label>

          <label className="flex items-center gap-3 self-end rounded-lg border border-slate-800 bg-slate-950/50 p-3 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={noiseReduction}
              onChange={(event) => setNoiseReduction(event.target.checked)}
              className="accent-cyan-400"
            />
            Aplicar filtro Savitzky–Golay
          </label>
        </div>

        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => void runAnalysis()}
            disabled={pending || !deviceId || !spectrumTimestamp}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-cyan-400 px-4 py-2.5 text-sm font-semibold text-slate-950 hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ScanSearch size={17} />
            {pending ? "Analizando..." : "Analizar espectro"}
          </button>

          <button
            type="button"
            onClick={() => {
              void Promise.all([
                devicesQuery.refetch(),
                spectraQuery.refetch(),
              ]);
            }}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-700 px-4 py-2.5 text-sm font-medium text-slate-300 hover:bg-slate-800"
          >
            <RefreshCw size={16} />
            Actualizar datos
          </button>

          <span className="text-xs text-slate-500">
            Espectros disponibles para el dispositivo: {deviceSpectra.length}
          </span>
        </div>
      </section>

      {!result && (
        <section className="flex min-h-56 flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900/30 p-8 text-center">
          <Activity size={28} className="text-slate-500" />
          <h3 className="mt-4 font-semibold text-slate-200">
            Análisis pendiente
          </h3>
          <p className="mt-2 max-w-lg text-sm leading-6 text-slate-400">
            Selecciona un dispositivo y un espectro almacenado, y ejecuta el
            análisis para visualizar la curva, sus picos y el seguimiento
            de la longitud de onda de Bragg.
          </p>
        </section>
      )}

      {result && (
        <>
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              label="Longitud de onda de Bragg"
              value={
                result.peak_wavelength_nm === null
                  ? "Sin pico"
                  : `${result.peak_wavelength_nm.toFixed(5)} nm`
              }
            />
            <MetricCard
              label="Intensidad del pico"
              value={
                result.peak_intensity === null
                  ? "—"
                  : result.peak_intensity.toPrecision(5)
              }
            />
            <MetricCard
              label="Picos detectados"
              value={String(result.peaks.length)}
            />
            <MetricCard
              label="RMS del espectro"
              value={result.rms.toPrecision(5)}
            />
          </section>

          <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 sm:p-6">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-white">
                Inspección del espectro
              </h3>
              <p className="mt-1 text-sm text-slate-400">
                Longitud de onda frente a intensidad. Se muestran la señal
                original, la filtrada y los máximos detectados.
              </p>
            </div>

            <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950/50">
              <Plot
                data={spectrumPlotData}
                layout={{
                  autosize: true,
                  height: 440,
                  margin: { l: 70, r: 25, t: 25, b: 70 },
                  paper_bgcolor: "rgba(0,0,0,0)",
                  plot_bgcolor: "rgba(2,6,23,0.2)",
                  font: { color: "#cbd5e1" },
                  xaxis: {
                    title: {
                      text: `Longitud de onda (${result.spectrum.wavelength_unit})`,
                    },
                    gridcolor: "#1e293b",
                  },
                  yaxis: {
                    title: {
                      text: `Intensidad (${result.spectrum.intensity_unit})`,
                    },
                    gridcolor: "#1e293b",
                  },
                  legend: { orientation: "h", y: -0.23 },
                  hovermode: "closest",
                  uirevision: `${result.device_id}-${result.spectrum.timestamp}`,
                }}
                config={{ responsive: true, displaylogo: false, scrollZoom: true }}
                useResizeHandler
                style={{ width: "100%" }}
              />
            </div>

            <p className="mt-3 text-xs text-slate-500">
              Dispositivo: {result.device_id} · Adquisición:{" "}
              {new Date(result.spectrum.timestamp).toLocaleString()} ·{" "}
              {result.spectrum.wavelength.length} puntos.
            </p>
          </section>

          <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 sm:p-6">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-white">
                Picos de Bragg detectados
              </h3>
              <p className="mt-1 text-sm text-slate-400">
                La posición puede incluir refinamiento cuadrático sub-píxel.
              </p>
            </div>

            {result.peaks.length === 0 ? (
              <p className="rounded-lg border border-dashed border-slate-700 p-5 text-sm text-slate-400">
                No se detectaron picos con los parámetros actuales. Reduce
                la prominencia mínima o comprueba la calidad del espectro.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[620px] text-left text-sm">
                  <thead className="border-b border-slate-800 text-xs uppercase tracking-wide text-slate-500">
                    <tr>
                      <th className="px-3 py-3">#</th>
                      <th className="px-3 py-3">λB (nm)</th>
                      <th className="px-3 py-3">Intensidad</th>
                      <th className="px-3 py-3">Prominencia</th>
                      <th className="px-3 py-3">Anchura (nm)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.peaks.map((peak, index) => (
                      <tr
                        key={`${peak.index}-${peak.wavelength_nm}`}
                        className="border-b border-slate-800/70 text-slate-300"
                      >
                        <td className="px-3 py-3">{index + 1}</td>
                        <td className="px-3 py-3 font-mono">
                          {peak.wavelength_nm.toFixed(5)}
                        </td>
                        <td className="px-3 py-3 font-mono">
                          {peak.intensity.toPrecision(5)}
                        </td>
                        <td className="px-3 py-3 font-mono">
                          {peak.prominence?.toPrecision(5) ?? "—"}
                        </td>
                        <td className="px-3 py-3 font-mono">
                          {peak.width_nm?.toFixed(5) ?? "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 sm:p-6">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-white">
                Seguimiento de longitud de onda de Bragg
              </h3>
              <p className="mt-1 text-sm text-slate-400">
                Evolución temporal de λB y su desplazamiento respecto a la
                longitud de onda de referencia.
              </p>
            </div>

            {result.tracking_points.length === 0 ? (
              <p className="text-sm text-slate-400">
                No hay suficientes espectros con picos válidos para mostrar
                el seguimiento.
              </p>
            ) : (
              <>
                <div className="grid gap-4 md:grid-cols-2">
                  <TrackingChart
                    title="Longitud de onda de Bragg"
                    points={result.tracking_points}
                    valueKey="wavelength_nm"
                    yTitle="λB (nm)"
                  />
                  <TrackingChart
                    title="Desplazamiento espectral"
                    points={result.tracking_points}
                    valueKey="delta_wavelength_nm"
                    yTitle="Δλ (nm)"
                  />
                </div>

                <p className="mt-4 text-xs text-slate-500">
                  Referencia λ0:{" "}
                  {result.reference_wavelength_nm?.toFixed(5) ?? "—"} nm ·{" "}
                  Espectros válidos en el seguimiento:{" "}
                  {result.analyzed_spectra_count}.
                </p>
              </>
            )}
          </section>

          <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
            <h3 className="text-lg font-semibold text-white">
              Metadata y parámetros
            </h3>
            <p className="mt-1 text-sm text-slate-400">
              Información asociada al espectro seleccionado y a su análisis.
            </p>

            <div className="mt-4 grid gap-4 lg:grid-cols-2">
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Metadata de adquisición
                </p>
                <pre className="max-h-72 overflow-auto rounded-lg border border-slate-800 bg-slate-950 p-4 text-xs leading-5 text-slate-300">
                  {JSON.stringify(result.spectrum.metadata, null, 2)}
                </pre>
              </div>

              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Parámetros del análisis
                </p>
                <pre className="max-h-72 overflow-auto rounded-lg border border-slate-800 bg-slate-950 p-4 text-xs leading-5 text-slate-300">
                  {JSON.stringify(
                    {
                      noise_reduction: result.noise_reduction,
                      noise_window_length: result.noise_window_length,
                      noise_polyorder: result.noise_polyorder,
                      prominence: result.prominence,
                      refinement: result.refinement,
                      reference_wavelength_nm:
                        result.reference_wavelength_nm,
                      analyzed_spectra_count:
                        result.analyzed_spectra_count,
                    },
                    null,
                    2,
                  )}
                </pre>
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: string;
}

function MetricCard({ label, value }: MetricCardProps) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 break-words text-xl font-semibold text-slate-100">
        {value}
      </p>
    </div>
  );
}

interface TrackingChartProps {
  title: string;
  points: FBGAnalysisResponse["tracking_points"];
  valueKey: "wavelength_nm" | "delta_wavelength_nm";
  yTitle: string;
}

function TrackingChart({
  title,
  points,
  valueKey,
  yTitle,
}: TrackingChartProps) {
  return (
    <div className="min-w-0 rounded-lg border border-slate-800 bg-slate-950/50 p-3">
      <h4 className="mb-2 text-sm font-medium text-slate-300">{title}</h4>
      <Plot
        data={[
          {
            type: "scatter",
            mode: "lines+markers",
            x: points.map((point) => point.timestamp),
            y: points.map((point) => point[valueKey]),
            line: { color: "#a78bfa", width: 2 },
            marker: { size: 5 },
            hovertemplate:
              "%{x|%Y-%m-%d %H:%M:%S}" +
              `<br>${yTitle}: %{y:.6f}` +
              "<extra></extra>",
          },
        ]}
        layout={{
          autosize: true,
          height: 300,
          margin: { l: 65, r: 15, t: 15, b: 60 },
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(2,6,23,0.2)",
          font: { color: "#cbd5e1" },
          xaxis: { title: { text: "Tiempo" }, gridcolor: "#1e293b" },
          yaxis: { title: { text: yTitle }, gridcolor: "#1e293b" },
          showlegend: false,
        }}
        config={{ responsive: true, displaylogo: false }}
        useResizeHandler
        style={{ width: "100%" }}
      />
    </div>
  );
}

export default FBGAnalysisPage;
