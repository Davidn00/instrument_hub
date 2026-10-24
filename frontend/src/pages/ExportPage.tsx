
import { useState } from "react";
import {
  Download,
  FileJson,
  FileSpreadsheet,
  LoaderCircle,
} from "lucide-react";

import { apiRequest } from "../api/client";

type Dataset =
  | "devices"
  | "experiments"
  | "measurements"
  | "spectra"
  | "alerts";

type ExportFormat = "csv" | "json";

type ExportRow = Record<string, unknown>;

const DATASETS: {
  value: Dataset;
  label: string;
  description: string;
}[] = [
  {
    value: "measurements",
    label: "Measurements",
    description: "Recorded measurements from instrumentation devices.",
  },
  {
    value: "spectra",
    label: "Spectra",
    description: "Persisted spectrum records.",
  },
  {
    value: "experiments",
    label: "Experiments",
    description: "Registered scientific experiments.",
  },
  {
    value: "devices",
    label: "Devices",
    description: "Registered instrumentation devices.",
  },
  {
    value: "alerts",
    label: "Alert history",
    description: "Alert events, including acknowledged events.",
  },
];

function getExportPath(dataset: Dataset, limit: number): string {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: "0",
  });

  switch (dataset) {
    case "devices":
      return "devices";

    case "experiments":
      return "experiments";

    case "measurements":
      return `measurements?${params.toString()}`;

    case "spectra":
      return `spectra?${params.toString()}`;

    case "alerts":
      return `alerts?${params.toString()}`;
  }
}

function csvValue(value: unknown): string {
  let text: string;

  if (value === null || value === undefined) {
    text = "";
  } else if (typeof value === "object") {
    text = JSON.stringify(value);
  } else {
    text = String(value);
  }

  // Escape values containing CSV separators, quotes, or newlines.
  return `"${text.replace(/"/g, '""')}"`;
}

function rowsToCsv(rows: ExportRow[]): string {
  if (rows.length === 0) {
    return "";
  }

  // Preserve every field returned by the API, including optional fields.
  const columns = Array.from(
    new Set(rows.flatMap((row) => Object.keys(row))),
  );

  const header = columns.map(csvValue).join(",");

  const body = rows.map((row) =>
    columns
      .map((column) => csvValue(row[column]))
      .join(","),
  );

  return [header, ...body].join("\r\n");
}

function downloadFile(
  content: string,
  filename: string,
  mimeType: string,
): void {
  const blob = new Blob(["\uFEFF", content], {
    type: `${mimeType};charset=utf-8`,
  });

  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");

  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();

  URL.revokeObjectURL(url);
}

