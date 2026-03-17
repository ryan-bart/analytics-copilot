import { useState } from "react";
import { queryData } from "./api/client";
import QueryInput from "./components/QueryInput";
import ResultsTable from "./components/ResultsTable";
import SchemaPanel from "./components/SchemaPanel";
import type { QueryResponse } from "./types";

export default function App() {
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleQuery = async (question: string) => {
    setIsLoading(true);
    setResult(null);
    try {
      const data = await queryData(question);
      setResult(data);
    } catch (err) {
      setResult({
        question,
        sql: "",
        explanation: "",
        suggested_chart_type: "table",
        columns: [],
        rows: [],
        row_count: 0,
        error: err instanceof Error ? err.message : "An error occurred",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 shrink-0 border-r border-gray-200 bg-white p-4 overflow-y-auto">
        <h2 className="mb-4 text-lg font-semibold text-gray-800">Analytics Copilot</h2>
        <SchemaPanel />
      </aside>

      <main className="flex-1 p-6">
        <div className="mx-auto max-w-4xl space-y-6">
          <QueryInput onSubmit={handleQuery} isLoading={isLoading} />
          {result && <ResultsTable result={result} />}
        </div>
      </main>
    </div>
  );
}
