
import { Menu } from "lucide-react";
import { useLocation } from "react-router-dom";

import {
  useHealthQuery,
  useReadinessQuery,
} from "../api/queries";

interface HeaderProps {
  onMenuClick: () => void;
}

const pageTitles: Record<string, string> = {
  "/": "Dashboard",
  "/devices": "Devices",
  "/live-acquisition": "Live Acquisition",
  "/spectrum": "Spectrum",
  "/time-series": "Time Series",
  "/fft": "FFT Analysis",
  "/fbg-analysis": "FBG Analysis",
  "/experiments": "Experiments",
  "/alerts": "Alerts",
  "/export": "Export",
};

function Header({ onMenuClick }: HeaderProps) {
  const location = useLocation();

  const health = useHealthQuery();
  const readiness = useReadinessQuery();

  const currentTitle =
    pageTitles[location.pathname] ?? "InstrumentHub";

  const apiLabel = health.isPending
    ? "Checking API"
    : health.isError
      ? "API unavailable"
      : "API connected";

  const apiColor = health.isPending
    ? "bg-slate-500"
    : health.isError
      ? "bg-red-400"
      : "bg-emerald-400";

  const databaseLabel = readiness.isPending
    ? "Checking database"
    : readiness.isError
      ? "Database unavailable"
      : "Database ready";

  const databaseColor = readiness.isPending
    ? "bg-slate-500"
    : readiness.isError
      ? "bg-red-400"
      : "bg-emerald-400";

  return (
    <header className="sticky top-0 z-20 flex min-h-20 items-center justify-between gap-4 border-b border-slate-800 bg-slate-950/90 px-4 py-3 backdrop-blur-md sm:px-6 lg:px-8">
      <div className="flex min-w-0 items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="rounded-lg border border-slate-800 p-2 text-slate-300 hover:bg-slate-900 lg:hidden"
          aria-label="Open navigation"
          aria-controls="instrumenthub-sidebar"
        >
          <Menu size={20} />
        </button>

        <div className="min-w-0">
          <p className="hidden text-xs font-medium uppercase tracking-[0.16em] text-slate-500 sm:block">
            InstrumentHub / Workspace
          </p>

          <h1 className="truncate text-lg font-semibold text-slate-100 sm:mt-1 sm:text-xl">
            {currentTitle}
          </h1>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-3">
        <div className="hidden flex-col items-end gap-1.5 xl:flex">
          <span
            className="inline-flex items-center gap-2 text-xs text-slate-300"
            title={
              health.isError
                ? health.error.message
                : "FastAPI health endpoint"
            }
          >
            <span className={`h-2 w-2 rounded-full ${apiColor}`} />
            {apiLabel}
          </span>

          <span
            className="inline-flex items-center gap-2 text-xs text-slate-400"
            title={
              readiness.isError
                ? readiness.error.message
                : "Database readiness endpoint"
            }
          >
            <span className={`h-2 w-2 rounded-full ${databaseColor}`} />
            {databaseLabel}
          </span>
        </div>

        <div
          className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-700 bg-slate-800 text-sm font-semibold text-cyan-300"
          aria-label="InstrumentHub workspace"
          title="InstrumentHub workspace"
        >
          IH
        </div>
      </div>
    </header>
  );
}

export default Header;