export default function ExportPage() {
  const [dataset, setDataset] = useState<Dataset>("measurements");
  const [format, setFormat] = useState<ExportFormat>("csv");
  const [limit, setLimit] = useState("1000");
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handleExport() {
    setIsExporting(true);
    setError(null);
    setSuccess(null);

    try {
      const path = getExportPath(dataset, Number(limit));
      const rows = await apiRequest<ExportRow[]>(path);

      if (!Array.isArray(rows)) {
        throw new Error(
          "The API response is not a list of records.",
        );
      }

      const timestamp = new Date()
        .toISOString()
        .replace(/[:.]/g, "-");

      const filename = `instrumenthub-${dataset}-${timestamp}.${format}`;

      const content =
        format === "json"
          ? JSON.stringify(rows, null, 2)
          : rowsToCsv(rows);

      const mimeType =
        format === "json"
          ? "application/json"
          : "text/csv";

      downloadFile(content, filename, mimeType);

      setSuccess(
        `Export completed: ${rows.length} record(s) downloaded as ${format.toUpperCase()}.`,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An unexpected error occurred during export.",
      );
    } finally {
      setIsExporting(false);
    }
  }

  const selectedDataset = DATASETS.find(
    (item) => item.value === dataset,
  );

  return (
    <main className="space-y-8">
      <header>
        <p className="text-xs font-medium uppercase tracking-[0.16em] text-cyan-400">
          InstrumentHub / Data management
        </p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-white">
          Export data
        </h1>

        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
          Export persisted instrumentation data and scientific
          records in CSV or JSON format.
        </p>
      </header>

      <section className="max-w-3xl rounded-xl border border-slate-800 bg-slate-900/70 p-5 sm:p-7">
        <div className="flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-lg border border-slate-800 bg-slate-950 text-cyan-300">
            <Download size={22} />
          </span>

          <div>
            <h2 className="font-semibold text-white">
              Export configuration
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              Select the data source and output format.
            </p>
          </div>
        </div>

        <div className="mt-7 space-y-6">
          <div>
            <label
              htmlFor="export-dataset"
              className="mb-2 block text-sm font-medium text-slate-200"
            >
              Dataset
            </label>

            <select
              id="export-dataset"
              value={dataset}
              onChange={(event) =>
                setDataset(event.target.value as Dataset)
              }
              disabled={isExporting}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-3 text-sm text-white outline-none focus:border-cyan-400"
            >
              {DATASETS.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>

            <p className="mt-2 text-xs text-slate-500">
              {selectedDataset?.description}
            </p>
          </div>

          <div>
            <label
              htmlFor="export-format"
              className="mb-2 block text-sm font-medium text-slate-200"
            >
              Output format
            </label>

            <div className="grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={() => setFormat("csv")}
                disabled={isExporting}
                aria-pressed={format === "csv"}
                className={[
                  "flex items-center gap-3 rounded-lg border p-4 text-left transition",
                  format === "csv"
                    ? "border-cyan-400/50 bg-cyan-400/10 text-cyan-200"
                    : "border-slate-700 text-slate-300 hover:bg-slate-800",
                ].join(" ")}
              >
                <FileSpreadsheet size={21} />
                <span>
                  <span className="block text-sm font-semibold">
                    CSV
                  </span>
                  <span className="mt-1 block text-xs opacity-70">
                    Spreadsheet compatible
                  </span>
                </span>
              </button>

              <button
                id="export-format"
                type="button"
                onClick={() => setFormat("json")}
                disabled={isExporting}
                aria-pressed={format === "json"}
                className={[
                  "flex items-center gap-3 rounded-lg border p-4 text-left transition",
                  format === "json"
                    ? "border-cyan-400/50 bg-cyan-400/10 text-cyan-200"
                    : "border-slate-700 text-slate-300 hover:bg-slate-800",
                ].join(" ")}
              >
                <FileJson size={21} />
                <span>
                  <span className="block text-sm font-semibold">
                    JSON
                  </span>
                  <span className="mt-1 block text-xs opacity-70">
                    Structured records
                  </span>
                </span>
              </button>
            </div>
          </div>

          {(
            dataset === "measurements" ||
            dataset === "spectra" ||
            dataset === "alerts"
          ) && (
            <div>
              <label
                htmlFor="export-limit"
                className="mb-2 block text-sm font-medium text-slate-200"
              >
                Maximum number of records
              </label>

              <select
                id="export-limit"
                value={limit}
                onChange={(event) => setLimit(event.target.value)}
                disabled={isExporting}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-3 text-sm text-white outline-none focus:border-cyan-400"
              >
                <option value="100">100 records</option>
                <option value="500">500 records</option>
                <option value="1000">1,000 records</option>
              </select>

              <p className="mt-2 text-xs text-slate-500">
                The export includes the first records returned by
                the API, according to its ordering and pagination.
              </p>
            </div>
          )}

          <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Export summary
            </p>

            <p className="mt-2 text-sm text-slate-200">
              Dataset:{" "}
              <span className="font-medium">
                {selectedDataset?.label}
              </span>
            </p>

            <p className="mt-1 text-sm text-slate-200">
              Format:{" "}
              <span className="font-medium">
                {format.toUpperCase()}
              </span>
            </p>
          </div>

          <button
            type="button"
            onClick={() => void handleExport()}
            disabled={isExporting}
            className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-cyan-400 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
          >
            {isExporting ? (
              <>
                <LoaderCircle size={17} className="animate-spin" />
                Exporting...
              </>
            ) : (
              <>
                <Download size={17} />
                Download export
              </>
            )}
          </button>

          {error && (
            <div
              role="alert"
              className="rounded-lg border border-red-400/30 bg-red-400/5 p-4 text-sm text-red-300"
            >
              <p className="font-semibold">Export failed</p>
              <p className="mt-1 break-words">{error}</p>
            </div>
          )}

          {success && (
            <div
              role="status"
              className="rounded-lg border border-emerald-400/30 bg-emerald-400/5 p-4 text-sm text-emerald-300"
            >
              {success}
            </div>
          )}
        </div>
      </section>

      <p className="max-w-3xl text-xs leading-5 text-slate-500">
        This export uses the existing REST endpoints and generates
        the download in the browser. It does not modify or delete
        records stored in InstrumentHub.
      </p>
    </main>
  );
}
