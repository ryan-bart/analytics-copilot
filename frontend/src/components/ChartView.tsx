import Plot from "react-plotly.js";
import type { QueryResponse } from "../types";

interface ChartViewProps {
  result: QueryResponse;
}

export default function ChartView({ result }: ChartViewProps) {
  if (!result.chart_json) return null;

  const { data, layout } = result.chart_json as {
    data: Plotly.Data[];
    layout: Partial<Plotly.Layout>;
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <Plot
        data={data}
        layout={{
          ...layout,
          autosize: true,
          font: { family: "system-ui, sans-serif", size: 12 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
        }}
        config={{ responsive: true, displayModeBar: false }}
        className="w-full"
        useResizeHandler
        style={{ width: "100%", height: layout?.height ? `${layout.height}px` : "400px" }}
      />
    </div>
  );
}
