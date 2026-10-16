
import { useEffect, useState } from "react";
import Plot from "react-plotly.js";
import { Activity, BarChart3, RadioTower } from "lucide-react";

import { ApiError, apiRequest } from "../api/client";
import type { FftAnalysisResponse } from "../api/types";
import MeasurementTimeSeriesChart from "../components/MeasurementTimeSeriesChart";
import { useMeasurementStream } from "../hooks/useMeasurementStream";
import {
  buildMeasurementSeries,
  estimateSamplingRate,
} from "../utils/measurementSeries";

function FFTPage() {
  const stream = useMeasurementStream();

  const series = buildMeasurementSeries(
    stream.measurements,
    null,
    2048,
  );

  const [selectedSeriesKey, setSelectedSeriesKey] = useState("");
  const [result, setResult] = useState<FftAnalysisResponse | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedSeries = series.find(
    (item) => item.key === selectedSeriesKey,
  ) ?? null;

  useEffect(() => {
    if (
      series.length > 0 &&
      !series.some((item) => item.key === selectedSeriesKey)
    ) {
      setSelectedSeriesKey(series[0].key);
      setResult(null);
    }
  }, [series, selectedSeriesKey]);

  async function calculateFFT() {
    if (!selectedSeries) {
      setError("Selecciona una serie con mediciones.");
      return;
    }

    const points = selectedSeries.points;

    if (points.length < 16) {
      setError(
        "Se necesitan al menos 16 muestras. Mantén la adquisición activa para reunir más datos.",
      );
      return;
    }

    const samplingRate = estimateSamplingRate(points);

    if (!samplingRate || !Number.isFinite(samplingRate)) {
      setError(
        "No se pudo estimar una frecuencia de muestreo válida a partir de las marcas temporales.",
      );
      return;
    }

    setPending(true);
    setError(null);

    try {
      const analysis = await apiRequest<FftAnalysisResponse>(
        "analysis/fft",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            samples: points.map((point) => point.value),
            sampling_rate_hz: samplingRate,
            remove_mean: true,
          }),
        },
      );

      setResult(analysis);
    } catch (cause) {
      if (cause instanceof ApiError) {
        setError(`HTTP ${cause.status}: ${cause.message}`);
      } else if (cause instanceof Error) {
        setError(cause.message);
      } else {
        setError("No se pudo calcular la FFT.");
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="space-y-6">
      <section>
        <p className="text-sm text-slate-400">
          Analiza una señal adquirida y compara su comportamiento temporal
          con su distribución de amplitud en frecuencia.
        </p>
      </section>

      {stream.error && (
        <div
          role="status"
          className="rounded-lg border border-amber-900 bg-amber-950/30 p-3 text-sm text-amber-200"
        >
          {stream.error}
        </div>
      )}

      {error && (
        <div
          role="alert"
          className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300"
        >
          {error}
        </div>
      )}

      <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-5">
        <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_auto] md:items-end">
          <label className="block text-sm font-medium text-slate-300">
            Serie de entrada
            <select
              value={selectedSeriesKey}
              onChange={(event) => {
                setSelectedSeriesKey(event.target.value);
                setResult(null);
                setError(null);
              }}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-slate-100 outline-none focus:border-cyan-500"
            >
              <option value="">Selecciona un dispositivo/canal</option>
              {series.map((item) => (
                <option key={item.key} value={item.key}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>

          <button
            type="button"
            onClick={() => void calculateFFT()}
            disabled={!selectedSeries || pending}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-cyan-400 px-4 py-2.5 text-sm font-semibold text-slate-950 hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <BarChart3 size={17} />
            {pending ? "Calculando..." : "Calcular FFT"}
          </button>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-slate-400">
          <span className="inline-flex items-center gap-2">
            <RadioTower size={14} />
            WebSocket: {stream.status}
          </span>
          <span>
            Muestras disponibles: {selectedSeries?.points.length ?? 0}
          </span>
          <span>Máximo por serie: 2.048 muestras</span>
        </div>
      </section>

      <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 sm:p-6">
        <div className="mb-4 flex items-center gap-2">
          <Activity size={18} className="text-cyan-300" />
          <div>
            <h2 className="text-lg font-semibold text-slate-100">
              Dominio temporal
            </h2>
            <p className="text-sm text-slate-400">
              Valor medido en función del tiempo.
            </p>
          </div>
        </div>

        <MeasurementTimeSeriesChart
          series={selectedSeries ? [selectedSeries] : []}
          height={350}
        />
      </section>

      <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 sm:p-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-slate-100">
            Dominio frecuencial
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Amplitud frente a frecuencia, calculada por el backend.
          </p>
        </div>

        {!result ? (
          <div className="flex min-h-64 items-center justify-center rounded-lg border border-dashed border-slate-700 bg-slate-950/50 p-6 text-center">
            <p className="text-sm text-slate-400">
              Reúne al menos 16 muestras y pulsa Calcular FFT.
            </p>
          </div>
        ) : (
          <>
            <div className="mb-4 grid gap-4 sm:grid-cols-3">
              <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
                <p className="text-sm text-slate-400">Frecuencia dominante</p>
                <p className="mt-2 text-xl font-semibold text-cyan-300">
                  {result.dominant_frequency_hz.toFixed(4)} Hz
                </p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
                <p className="text-sm text-slate-400">Muestras analizadas</p>
                <p className="mt-2 text-xl font-semibold text-slate-100">
                  {result.sample_count.toLocaleString("es-MX")}
                </p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
                <p className="text-sm text-slate-400">
                  Frecuencia de muestreo estimada
                </p>
                <p className="mt-2 text-xl font-semibold text-slate-100">
                  {result.sampling_rate_hz.toFixed(3)} Hz
                </p>
              </div>
            </div>

            <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950/50">
              <Plot
                data={[
                  {
                    type: "scatter",
                    mode: "lines",
                    name: "Amplitud",
                    x: result.frequencies_hz,
                    y: result.amplitudes,
                    line: { color: "#22d3ee", width: 2 },
                    hovertemplate:
                      "Frecuencia: %{x:.4f} Hz" +
                      "<br>Amplitud: %{y:.5g}" +
                      "<extra></extra>",
                  },
                ]}
                layout={{
                  autosize: true,
                  height: 400,
                  margin: { l: 70, r: 25, t: 25, b: 65 },
                  paper_bgcolor: "rgba(0,0,0,0)",
                  plot_bgcolor: "rgba(2,6,23,0.2)",
                  font: {
                    color: "#cbd5e1",
                    family: "Inter, system-ui, sans-serif",
                  },
                  xaxis: {
                    title: { text: "Frecuencia (Hz)" },
                    gridcolor: "#1e293b",
                    automargin: true,
                  },
                  yaxis: {
                    title: { text: "Amplitud" },
                    gridcolor: "#1e293b",
                    automargin: true,
                  },
                  showlegend: false,
                  uirevision: `instrumenthub-fft-${selectedSeriesKey}`,
                }}
                config={{
                  responsive: true,
                  displaylogo: false,
                  scrollZoom: true,
                }}
                useResizeHandler
                style={{ width: "100%" }}
              />
            </div>

            <p className="mt-3 text-xs leading-5 text-slate-500">
              Resultado calculado sobre la ventana de muestras enviada en la
              última petición. Para analizar una ventana más reciente, vuelve
              a pulsar Calcular FFT.
            </p>
          </>
        )}
      </section>
    </div>
  );
}

export default FFTPage;
