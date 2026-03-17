import { useState } from "react";
import type { QueryResponse } from "../types";

interface DaxMeasure {
  name: string;
  expression: string;
  description: string;
}

interface DaxPanelProps {
  result: QueryResponse;
}

export default function DaxPanel({ result }: DaxPanelProps) {
  const [measures, setMeasures] = useState<DaxMeasure[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  const handleSuggest = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/dax", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: result.question,
          sql: result.sql,
          columns: result.columns,
        }),
      });
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        setMeasures(data.measures);
      }
    } catch {
      setError("Failed to generate DAX measures");
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string, name: string) => {
    navigator.clipboard.writeText(text);
    setCopied(name);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700">Power BI DAX Measures</h3>
        <button
          onClick={handleSuggest}
          disabled={isLoading}
          className="rounded bg-purple-600 px-3 py-1 text-xs font-medium text-white hover:bg-purple-700 disabled:opacity-50"
        >
          {isLoading ? "Generating..." : "Suggest DAX Measures"}
        </button>
      </div>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

      {measures.length > 0 && (
        <div className="mt-3 space-y-3">
          {measures.map((m) => (
            <div key={m.name} className="rounded border border-gray-100 bg-gray-50 p-3">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-sm font-medium text-gray-800">{m.name}</span>
                  <p className="text-xs text-gray-500">{m.description}</p>
                </div>
                <button
                  onClick={() => copyToClipboard(m.expression, m.name)}
                  className="shrink-0 text-xs text-blue-600 hover:text-blue-800"
                >
                  {copied === m.name ? "Copied!" : "Copy"}
                </button>
              </div>
              <pre className="mt-2 overflow-x-auto rounded bg-gray-900 p-2 text-xs text-amber-300">
                <code>{m.expression}</code>
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
