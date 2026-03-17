import { useEffect, useState } from "react";

interface HistoryItem {
  id: number;
  question: string;
  chart_type: string;
  row_count: number;
  created_at: string;
}

interface HistoryPanelProps {
  onSelect: (question: string) => void;
  refreshKey: number;
}

export default function HistoryPanel({ onSelect, refreshKey }: HistoryPanelProps) {
  const [items, setItems] = useState<HistoryItem[]>([]);

  useEffect(() => {
    fetch("/api/history")
      .then((r) => r.json())
      .then((data) => setItems(data.items ?? []))
      .catch(console.error);
  }, [refreshKey]);

  if (items.length === 0) return null;

  return (
    <div className="mt-6">
      <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
        Recent Queries
      </h3>
      <div className="space-y-1">
        {items.map((item) => (
          <button
            key={item.id}
            onClick={() => onSelect(item.question)}
            className="block w-full rounded px-2 py-1.5 text-left text-xs text-gray-600 hover:bg-gray-100"
          >
            <div className="truncate font-medium">{item.question}</div>
            <div className="text-gray-400">
              {item.row_count} rows · {item.chart_type}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
