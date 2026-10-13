
import { Link, Route, Routes } from "react-router-dom";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  //Cpu,
  Download,
  //FlaskConical,
  RadioTower,
  Waves,
} from "lucide-react";

import AppLayout from "./components/AppLayout";
import DashboardPage from "./pages/DashboardPage";
import ModulePage from "./pages/ModulePage";
import DevicesPage from "./pages/DevicesPage";
import ExperimentsPage from "./pages/ExperimentsPage";



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

        <Route
          path="live-acquisition"
          element={
            <ModulePage
              title="Live Acquisition"
              description="Monitor the acquisition workflow and prepare the real-time measurement workspace."
              icon={RadioTower}
              stage="Parts 29C and 31"
              features={[
                "Acquisition controls based on supported backend operations.",
                "Live measurement stream through WebSocket.",
                "Connection state, errors and reconnection handling.",
              ]}
            />
          }
        />

        <Route
          path="spectrum"
          element={
            <ModulePage
              title="Spectrum"
              description="Explore wavelength and intensity data from supported optical instrumentation."
              icon={Waves}
              stage="Part 30"
              features={[
                "Intensity versus wavelength.",
                "Interactive zoom and axis controls.",
                "Live spectrum updates when available from the backend.",
              ]}
            />
          }
        />

        <Route
          path="time-series"
          element={
            <ModulePage
              title="Time Series"
              description="Inspect measurement histories across instrument channels."
              icon={Activity}
              stage="Part 31"
              features={[
                "Value versus time.",
                "Multiple channels and time-range selection.",
                "Descriptive statistics and interactive Plotly charts.",
              ]}
            />
          }
        />

        <Route
          path="fft"
          element={
            <ModulePage
              title="FFT Analysis"
              description="Visualize signals in the time domain and their frequency-domain representation."
              icon={BarChart3}
              stage="Part 32"
              features={[
                "Time-domain signal.",
                "Frequency spectrum.",
                "Integration with backend signal-processing results.",
              ]}
            />
          }
        />

        <Route
          path="fbg-analysis"
          element={
            <ModulePage
              title="FBG Analysis"
              description="Prepare the analysis workspace for fiber Bragg grating spectra."
              icon={Waves}
              stage="Part 33"
              features={[
                "Spectrum inspection and peak identification.",
                "Bragg wavelength tracking.",
                "Analysis results and associated measurement metadata.",
              ]}
            />
          }
        />

        <Route
          path="/experiments"
          element={
            <ExperimentsPage
            />
          }
        />

        <Route
          path="alerts"
          element={
            <ModulePage
              title="Alerts"
              description="Prepare the operational monitoring and alert review workspace."
              icon={AlertTriangle}
              stage="Part 33"
              features={[
                "Alert listing and severity.",
                "Measurement threshold events when supported.",
                "Alert status and acknowledgement workflows.",
              ]}
            />
          }
        />

        <Route
          path="export"
          element={
            <ModulePage
              title="Export"
              description="Prepare controlled export of instrumentation data and analysis results."
              icon={Download}
              stage="Part 33"
              features={[
                "Selection of datasets and time ranges.",
                "Supported export formats.",
                "Validation and download handling.",
              ]}
            />
          }
        />

        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

export default App;
