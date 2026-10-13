
import { useState, type FormEvent } from "react";
import { Plus, RefreshCw, X } from "lucide-react";
import { ApiError } from "../api/client";
import { useCreateDeviceMutation, useDevicesQuery } from "../api/queries";
import type { ChannelCreate, DeviceCreate, JsonObject } from "../api/types";

interface ChannelForm {
  name: string;
  unit: string;
  description: string;
  metadataText: string;
}

const emptyChannel = (): ChannelForm => ({
  name: "",
  unit: "",
  description: "",
  metadataText: "{}",
});

const inputClass =
  "mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-slate-100 outline-none placeholder:text-slate-500 focus:border-cyan-500";

const labelClass = "block text-sm font-medium text-slate-300";

function parseMetadata(text: string, label: string): JsonObject {
  let parsed: unknown;

  try {
    parsed = JSON.parse(text);
  } catch {
    throw new Error(`${label}: introduce un JSON válido.`);
  }

  if (
    parsed === null ||
    typeof parsed !== "object" ||
    Array.isArray(parsed)
  ) {
    throw new Error(`${label}: el valor debe ser un objeto JSON, por ejemplo {}.`);
  }

  return parsed as JsonObject;
}

function getErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    return `Error HTTP ${error.status}: ${error.message}`;
  }

  return error.message || "Se produjo un error inesperado.";
}

