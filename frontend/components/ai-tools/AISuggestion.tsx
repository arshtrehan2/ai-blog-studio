"use client";

interface Props {
  type: string;
  suggestion: string;
  onAccept: () => void;
  onReject: () => void;
}

const LABELS: Record<string, string> = {
  improve: "Improved Content",
  summary: "Generated Summary",
  tags: "Suggested Tags",
  "seo-title": "SEO Title & Description",
  tldr: "TLDR",
};

export default function AISuggestion({
  type,
  suggestion,
  onAccept,
  onReject,
}: Props) {
  return (
    <div className="rounded-xl border border-blue-200 bg-blue-50 p-3">
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs font-semibold text-blue-700">
          ✨ {LABELS[type] ?? "AI Suggestion"}
        </p>
      </div>

      <div className="bg-white rounded-lg border border-blue-100 p-2 mb-3 max-h-40 overflow-y-auto">
        <p className="text-xs text-slate-700 whitespace-pre-wrap">{suggestion}</p>
      </div>

      <div className="flex gap-2">
        <button
          type="button"
          onClick={onAccept}
          className="flex-1 text-xs bg-blue-600 hover:bg-blue-700 text-white font-semibold px-3 py-1.5 rounded-lg transition-colors"
        >
          ✓ Accept
        </button>
        <button
          type="button"
          onClick={onReject}
          className="flex-1 text-xs border border-slate-300 hover:bg-slate-50 text-slate-600 font-medium px-3 py-1.5 rounded-lg transition-colors"
        >
          × Dismiss
        </button>
      </div>
    </div>
  );
}
