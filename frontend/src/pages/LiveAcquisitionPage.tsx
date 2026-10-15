
import { useState } from "react";
import { Activity, CircleStop, Play, RadioTower } from "lucide-react";
import { ApiError, apiRequest } from "../api/client";
import { useDevicesQuery } from "../api/queries";
import type { Device } from "../api/types";
import SpectrumChart from "../components/SpectrumChart";
import { useSpectrumStream } from "../hooks/useSpectrumStream";

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return `HTTP ${error.status}: ${error.message}`;
  }

  if (error instanceof Error) return error.message;

  return "Ocurrió un error inesperado.";
}

function LiveAcquisitionPage() {
  const devicesQuery = useDevicesQuery();
  const stream = useSpectrumStream();

  const [selectedDeviceId, setSelectedDeviceId] = useState("");
  const [acquiring, setAcquiring] = useState(false);
  const [pendingAction, setPendingAction] = useState<
    "start" | "stop" | null
  >(null);
  const [feedback, setFeedback] = useState<{
    kind: "success" | "error";
    message: string;
  } | null>(null);

  const devices: Device[] = devicesQuery.data ?? [];

  async function runAcquisitionAction(action: "start" | "stop") {
    if (!selectedDeviceId) {
      setFeedback({
        kind: "error",
        message: "Selecciona un dispositivo antes de iniciar la adquisición.",
      });
      return;
    }

    setPendingAction(action);
    setFeedback(null);

    try {
      await apiRequest<unknown>(`acquisition/${action}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          device_id: selectedDeviceId,
        }),
      });

      setAcquiring(action === "start");

      setFeedback({
        kind: "success",
        message:
          action === "start"
            ? `Solicitud de inicio enviada para ${selectedDeviceId}.`
            : `Solicitud de detención enviada para ${selectedDeviceId}.`,
      });
    } catch (error) {
      setFeedback({
        kind: "error",
        message: getErrorMessage(error),
      });
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

  return (
    <div className="space-y-6">
      <section>
        <p className="text-sm text-slate-400">
          Controla el inicio y la detención de la adquisición y observa los
          espectros que publica el backend.
        </p>
      </section>

      {feedback && (
        <div
          role={feedback.kind === "error" ? "alert" : "status"}
          className={`rounded-lg border p-3 text-sm ${
            feedback.kind === "error"
              ? "border-red-900 bg-red-950/40 text-red-300"
              : "border-emerald-800 bg-emerald-950/40 text-emerald-300"
          }`}
        >
          {feedback.message}
        </div>
      )}

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
        <div className="space-y-5 rounded-xl border border-slate-800 bg-slate-900/50 p-5">
          <div>
            <h2 className="text-lg font-semibold text-slate-100">
              Control de adquisición
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              Selecciona un instrumento registrado.
            </p>
          </div>

          {devicesQuery.isPending ? (
            <p className="text-sm text-slate-400">Cargando dispositivos...</p>
          ) : devicesQuery.isError ? (
            <div>
              <p className="text-sm text-red-300">
                No se pudieron cargar los dispositivos:{" "}
                {devicesQuery.error.message}
              </p>
              <button
                type="button"
                onClick={() => void devicesQuery.refetch()}
                className="mt-2 text-sm text-cyan-300 hover:underline"
              >
                Reintentar
              </button>
            </div>
          ) : devices.length === 0 ? (
            <p className="text-sm text-slate-400">
              No hay dispositivos registrados. Crea uno desde Devices.
            </p>
          ) : (
            <label className="block text-sm font-medium text-slate-300">
              Dispositivo
              <select
                className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-slate-100 outline-none focus:border-cyan-500"
                value={selectedDeviceId}
                onChange={(event) => setSelectedDeviceId(event.target.value)}
                disabled={pendingAction !== null || acquiring}
              >
                <option value="">Selecciona un dispositivo</option>
                {devices.map((device) => (
                  <option key={device.id} value={device.device_id}>
                    {device.name} ({device.device_id})
                  </option>
                ))}
              </select>
            </label>
          )}

          <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Activity size={16} />
              Estado local de la solicitud
            </div>
            <p className="mt-2 text-lg font-semibold text-slate-100">
              {acquiring ? "Adquisición iniciada" : "Sin iniciar desde esta sesión"}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Este estado refleja la última acción aceptada por la API, no una
              confirmación independiente del hardware.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => void runAcquisitionAction("start")}
              disabled={
                !selectedDeviceId ||
                acquiring ||
                pendingAction !== null ||
                devicesQuery.isPending
              }
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-500 px-3 py-2.5 text-sm font-semibold text-slate-950 hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Play size={16} />
              {pendingAction === "start" ? "Iniciando..." : "Iniciar"}
            </button>

            <button
              type="button"
              onClick={() => void runAcquisitionAction("stop")}
              disabled={
                !selectedDeviceId ||
                !acquiring ||
                pendingAction !== null
              }
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-red-900 bg-red-950/30 px-3 py-2.5 text-sm font-semibold text-red-300 hover:bg-red-950/60 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <CircleStop size={16} />
              {pendingAction === "stop" ? "Deteniendo..." : "Detener"}
            </button>
          </div>

          <div className="border-t border-slate-800 pt-4">
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <RadioTower size={16} />
              Conexión de eventos
            </div>
            <p className="mt-2 text-sm text-slate-200">
              {connectionLabel[stream.status]}
            </p>
            {stream.error && (
              <p className="mt-2 text-xs text-amber-300">{stream.error}</p>
            )}
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-slate-100">
              Espectro recibido
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              Último espectro recibido por WebSocket.
            </p>
          </div>

          <SpectrumChart spectrum={stream.spectrum} height={390} />

          {stream.spectrum && (
            <div className="mt-4 flex flex-wrap justify-between gap-2 text-xs text-slate-400">
              <span>Dispositivo: {stream.spectrum.device_id}</span>
              <span>
                Puntos: {stream.spectrum.wavelength.length.toLocaleString("es-MX")}
              </span>
              <span>
                Timestamp: {stream.spectrum.timestamp}
              </span>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

export default LiveAcquisitionPage;
