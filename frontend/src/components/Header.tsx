
import { Menu } from "lucide-react";
import { useLocation } from "react-router-dom";

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

  const currentTitle = pageTitles[location.pathname] ?? "InstrumentHub";

  return (
    <header className="sticky top-0 z-20 flex h-20 items-center justify-between border-b border-slate-800 bg-slate-950/90 px-4 backdrop-blur-md sm:px-6 lg:px-8">
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

      <div className="flex items-center gap-3">
        <span className="hidden items-center gap-2 rounded-full border border-slate-800 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-300 sm:inline-flex">
          <span className="h-2 w-2 rounded-full bg-amber-400" />
          API not connected
        </span>

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
