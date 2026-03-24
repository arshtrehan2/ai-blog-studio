"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import type {
  AIToolStatus,
  ImproveResponse,
  SummaryResponse,
  TagsResponse,
  SeoTitleResponse,
  TldrResponse,
} from "@/lib/types";

interface Props {
  content: string;
  title?: string;
  onImprove: (improved: string) => void;
  onSummary: (summary: string) => void;
  onTags: (tags: string[]) => void;
  onSeoTitle: (title: string, description: string) => void;
  onTldr: (tldr: string) => void;
}

type ToolKey = "improve" | "summary" | "tags" | "seo" | "tldr";

export function AIToolsPanel({
  content,
  title,
  onImprove,
  onSummary,
  onTags,
  onSeoTitle,
  onTldr,
}: Props) {
  const [statuses, setStatuses] = useState<Record<ToolKey, AIToolStatus>>({
    improve: "idle",
    summary: "idle",
    tags: "idle",
    seo: "idle",
    tldr: "idle",
  });
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<Record<string, string>>({})

  const setStatus = (key: ToolKey, status: AIToolStatus) =>
    setStatuses((s) => ({ ...s, [key]: status }));

  async function runTool(key: ToolKey) {
    if (!content.trim()) {
      setError("Write some content first.");
      return;
    }
    setStatus(key, "loading");
    setError(null);
    try {
      switch (key) {
        case "improve": {
          const r = await api.post<ImproveResponse>("/ai/improve", { content });
          setSuggestions((s) => ({ ...s, improve: r.improved_content }));
          setStatus(key, "suggestion");
          break;
        }
        case "summary": {
          const r = await api.post<SummaryResponse>("/ai/summary", { content });
          onSummary(r.summary);
          setStatus(key, "accepted");
          break;
        }
        case "tags": {
          const r = await api.post<TagsResponse>("/ai/tags", { content, title });
          onTags(r.tags);
          setStatus(key, "accepted");
          break;
        }
        case "seo": {
          const r = await api.post<SeoTitleResponse>("/ai/seo-title", { content, title });
          onSeoTitle(r.seo_title, r.seo_description);
          setStatus(key, "accepted");
          break;
        }
        case "tldr": {
          const r = await api.post<TldrResponse>("/ai/tldr", { content });
          onTldr(r.tldr);
          setStatus(key, "accepted");
          break;
        }
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "AI error");
      setStatus(key, "idle");
    }
  }

  const tools: { key: ToolKey; label: string; description: string }[] = [
    { key: "improve", label: "✨ Improve Writing", description: "Rewrite for clarity & engagement" },
    { key: "summary", label: "📝 Auto Summary", description: "Generate post summary" },
    { key: "tags", label: "🏷 Suggest Tags", description: "Get relevant tags" },
    { key: "seo", label: "🔍 SEO Title & Meta", description: "Optimize for search" },
    { key: "tldr", label: "⚡ TLDR", description: "1-2 sentence overview" },
  ];

  return (
    <div className="p-4">
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">AI Tools</h3>
      {error && (
        <div className="mb-3 p-2 rounded bg-red-50 text-red-600 text-xs">{error}</div>
      )}
      <div className="space-y-2">
        {tools.map(({ key, label, description }) => (
          <div key={key}>
            <button
              onClick={() => runTool(key)}
              disabled={statuses[key] === "loading"}
              className="w-full text-left px-3 py-2 rounded-lg border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50 disabled:opacity-50 transition"
            >
              <div className="text-sm font-medium text-slate-700">{label}</div>
              <div className="text-xs text-slate-400">{description}</div>
              {statuses[key] === "loading" && (
                <div className="text-xs text-indigo-500 mt-1">Generating...</div>
              )}
              {statuses[key] === "accepted" && (
                <div className="text-xs text-green-500 mt-1">✓ Applied</div>
              )}
            </button>
            {/* Diff view for improve */}
            {key === "improve" && statuses.improve === "suggestion" && suggestions.improve && (
              <div className="mt-2 p-3 rounded-lg bg-indigo-50 border border-indigo-200 text-xs">
                <p className="text-indigo-700 font-medium mb-1">Suggested improvement:</p>
                <p className="text-slate-700 line-clamp-4">{suggestions.improve.slice(0, 300)}...</p>
                <div className="flex gap-2 mt-2">
                  <button
                    onClick={() => { onImprove(suggestions.improve!); setStatus("improve", "accepted"); }}
                    className="px-2 py-1 bg-indigo-600 text-white rounded text-xs hover:bg-indigo-700"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => setStatus("improve", "idle")}
                    className="px-2 py-1 bg-slate-200 text-slate-700 rounded text-xs hover:bg-slate-300"
                  >
                    Reject
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
