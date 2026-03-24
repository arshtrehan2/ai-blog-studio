"use client";
import { useState } from "react";
import ReactMarkdown from "react-markdown";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export default function MarkdownEditor({ value, onChange }: Props) {
  const [mode, setMode] = useState<"edit" | "preview" | "split">("split");

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="flex gap-1 px-4 py-2 border-b border-slate-100 bg-white">
        {(["edit", "split", "preview"] as const).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`px-3 py-1 text-xs rounded capitalize ${
              mode === m
                ? "bg-indigo-100 text-indigo-700 font-semibold"
                : "text-slate-500 hover:bg-slate-100"
            }`}
          >
            {m}
          </button>
        ))}
      </div>

      {/* Panes */}
      <div className="flex flex-1 overflow-hidden">
        {(mode === "edit" || mode === "split") && (
          <textarea
            className={`${
              mode === "split" ? "w-1/2 border-r border-slate-200" : "w-full"
            } h-full p-4 font-mono text-sm resize-none outline-none bg-white text-slate-800 leading-relaxed`}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Write your post in Markdown..."
            spellCheck
          />
        )}
        {(mode === "preview" || mode === "split") && (
          <div
            className={`${
              mode === "split" ? "w-1/2" : "w-full"
            } h-full overflow-y-auto p-6 prose prose-slate max-w-none`}
          >
            <ReactMarkdown>{value || "*Nothing to preview yet*"}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
