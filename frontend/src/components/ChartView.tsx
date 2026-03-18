import { lazy, Suspense } from "react";
import type { QueryResponse } from "../types";

// react-plotly.js is CJS and its default export doesn't resolve cleanly
// under Vite's ESM interop — use a lazy dynamic import to unwrap it at runtime.
const Plot = lazy(() =>
  import("react-plotly.js").then((mod) => {
    // Walk through possible shapes: { default: Component }, { default: { default: Component } }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let comp = mod as any;
    while (comp && typeof comp === "object" && "default" in comp) {
      comp = comp.default;
    }
    return { default: comp };
  })
);

interface ChartViewProps {
  result: QueryResponse;
}

export default function ChartView({ result }: ChartViewProps) {
  if (!result.chart_json) return null;

  const chartJson = result.chart_json as Record<string, unknown>;
  const data = chartJson.data as Plotly.Data[] | undefined;
  const layout = chartJson.layout as Partial<Plotly.Layout> | undefined;

  if (!Array.isArray(data)) return null;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <Suspense fallback={<div className="h-96 animate-pulse bg-gray-100 rounded" />}>
        <Plot
          data={data}
          layout={{
            ...(layout ?? {}),
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
      </Suspense>
    </div>
  );
}
