
import Plot from "react-plotly.js";
import type { MeasurementSeries } from "../api/types";

interface MeasurementTimeSeriesChartProps {
  series: MeasurementSeries[];
  height?: number;
}

function MeasurementTimeSeriesChart({
  series,
  height = 430,
}: MeasurementTimeSeriesChartProps) {
  if (series.length === 0) {
    return (
      <div
        className="flex items-center justify-center rounded-lg border border-dashed border-slate-700 bg-slate-950/50 p-6 text-center"
        style={{ minHeight: height }}
      >
        <div>
          <p className="font-medium text-slate-300">
            Esperando mediciones
          </p>
          <p className="mt-2 text-sm text-slate-500">
            Inicia la adquisición de uno o más dispositivos para
            visualizar las series temporales.
          </p>
        </div>
      </div>
    );
  }

  const units = [...new Set(series.map((item) => item.unit))];

  return (
    <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950/50">
      <Plot
        data={series.map((item) => ({
          type: "scatter" as const,
          mode: "lines" as const,
          name: item.label,
          x: item.points.map((point) => point.timestamp),
          y: item.points.map((point) => point.value),
          customdata: item.points.map((point) => [
            point.quality,
          ]),
          hovertemplate:
            "%{x|%Y-%m-%d %H:%M:%S.%L}" +
            "<br>Valor: %{y:.5g}" +
            "<br>Calidad: %{customdata[0]}" +
            "<extra>%{fullData.name}</extra>",
          line: { width: 2 },
        }))}
        layout={{
          autosize: true,
          height,
          margin: { l: 70, r: 25, t: 25, b: 75 },
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(2,6,23,0.2)",
          font: {
            color: "#cbd5e1",
            family: "Inter, system-ui, sans-serif",
          },
          xaxis: {
            title: { text: "Tiempo" },
            type: "date",
            gridcolor: "#1e293b",
            automargin: true,
          },
          yaxis: {
            title: {
              text:
                units.length === 1
                  ? `Valor (${units[0]})`
                  : "Valor (unidades mixtas)",
            },
            gridcolor: "#1e293b",
            automargin: true,
          },
          legend: {
            orientation: "h",
            y: -0.25,
          },
          hovermode: "closest",
          uirevision: "instrumenthub-time-series",
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

export default MeasurementTimeSeriesChart;
