
import { Link, Route, Routes } from "react-router-dom";
import {
  //Activity,
  //AlertTriangle,
  //BarChart3,
  //Cpu,
  Download,
  //FlaskConical,
  //RadioTower,
  //Waves,
} from "lucide-react";

import AppLayout from "./components/AppLayout";
import DashboardPage from "./pages/DashboardPage";
import ModulePage from "./pages/ModulePage";
import DevicesPage from "./pages/DevicesPage";
import ExperimentsPage from "./pages/ExperimentsPage";
import SpectrumPage from "./pages/SpectrumPage";
import LiveAcquisitionPage from "./pages/LiveAcquisitionPage";
import TimeSeriesPage from "./pages/TimeSeriesPage";
import FFTPage from "./pages/FFTPage";
import FBGAnalysisPage from "./pages/FBGAnalysisPage";
import AlertsPage from "./pages/AlertsPage";
import ExportPage from "./pages/ExportPage";



function NotFoundPage() {
  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900 p-8">
      <p className="text-sm font-medium text-cyan-400">404</p>

      <h2 className="mt-3 text-2xl font-bold text-white">
        Page not found
      </h2>

      <p className="mt-2 text-sm text-slate-400">
        The requested InstrumentHub page does not exist.
      </p>

      <Link
        to="/"
        className="mt-6 inline-flex rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-300"
      >
        Back to dashboard
      </Link>
    </section>
  );
}

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<DashboardPage />} />

        <Route
          path="/devices"
          element={
            <DevicesPage
            />
          }
        />
        <Route path="/live-acquisition" element={<LiveAcquisitionPage />} />

        <Route path="/spectrum" element={<SpectrumPage />} />

        <Route
          path="time-series"
          element={<TimeSeriesPage />}
        />

        <Route
          path="fft"
          element={<FFTPage />}
        />
        <Route
          path="fbg-analysis"
          element={<FBGAnalysisPage />}
        />

        <Route
          path="/experiments"
          element={
            <ExperimentsPage
            />
          }
        />
        <Route path="alerts" element={<AlertsPage />} />
        <Route path="export" element={<ExportPage />} />

        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

export default App;