function DevicesPage() {
  const devicesQuery = useDevicesQuery();
  const createDevice = useCreateDeviceMutation();

  const [formOpen, setFormOpen] = useState(false);
  const [deviceId, setDeviceId] = useState("");
  const [name, setName] = useState("");
  const [deviceType, setDeviceType] = useState("SIMULATED");
  const [deviceInterface, setDeviceInterface] = useState("");
  const [metadataText, setMetadataText] = useState("{}");
  const [channels, setChannels] = useState<ChannelForm[]>([emptyChannel()]);
  const [validationError, setValidationError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  function resetForm() {
    setDeviceId("");
    setName("");
    setDeviceType("SIMULATED");
    setDeviceInterface("");
    setMetadataText("{}");
    setChannels([emptyChannel()]);
    setValidationError("");
  }

  function updateChannel(
    index: number,
    field: keyof ChannelForm,
    value: string,
  ) {
    setChannels((current) =>
      current.map((channel, channelIndex) =>
        channelIndex === index
          ? { ...channel, [field]: value }
          : channel,
      ),
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");
    setSuccessMessage("");

    const trimmedDeviceId = deviceId.trim();
    const trimmedName = name.trim();
    const trimmedDeviceType = deviceType.trim();

    if (!trimmedDeviceId || !trimmedName || !trimmedDeviceType) {
      setValidationError(
        "Completa el identificador, el nombre y el tipo de dispositivo.",
      );
      return;
    }

    try {
      const metadata = parseMetadata(metadataText, "Metadatos del dispositivo");

      const channelPayload: ChannelCreate[] = channels.map(
        (channel, index) => {
          if (!channel.name.trim() || !channel.unit.trim()) {
            throw new Error(
              `Canal ${index + 1}: el nombre y la unidad son obligatorios.`,
            );
          }

          return {
            name: channel.name.trim(),
            unit: channel.unit.trim(),
            description: channel.description.trim() || null,
            metadata: parseMetadata(
              channel.metadataText,
              `Metadatos del canal ${index + 1}`,
            ),
          };
        },
      );

      const payload: DeviceCreate = {
        device_id: trimmedDeviceId,
        name: trimmedName,
        device_type: trimmedDeviceType,
        interface: deviceInterface.trim() || null,
        metadata,
        channels: channelPayload,
      };

      await createDevice.mutateAsync(payload);

      resetForm();
      setFormOpen(false);
      setSuccessMessage("Dispositivo creado correctamente.");
    } catch (error) {
      setValidationError(
        error instanceof Error
          ? getErrorMessage(error)
          : "No se pudo crear el dispositivo.",
      );
    }
  }

  return (
    <div className="space-y-6">
      <section className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <p className="text-sm text-slate-400">
            Registro e inventario de instrumentos conectados a la plataforma.
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Los datos se obtienen del backend de InstrumentHub.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => void devicesQuery.refetch()}
            disabled={devicesQuery.isFetching}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-700 px-3 py-2.5 text-sm text-slate-200 hover:bg-slate-800 disabled:opacity-50"
          >
            <RefreshCw
              size={16}
              className={devicesQuery.isFetching ? "animate-spin" : ""}
            />
            Actualizar
          </button>

          <button
            type="button"
            onClick={() => {
              setSuccessMessage("");
              setValidationError("");
              setFormOpen((open) => !open);
            }}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-cyan-500 px-4 py-2.5 text-sm font-semibold text-slate-950 hover:bg-cyan-400"
          >
            {formOpen ? <X size={16} /> : <Plus size={16} />}
            {formOpen ? "Cerrar formulario" : "Nuevo dispositivo"}
          </button>
        </div>
      </section>

      {successMessage && (
        <div
          role="status"
          className="rounded-lg border border-emerald-800 bg-emerald-950/40 p-3 text-sm text-emerald-300"
        >
          {successMessage}
        </div>
      )}

      {formOpen && (
        <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <h2 className="text-lg font-semibold text-slate-100">
            Registrar dispositivo
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Completa los campos del contrato DeviceCreate.
          </p>

          <form onSubmit={handleSubmit} className="mt-5 space-y-5">
            <div className="grid gap-4 md:grid-cols-2">
              <label className={labelClass}>
                Identificador único *
                <input
                  className={inputClass}
                  value={deviceId}
                  onChange={(event) => setDeviceId(event.target.value)}
                  placeholder="sensor-temp-001"
                  required
                />
              </label>

              <label className={labelClass}>
                Nombre *
                <input
                  className={inputClass}
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="Sensor de temperatura"
                  required
                />
              </label>

              <label className={labelClass}>
                Tipo de dispositivo *
                <select
                  className={inputClass}
                  value={deviceType}
                  onChange={(event) => setDeviceType(event.target.value)}
                  required
                >
                  <option value="SIMULATED">Simulado</option>
                  <option value="SERIAL">Serial</option>
                  <option value="MQTT">MQTT</option>
                  <option value="TCP">TCP</option>
                  <option value="IBSEN">IBSEN</option>
                  <option value="FBG">FBG</option>
                  <option value="OTHER">Otro</option>
                </select>
              </label>

              <label className={labelClass}>
                Interfaz
                <input
                  className={inputClass}
                  value={deviceInterface}
                  onChange={(event) =>
                    setDeviceInterface(event.target.value)
                  }
                  placeholder="COM3, /dev/ttyUSB0, mqtt://..."
                />
              </label>
            </div>

            <label className={labelClass}>
              Metadatos del dispositivo (JSON)
              <textarea
                className={inputClass + " min-h-20 font-mono"}
                value={metadataText}
                onChange={(event) => setMetadataText(event.target.value)}
                spellCheck={false}
                required
              />
              <span className="mt-1 block text-xs text-slate-500">
                Debe ser un objeto JSON. Usa {"{}"} si no necesitas metadatos.
              </span>
            </label>

            <div className="space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <h3 className="font-medium text-slate-200">Canales</h3>
                  <p className="text-xs text-slate-500">
                    Cada canal requiere nombre, unidad y metadatos.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() =>
                    setChannels((current) => [...current, emptyChannel()])
                  }
                  className="rounded-lg border border-slate-700 px-3 py-2 text-sm text-cyan-300 hover:bg-slate-800"
                >
                  Añadir canal
                </button>
              </div>

              {channels.map((channel, index) => (
                <div
                  key={index}
                  className="space-y-3 rounded-lg border border-slate-800 bg-slate-950/50 p-4"
                >
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold text-slate-200">
                      Canal {index + 1}
                    </h4>
                    <button
                      type="button"
                      onClick={() =>
                        setChannels((current) =>
                          current.filter((_, i) => i !== index),
                        )
                      }
                      aria-label={`Eliminar canal ${index + 1}`}
                      className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-red-300"
                    >
                      <X size={16} />
                    </button>
                  </div>

                  <div className="grid gap-3 md:grid-cols-2">
                    <label className={labelClass}>
                      Nombre *
                      <input
                        className={inputClass}
                        value={channel.name}
                        onChange={(event) =>
                          updateChannel(index, "name", event.target.value)
                        }
                        placeholder="temperature"
                        required
                      />
                    </label>

                    <label className={labelClass}>
                      Unidad *
                      <input
                        className={inputClass}
                        value={channel.unit}
                        onChange={(event) =>
                          updateChannel(index, "unit", event.target.value)
                        }
                        placeholder="°C"
                        required
                      />
                    </label>
                  </div>

                  <label className={labelClass}>
                    Descripción
                    <input
                      className={inputClass}
                      value={channel.description}
                      onChange={(event) =>
                        updateChannel(index, "description", event.target.value)
                      }
                      placeholder="Temperatura medida por el sensor"
                    />
                  </label>

                  <label className={labelClass}>
                    Metadatos del canal (JSON)
                    <textarea
                      className={inputClass + " min-h-16 font-mono"}
                      value={channel.metadataText}
                      onChange={(event) =>
                        updateChannel(index, "metadataText", event.target.value)
                      }
                      spellCheck={false}
                      required
                    />
                  </label>
                </div>
              ))}
            </div>

            {validationError && (
              <div
                role="alert"
                className="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-300"
              >
                {validationError}
              </div>
            )}

            <div className="flex flex-wrap justify-end gap-3">
              <button
                type="button"
                onClick={() => {
                  resetForm();
                  setFormOpen(false);
                }}
                className="rounded-lg border border-slate-700 px-4 py-2.5 text-sm text-slate-200 hover:bg-slate-800"
              >
                Cancelar
              </button>

              <button
                type="submit"
                disabled={createDevice.isPending}
                className="rounded-lg bg-cyan-500 px-4 py-2.5 text-sm font-semibold text-slate-950 hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {createDevice.isPending ? "Guardando..." : "Guardar dispositivo"}
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/50">
        <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
          <div>
            <h2 className="font-semibold text-slate-100">Dispositivos registrados</h2>
            <p className="mt-1 text-xs text-slate-500">
              {devicesQuery.data
                ? `${devicesQuery.data.length} registros`
                : "Esperando respuesta del backend"}
            </p>
          </div>
        </div>

        {devicesQuery.isPending ? (
          <p className="p-6 text-sm text-slate-400">Cargando dispositivos...</p>
        ) : devicesQuery.isError ? (
          <div className="p-6">
            <p role="alert" className="text-sm text-red-300">
              No se pudieron cargar los dispositivos: {devicesQuery.error.message}
            </p>
            <button
              type="button"
              onClick={() => void devicesQuery.refetch()}
              className="mt-3 text-sm text-cyan-300 hover:underline"
            >
              Reintentar
            </button>
          </div>
        ) : devicesQuery.data.length === 0 ? (
          <p className="p-6 text-sm text-slate-400">
            No hay dispositivos registrados. Usa «Nuevo dispositivo» para crear el primero.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="bg-slate-950/70 text-xs uppercase tracking-wide text-slate-400">
                <tr>
                  <th className="px-5 py-3">Dispositivo</th>
                  <th className="px-5 py-3">Identificador</th>
                  <th className="px-5 py-3">Tipo</th>
                  <th className="px-5 py-3">Interfaz</th>
                  <th className="px-5 py-3">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {devicesQuery.data.map((device) => (
                  <tr key={device.id} className="hover:bg-slate-800/40">
                    <td className="px-5 py-4 font-medium text-slate-100">
                      {device.name}
                    </td>
                    <td className="px-5 py-4 font-mono text-xs text-slate-300">
                      {device.device_id}
                    </td>
                    <td className="px-5 py-4 text-slate-300">
                      {device.device_type}
                    </td>
                    <td className="px-5 py-4 text-slate-300">
                      {device.interface || "—"}
                    </td>
                    <td className="px-5 py-4">
                      <span className="rounded-full border border-slate-700 px-2.5 py-1 text-xs text-slate-300">
                        {device.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default DevicesPage;
