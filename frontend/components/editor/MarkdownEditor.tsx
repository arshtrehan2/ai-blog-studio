"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";

interface Props {
  value: string;
  onChange: (value: string) => void;
  minHeight?: string;
}

export default function MarkdownEditor({
  value,
  onChange,
  minHeight = "400px",
}: Props) {
  const [tab, setTab] = useState<"write" | "preview">("write");

  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden bg-white">
      {/* Toolbar */}
      <div className="flex items-center border-b border-slate-200 bg-slate-50 px-3 py-2 gap-1">
        <button
          type="button"
          onClick={() => setTab("write")}
          className={`text-xs px-3 py-1 rounded-md font-medium transition-colors ${
            tab === "write"
              ? "bg-white shadow-sm text-slate-800"
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          Write
        </button>
        <button
          type="button"
          onClick={() => setTab("preview")}
          className={`text-xs px-3 py-1 rounded-md font-medium transition-colors ${
            tab === "preview"
              ? "bg-white shadow-sm text-slate-800"
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          Preview
        </button>

        {/* Markdown shortcuts */}
        {tab === "write" && (
          <div className="ml-auto flex gap-1">
            {[
              { label: "B", insert: "**bold**" },
              { label: "I", insert: "_italic_" },
              { label: "<>", insert: "`code`" },
            ].map(({ label, insert }) => (
              <button
                key={label}
                type="button"
                onClick={() => onChange(value + insert)}
                className="text-xs px-2 py-1 text-slate-500 hover:bg-slate-200 rounded font-mono"
              >
                {label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Panes */}
      {tab === "write" ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Write your post in Markdown…"
          className="w-full p-4 font-mono text-sm text-slate-800 bg-white resize-none outline-none"
          style={{ minHeight }}
        />
      ) : (
        <div
          className="prose prose-slate max-w-none p-4 overflow-auto"
          style={{ minHeight }}
        >
          {value ? (
            <ReactMarkdown>{value}</ReactMarkdown>
          ) : (
            <p className="text-slate-400 text-sm italic">Nothing to preview.</p>
          )}
        </div>
      )}
    </div>
  );
}
