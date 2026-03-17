import { useEffect, useState } from "react";
import { getSchema } from "../api/client";
import type { SchemaResponse } from "../types";

export default function SchemaPanel() {
  const [schema, setSchema] = useState<SchemaResponse | null>(null);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  useEffect(() => {
    getSchema().then(setSchema).catch(console.error);
  }, []);

  const toggleTable = (name: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  if (!schema) return <div className="text-sm text-gray-400">Loading schema...</div>;

  return (
    <div className="space-y-1">
      <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
        Database Schema
      </h3>
      {schema.tables.map((table) => (
        <div key={table.name}>
          <button
            onClick={() => toggleTable(table.name)}
            className="flex w-full items-center justify-between rounded px-2 py-1 text-sm font-medium text-gray-700 hover:bg-gray-100"
          >
            <span>{table.name}</span>
            <span className="text-xs text-gray-400">
              {expanded.has(table.name) ? "−" : "+"}
            </span>
          </button>
          {expanded.has(table.name) && (
            <div className="ml-3 space-y-0.5 border-l border-gray-200 pl-3">
              {table.columns.map((col) => (
                <div key={col.name} className="flex items-center gap-2 text-xs text-gray-600">
                  <span className={col.primary_key ? "font-semibold" : ""}>
                    {col.name}
                  </span>
                  <span className="text-gray-400">{col.type}</span>
                  {col.primary_key && (
                    <span className="rounded bg-yellow-100 px-1 text-[10px] text-yellow-700">
                      PK
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
