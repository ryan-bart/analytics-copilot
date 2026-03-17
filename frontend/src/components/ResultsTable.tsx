import { useState } from "react";
import type { QueryResponse } from "../types";

interface ResultsTableProps {
  result: QueryResponse;
}

export default function ResultsTable({ result }: ResultsTableProps) {
  const [showSql, setShowSql] = useState(false);

  if (result.error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4">
        <p className="text-sm text-red-700">{result.error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <p className="text-sm text-gray-700">{result.explanation}</p>
        <button
          onClick={() => setShowSql(!showSql)}
          className="mt-2 text-xs text-blue-600 hover:text-blue-800"
        >
          {showSql ? "Hide SQL" : "Show SQL"}
        </button>
        {showSql && (
          <pre className="mt-2 overflow-x-auto rounded bg-gray-900 p-3 text-xs text-green-400">
            <code>{result.sql}</code>
          </pre>
        )}
      </div>

      {result.rows.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {result.columns.map((col) => (
                  <th
                    key={col}
                    className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {result.rows.map((row, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  {result.columns.map((col) => (
                    <td key={col} className="whitespace-nowrap px-4 py-2 text-sm text-gray-700">
                      {String(row[col] ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          <div className="border-t border-gray-200 bg-gray-50 px-4 py-2 text-xs text-gray-500">
            {result.row_count} row{result.row_count !== 1 ? "s" : ""}
          </div>
        </div>
      )}
    </div>
  );
}
