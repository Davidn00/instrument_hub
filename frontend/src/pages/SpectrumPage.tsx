
import { Activity, RadioTower, Waves } from "lucide-react";
import SpectrumChart from "../components/SpectrumChart";
import { useSpectraQuery } from "../api/queries";
import { useSpectrumStream } from "../hooks/useSpectrumStream";

function formatTimestamp(value: string | null): string {
  if (!value) return "Sin datos";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("es-MX", {
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(date);
}

function SpectrumPage() {
  const stream = useSpectrumStream();
  const history = useSpectraQuery(1);

  // El espectro más reciente del WebSocket tiene prioridad.
  // Si todavía no llega ninguno, mostramos el último registro REST.
  const spectrum = stream.spectrum ?? history.data?.[0] ?? null;

  const connectionLabel: Record<string, string> = {
    connecting: "Conectando",
    connected: "Conectado",
    reconnecting: "Reconectando",
    disconnected: "Desconectado",
    error: "Error de conexión",
  };

  const connectionColor =
    stream.status === "connected"
      ? "border-emerald-800 bg-emerald-950/40 text-emerald-300"
      : stream.status === "error"
        ? "border-red-900 bg-red-950/40 text-red-300"
        : "border-slate-700 bg-slate-900 text-slate-300";

  return (
    <div className="space-y-6">
      <section className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <p className="text-sm text-slate-400">
            Visualización de espectros ópticos recibidos desde InstrumentHub.
          </p>
          <p className="mt-1 text-xs text-slate-500">
            La curva se actualiza al recibir un nuevo evento spectrum.
          </p>
        </div>

        <span
          className={`inline-flex w-fit items-center gap-2 rounded-full border px-3 py-2 text-xs font-medium ${connectionColor}`}
        >
          <span
            className={`h-2 w-2 rounded-full ${
              stream.status === "connected"
                ? "bg-emerald-400"
                : stream.status === "error"
                  ? "bg-red-400"
                  : "bg-slate-400"
            }`}
          />
          <RadioTower size={14} />
          WebSocket: {connectionLabel[stream.status]}
        </span>
      </section>

      {stream.error && (
        <div
          role="status"
          className="rounded-lg border border-amber-900 bg-amber-950/30 p-3 text-sm text-amber-200"
        >
          {stream.error}
        </div>
      )}

      {history.isError && !stream.spectrum && (
        <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-3 text-sm text-slate-400">
          No fue posible cargar el espectro histórico: {history.error.message}
        </div>
      )}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Waves size={16} />
            Dispositivo
          </div>
          <p className="mt-2 truncate text-lg font-semibold text-slate-100">
            {spectrum?.device_id ?? "Sin datos"}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Activity size={16} />
            Puntos del espectro
          </div>
          <p className="mt-2 text-lg font-semibold text-slate-100">
            {spectrum?.wavelength.length.toLocaleString("es-MX") ?? "—"}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 sm:col-span-2 xl:col-span-1">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <RadioTower size={16} />
            Último espectro
          </div>
          <p className="mt-2 text-sm font-semibold text-slate-100">
            {formatTimestamp(
              stream.spectrum?.timestamp ?? spectrum?.timestamp ?? null,
            )}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            {stream.spectrum
              ? "Recibido por WebSocket"
              : spectrum
                ? "Recuperado mediante REST"
                : "Aún no se han recibido datos"}
          </p>
        </div>
      </section>

      <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 sm:p-6">
        <div className="mb-5">
          <h2 className="text-lg font-semibold text-slate-100">
            Espectro óptico
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Intensidad en función de la longitud de onda.
          </p>
        </div>

        <SpectrumChart spectrum={spectrum} height={460} />
      </section>

      <p className="text-xs text-slate-500">
        Esta vista conserva el último espectro recibido en memoria. La consulta
        REST se utiliza como respaldo inicial, no como sustituto del flujo en vivo.
      </p>
    </div>
  );
}

export default SpectrumPage;
