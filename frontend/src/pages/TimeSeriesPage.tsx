
import { useEffect, useRef, useState } from "react";
import { Activity, Play, RadioTower, Square } from "lucide-react";

import { ApiError, apiRequest } from "../api/client";
import { useDevicesQuery } from "../api/queries";
import MeasurementTimeSeriesChart from "../components/MeasurementTimeSeriesChart";
import { useMeasurementStream } from "../hooks/useMeasurementStream";
import { buildMeasurementSeries } from "../utils/measurementSeries";

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return `HTTP ${error.status}: ${error.message}`;
  }

  if (error instanceof Error) return error.message;

  return "Ocurrió un error inesperado.";
}

function TimeSeriesPage() {
  const devicesQuery = useDevicesQuery();
  const stream = useMeasurementStream();

  const devices = devicesQuery.data ?? [];

  const [selectedDeviceIds, setSelectedDeviceIds] =
    useState<string[]>([]);
  const [pendingAction, setPendingAction] =
    useState<"start" | "stop" | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const initialized = useRef(false);

  useEffect(() => {
    if (!initialized.current && devices.length > 0) {
      setSelectedDeviceIds(devices.map((device) => device.device_id));
      initialized.current = true;
    }
  }, [devices]);

  const series = buildMeasurementSeries(
    stream.measurements,
    selectedDeviceIds,
    600,
  );

  function toggleDevice(deviceId: string) {
    setSelectedDeviceIds((current) =>
      current.includes(deviceId)
        ? current.filter((item) => item !== deviceId)
        : [...current, deviceId],
    );
  }

  async function runAcquisitionAction(action: "start" | "stop") {
    if (selectedDeviceIds.length === 0) {
      setActionError("Selecciona al menos un dispositivo.");
      return;
    }

    setPendingAction(action);
    setFeedback(null);
    setActionError(null);

    try {
      await Promise.all(
        selectedDeviceIds.map((device_id) =>
          apiRequest<{ device_id: string; status: string }>(
            `acquisition/${action}`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ device_id }),
            },
          ),
        ),
      );

      setFeedback(
        action === "start"
          ? `Solicitud de inicio enviada para ${selectedDeviceIds.length} dispositivo(s).`
          : `Solicitud de detención enviada para ${selectedDeviceIds.length} dispositivo(s).`,
      );
    } catch (error) {
      setActionError(
        `${getErrorMessage(error)} Si seleccionaste varios dispositivos, comprueba el estado de cada uno: algunas solicitudes podrían haberse completado antes del error.`,
      );
    } finally {
      setPendingAction(null);
    }
  }

  const connectionLabel: Record<string, string> = {
    connecting: "Conectando",
    connected: "Conectado",
    reconnecting: "Reconectando",
    disconnected: "Desconectado",
    error: "Error",
  };

  const measurementCount = series.reduce(
    (total, item) => total + item.points.length,
    0,
  );

  return (
    <div className="space-y-6">
      <section>
        <p className="text-sm text-slate-400">
          Supervisa múltiples dispositivos y canales en tiempo real.
          Cada curva representa una serie independiente.
        </p>
      </section>

      {feedback && (
        <div
          role="status"
          className="rounded-lg border border-emerald-800 bg-emerald-950/40 p-3 text-sm text-emerald-300"
        >
          {feedback}
        </div>
      )}

      {actionError && (
        <div
          role="alert"
          className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300"
        >
          {actionError}
        </div>
      )}

      {stream.error && (
        <div
          role="status"
          className="rounded-lg border border-amber-900 bg-amber-950/30 p-3 text-sm text-amber-200"
        >
          {stream.error}
        </div>
      )}

      <section className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <RadioTower size={16} />
            WebSocket
          </div>
          <p className="mt-2 text-lg font-semibold text-slate-100">
            {connectionLabel[stream.status]}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Activity size={16} />
            Series activas
          </div>
          <p className="mt-2 text-lg font-semibold text-slate-100">
            {series.length}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            Mediciones en el buffer
          </div>
          <p className="mt-2 text-lg font-semibold text-slate-100">
            {measurementCount.toLocaleString("es-MX")}
          </p>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(260px,1fr)_minmax(0,2.5fr)]">
        <div className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/50 p-5">
          <div>
            <h2 className="text-lg font-semibold text-slate-100">
              Dispositivos
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              Selecciona los dispositivos que quieres observar y controlar.
            </p>
          </div>

          {devicesQuery.isPending ? (
            <p className="text-sm text-slate-400">Cargando dispositivos...</p>
          ) : devicesQuery.isError ? (
            <p className="text-sm text-red-300">
              {devicesQuery.error.message}
            </p>
          ) : devices.length === 0 ? (
            <p className="text-sm text-slate-400">
              Registra dispositivos desde la sección Devices.
            </p>
          ) : (
            <div className="max-h-72 space-y-3 overflow-y-auto">
              {devices.map((device) => (
                <label
                  key={device.device_id}
                  className="flex cursor-pointer items-start gap-3 text-sm"
                >
                  <input
                    type="checkbox"
                    checked={selectedDeviceIds.includes(device.device_id)}
                    onChange={() => toggleDevice(device.device_id)}
                    disabled={pendingAction !== null}
                    className="mt-1 accent-cyan-400"
                  />
                  <span className="min-w-0">
                    <span className="block font-medium text-slate-200">
                      {device.name}
                    </span>
                    <span className="block break-all text-xs text-slate-500">
                      {device.device_id} · {device.device_type}
                    </span>
                  </span>
                </label>
              ))}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => void runAcquisitionAction("start")}
              disabled={
                selectedDeviceIds.length === 0 ||
                pendingAction !== null
              }
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-500 px-3 py-2.5 text-sm font-semibold text-slate-950 hover:bg-emerald-400 disabled:opacity-40"
            >
              <Play size={16} />
              {pendingAction === "start" ? "Iniciando..." : "Iniciar"}
            </button>

            <button
              type="button"
              onClick={() => void runAcquisitionAction("stop")}
              disabled={
                selectedDeviceIds.length === 0 ||
                pendingAction !== null
              }
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-red-900 bg-red-950/30 px-3 py-2.5 text-sm font-semibold text-red-300 hover:bg-red-950/60 disabled:opacity-40"
            >
              <Square size={15} />
              {pendingAction === "stop" ? "Deteniendo..." : "Detener"}
            </button>
          </div>

          <p className="text-xs leading-5 text-slate-500">
            Las solicitudes se envían por dispositivo. Si una falla,
            comprueba el estado de los demás antes de volver a intentarlo.
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 sm:p-6">
          <div className="mb-5">
            <h2 className="text-lg font-semibold text-slate-100">
              Series temporales
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              Valor de cada canal frente a su marca temporal. Se muestran
              los últimos 600 puntos por serie.
            </p>
          </div>

          <MeasurementTimeSeriesChart series={series} height={470} />
        </div>
      </section>

      <p className="text-xs text-slate-500">
        Los puntos del buffer se conservan únicamente en la memoria de esta
        página. El historial persistido continúa disponible mediante la API REST.
      </p>
    </div>
  );
}

export default TimeSeriesPage;
