
import { useState, type FormEvent } from "react";
import { Plus, RefreshCw, X } from "lucide-react";
import { ApiError } from "../api/client";
import {
  useCreateExperimentMutation,
  useExperimentsQuery,
} from "../api/queries";
import type { ExperimentCreate, JsonObject } from "../api/types";

const inputClass =
  "mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-slate-100 outline-none placeholder:text-slate-500 focus:border-cyan-500";

const labelClass = "block text-sm font-medium text-slate-300";

function parseMetadata(text: string): JsonObject {
  let parsed: unknown;

  try {
    parsed = JSON.parse(text);
  } catch {
    throw new Error("Los metadatos deben contener JSON válido.");
  }

  if (
    parsed === null ||
    typeof parsed !== "object" ||
    Array.isArray(parsed)
  ) {
    throw new Error(
      'Los metadatos deben ser un objeto JSON, por ejemplo {"project":"InstrumentHub"}.',
    );
  }

  return parsed as JsonObject;
}

function getErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    return `Error HTTP ${error.status}: ${error.message}`;
  }

  return error.message || "Se produjo un error inesperado.";
}

function formatDate(value: string | null): string {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("es-MX", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function ExperimentsPage() {
  const experimentsQuery = useExperimentsQuery();
  const createExperiment = useCreateExperimentMutation();

  const [formOpen, setFormOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [metadataText, setMetadataText] = useState("{}");
  const [validationError, setValidationError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  function resetForm() {
    setName("");
    setDescription("");
    setMetadataText("{}");
    setValidationError("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setValidationError("");
    setSuccessMessage("");

    const trimmedName = name.trim();

    if (!trimmedName) {
      setValidationError("El nombre del experimento es obligatorio.");
      return;
    }

    try {
      const payload: ExperimentCreate = {
        name: trimmedName,
        description: description.trim() || null,
        metadata: parseMetadata(metadataText),
      };

      await createExperiment.mutateAsync(payload);

      resetForm();
      setFormOpen(false);
      setSuccessMessage("Experimento creado correctamente.");
    } catch (error) {
      setValidationError(
        error instanceof Error
          ? getErrorMessage(error)
          : "No se pudo crear el experimento.",
      );
    }
  }

  return (
    <div className="space-y-6">
      <section className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <p className="text-sm text-slate-400">
            Organiza sesiones de medición y experimentos de instrumentación.
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Los experimentos se consultan desde el backend.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => void experimentsQuery.refetch()}
            disabled={experimentsQuery.isFetching}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-700 px-3 py-2.5 text-sm text-slate-200 hover:bg-slate-800 disabled:opacity-50"
          >
            <RefreshCw
              size={16}
              className={experimentsQuery.isFetching ? "animate-spin" : ""}
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
            {formOpen ? "Cerrar formulario" : "Nuevo experimento"}
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
            Crear experimento
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            El formulario envía únicamente los campos de ExperimentCreate.
          </p>

          <form onSubmit={handleSubmit} className="mt-5 space-y-4">
            <label className={labelClass}>
              Nombre del experimento *
              <input
                className={inputClass}
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Caracterización del sensor de temperatura"
                required
              />
            </label>

            <label className={labelClass}>
              Descripción
              <textarea
                className={inputClass + " min-h-24"}
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Objetivo, procedimiento y condiciones del experimento..."
              />
            </label>

            <label className={labelClass}>
              Metadatos (JSON)
              <textarea
                className={inputClass + " min-h-24 font-mono"}
                value={metadataText}
                onChange={(event) => setMetadataText(event.target.value)}
                spellCheck={false}
                required
              />
              <span className="mt-1 block text-xs text-slate-500">
                Ejemplo: {"{\"project\":\"InstrumentHub\",\"operator\":\"lab\"}"}
              </span>
            </label>

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
                disabled={createExperiment.isPending}
                className="rounded-lg bg-cyan-500 px-4 py-2.5 text-sm font-semibold text-slate-950 hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {createExperiment.isPending
                  ? "Guardando..."
                  : "Guardar experimento"}
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/50">
        <div className="border-b border-slate-800 px-5 py-4">
          <h2 className="font-semibold text-slate-100">
            Experimentos registrados
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            {experimentsQuery.data
              ? `${experimentsQuery.data.length} registros`
              : "Esperando respuesta del backend"}
          </p>
        </div>

        {experimentsQuery.isPending ? (
          <p className="p-6 text-sm text-slate-400">
            Cargando experimentos...
          </p>
        ) : experimentsQuery.isError ? (
          <div className="p-6">
            <p role="alert" className="text-sm text-red-300">
              No se pudieron cargar los experimentos:{" "}
              {experimentsQuery.error.message}
            </p>
            <button
              type="button"
              onClick={() => void experimentsQuery.refetch()}
              className="mt-3 text-sm text-cyan-300 hover:underline"
            >
              Reintentar
            </button>
          </div>
        ) : experimentsQuery.data.length === 0 ? (
          <p className="p-6 text-sm text-slate-400">
            Todavía no hay experimentos. Crea uno para comenzar.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="bg-slate-950/70 text-xs uppercase tracking-wide text-slate-400">
                <tr>
                  <th className="px-5 py-3">Nombre</th>
                  <th className="px-5 py-3">Descripción</th>
                  <th className="px-5 py-3">Estado</th>
                  <th className="px-5 py-3">Inicio</th>
                  <th className="px-5 py-3">Fin</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {experimentsQuery.data.map((experiment) => (
                  <tr key={experiment.id} className="hover:bg-slate-800/40">
                    <td className="px-5 py-4 font-medium text-slate-100">
                      {experiment.name}
                    </td>
                    <td className="max-w-sm px-5 py-4 text-slate-300">
                      <span className="line-clamp-2">
                        {experiment.description || "—"}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <span className="rounded-full border border-slate-700 px-2.5 py-1 text-xs text-slate-300">
                        {experiment.status}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-5 py-4 text-slate-300">
                      {formatDate(experiment.started_at)}
                    </td>
                    <td className="whitespace-nowrap px-5 py-4 text-slate-300">
                      {formatDate(experiment.ended_at)}
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

export default ExperimentsPage;
