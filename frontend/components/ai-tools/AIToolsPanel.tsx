"use client";

import { useState } from "react";
import { aiApi } from "@/lib/api";
import AISuggestion from "./AISuggestion";

type AITool = "improve" | "summary" | "tags" | "seo-title" | "tldr" | null;

interface Props {
  content: string;
  title: string;
  onImprovedContent: (v: string) => void;
  onSummary: (v: string) => void;
  onTags: (tags: string[]) => void;
  onSeoTitle: (title: string, description: string) => void;
}

export default function AIToolsPanel({
  content,
  title,
  onImprovedContent,
  onSummary,
  onTags,
  onSeoTitle,
}: Props) {
  const [activeTool, setActiveTool] = useState<AITool>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Suggestions state
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [suggestionType, setSuggestionType] = useState<AITool>(null);

  async function runTool(tool: AITool) {
    if (!content.trim()) {
      setError("Add some content first.");
      return;
    }
    setActiveTool(tool);
    setLoading(true);
    setError("");
    setSuggestion(null);
    setSuggestionType(null);

    try {
      switch (tool) {
        case "improve": {
          const r = await aiApi.improve(content);
          setSuggestion(r.improved_content);
          setSuggestionType("improve");
          break;
        }
        case "summary": {
          const r = await aiApi.summary(content);
          setSuggestion(r.summary);
          setSuggestionType("summary");
          break;
        }
        case "tags": {
          const r = await aiApi.tags(content, title);
          setSuggestion(r.tags.join(", "));
          setSuggestionType("tags");
          break;
        }
        case "seo-title": {
          const r = await aiApi.seoTitle(content, title);
          setSuggestion(`${r.seo_title}\n\n${r.seo_description}`);
          setSuggestionType("seo-title");
          break;
        }
        case "tldr": {
          const r = await aiApi.tldr(content);
          setSuggestion(r.tldr);
          setSuggestionType("tldr");
          break;
        }
      }
    } catch (err: unknown) {
      const e = err as { detail?: string; status?: number };
      if (e?.status === 429) {
        setError("Rate limit reached. Try again in an hour.");
      } else {
        setError(e?.detail ?? "AI request failed.");
      }
    } finally {
      setLoading(false);
      setActiveTool(null);
    }
  }

  function handleAccept() {
    if (!suggestion) return;
    switch (suggestionType) {
      case "improve":
        onImprovedContent(suggestion);
        break;
      case "summary":
        onSummary(suggestion);
        break;
      case "tags":{
        const tags = suggestion
          .split(",")
          .map((t) => t.trim().toLowerCase())
          .filter(Boolean);
        onTags(tags);
        break;
      }
      case "seo-title": {
        const [t, ...rest] = suggestion.split("\n\n");
        onSeoTitle(t.trim(), rest.join("\n\n").trim());
        break;
      }
      case "tldr":
        onSummary(suggestion);
        break;
    }
    setSuggestion(null);
    setSuggestionType(null);
  }

  function handleReject() {
    setSuggestion(null);
    setSuggestionType(null);
  }

  const tools: { id: AITool; label: string; desc: string; emoji: string }[] = [
    { id: "improve", label: "Improve Writing", desc: "Rewrite for clarity & engagement", emoji: "✏️" },
    { id: "summary", label: "Generate Summary", desc: "Create a concise summary", emoji: "📝" },
    { id: "tags", label: "Suggest Tags", desc: "Get relevant tags", emoji: "🏷️" },
    { id: "seo-title", label: "SEO Title & Meta", desc: "Optimise for search engines", emoji: "🔍" },
    { id: "tldr", label: "TLDR", desc: "One-sentence summary", emoji: "⚡" },
  ];

  return (
    <div>
      <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
        AI Tools
      </h2>

      {error && (
        <p className="text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2 mb-3">
          {error}
        </p>
      )}

      <div className="space-y-2">
        {tools.map(({ id, label, desc, emoji }) => (
          <button
            key={id}
            type="button"
            onClick={() => runTool(id)}
            disabled={loading}
            className="w-full text-left p-3 rounded-xl border border-slate-200 hover:border-blue-300 hover:bg-blue-50 disabled:opacity-50 transition-all group"
          >
            <div className="flex items-center gap-2">
              <span className="text-base">{emoji}</span>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-700 group-hover:text-blue-700">
                  {loading && activeTool === id ? "Thinking…" : label}
                </p>
                <p className="text-xs text-slate-400 truncate">{desc}</p>
              </div>
              {loading && activeTool === id && (
                <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Suggestion panel */}
      {suggestion && suggestionType && (
        <div className="mt-4">
          <AISuggestion
            type={suggestionType as string}
            suggestion={suggestion}
            onAccept={handleAccept}
            onReject={handleReject}
          />
        </div>
      )}
    </div>
  );
}
