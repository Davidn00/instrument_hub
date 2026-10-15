
import Plot from "react-plotly.js";
import type { Spectrum } from "../api/types";

interface SpectrumChartProps {
  spectrum: Spectrum | null;
  height?: number;
}

function SpectrumChart({
  spectrum,
  height = 430,
}: SpectrumChartProps) {
  if (!spectrum) {
    return (
      <div
        className="flex min-h-64 items-center justify-center rounded-lg border border-dashed border-slate-700 bg-slate-950/50 p-6 text-center"
        style={{ minHeight: height }}
      >
        <div>
          <p className="font-medium text-slate-300">
            Esperando un espectro
          </p>
          <p className="mt-2 text-sm text-slate-500">
            El gráfico aparecerá cuando el backend publique un evento spectrum.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950/50">
      <Plot
        data={[
          {
            type: "scatter",
            mode: "lines",
            name: spectrum.device_id,
            x: spectrum.wavelength,
            y: spectrum.intensity,
            line: {
              color: "#22d3ee",
              width: 2,
            },
            hovertemplate:
              "%{x:.4f} " +
              `${spectrum.wavelength_unit}` +
              "<br>%{y:.4f} " +
              `${spectrum.intensity_unit}` +
              "<extra></extra>",
          },
        ]}
        layout={{
          autosize: true,
          height,
          margin: { l: 70, r: 25, t: 35, b: 65 },
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(2,6,23,0.2)",
          font: {
            color: "#cbd5e1",
            family: "Inter, system-ui, sans-serif",
          },
          xaxis: {
            title: { text: `Longitud de onda (${spectrum.wavelength_unit})` },
            gridcolor: "#1e293b",
            zerolinecolor: "#334155",
            automargin: true,
          },
          yaxis: {
            title: { text: `Intensidad (${spectrum.intensity_unit})` },
            gridcolor: "#1e293b",
            zerolinecolor: "#334155",
            automargin: true,
          },
          showlegend: false,
          uirevision: "instrumenthub-spectrum",
        }}
        config={{
          responsive: true,
          displaylogo: false,
          scrollZoom: true,
          modeBarButtonsToRemove: ["lasso2d", "select2d"],
        }}
        useResizeHandler
        style={{ width: "100%" }}
      />
    </div>
  );
}

export default SpectrumChart;
