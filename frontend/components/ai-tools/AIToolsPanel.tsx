"use client";
import { useState } from "react";
import { aiAPI } from "@/lib/api";
import { getToken } from "@/lib/auth";
import AISuggestion from "./AISuggestion";

type ToolName = "improve" | "summary" | "tags" | "seo-title" | "tldr";
type ToolState = "idle" | "loading" | "suggestion" | "error";

interface Props {
  content: string; title: string;
  onSuggestTags: (tags: string[]) => void;
  onSuggestSummary: (summary: string) => void;
  onSuggestSEO: (seoTitle: string, seoDesc: string) => void;
}

export default function AIToolsPanel({ content, title, onSuggestTags, onSuggestSummary, onSuggestSEO }: Props) {
  const [toolState, setToolState] = useState<ToolState>("idle");
  const [activeTool, setActiveTool] = useState<ToolName | null>(null);
  const [suggestion, setSuggestion] = useState<{ label: string; text: string; onAccept: () => void } | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function runTool(tool: ToolName) {
    const token = getToken();
    if (!token) { setError("Please sign in to use AI tools."); return; }
    if (!content.trim()) { setError("Please add some content first."); return; }
    setActiveTool(tool); setToolState("loading"); setError(null); setSuggestion(null);
    try {
      switch (tool) {
        case "improve": {
          const r = await aiAPI.improve({ content }, token);
          setSuggestion({ label: "Improved Content", text: r.improved_content, onAccept: () => { setToolState("idle"); setSuggestion(null); } });
          setToolState("suggestion"); break;
        }
        case "summary": {
          const r = await aiAPI.summary({ content }, token);
          setSuggestion({ label: "Suggested Summary", text: r.summary, onAccept: () => { onSuggestSummary(r.summary); setToolState("idle"); setSuggestion(null); } });
          setToolState("suggestion"); break;
        }
        case "tags": {
          const r = await aiAPI.tags({ content, title }, token);
          setSuggestion({ label: "Suggested Tags", text: r.tags.join(", "), onAccept: () => { onSuggestTags(r.tags); setToolState("idle"); setSuggestion(null); } });
          setToolState("suggestion"); break;
        }
        case "seo-title": {
          const r = await aiAPI.seoTitle({ content, title }, token);
          onSuggestSEO(r.seo_title, r.seo_description);
          setSuggestion({ label: "SEO fields updated!", text: `Title: ${r.seo_title}\nDescription: ${r.seo_description}`, onAccept: () => { setToolState("idle"); setSuggestion(null); } });
          setToolState("suggestion"); break;
        }
        case "tldr": {
          const r = await aiAPI.tldr({ content }, token);
          setSuggestion({ label: "TLDR", text: r.tldr, onAccept: () => { onSuggestSummary(r.tldr); setToolState("idle"); setSuggestion(null); } });
          setToolState("suggestion"); break;
        }
      }
    } catch (err: unknown) {
      const status = (err as { status?: number })?.status;
      setError(status === 429 ? "Rate limit reached. Please wait." : "AI tool failed. Please try again.");
      setToolState("error");
    }
  }

  const tools: { name: ToolName; label: string; description: string }[] = [
    { name: "improve", label: "Improve Writing", description: "Rewrite for clarity & quality" },
    { name: "summary", label: "Generate Summary", description: "Auto-summarize the post" },
    { name: "tags", label: "Suggest Tags", description: "Auto-generate relevant tags" },
    { name: "seo-title", label: "SEO Title + Meta", description: "Optimize for search engines" },
    { name: "tldr", label: "Generate TLDR", description: "One-line summary" },
  ];

  return (
    <section>
      <h3 style={{ fontSize: 13, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--color-text-muted)", marginBottom: 12 }}>AI Tools</h3>
      {error && <div role="alert" style={{ padding: "8px 12px", background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 6, color: "var(--color-error)", fontSize: 13, marginBottom: 12 }}>{error}</div>}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {tools.map(({ name, label, description }) => (
          <button key={name} onClick={() => runTool(name)} disabled={toolState === "loading"}
            style={{ padding: "10px 12px", background: activeTool === name && toolState === "loading" ? "#dbeafe" : "white", border: "1px solid var(--color-border)", borderRadius: 6, textAlign: "left", cursor: toolState === "loading" ? "not-allowed" : "pointer", opacity: toolState === "loading" && activeTool !== name ? 0.6 : 1 }}>
            <div style={{ fontSize: 13, fontWeight: 600 }}>{activeTool === name && toolState === "loading" ? "Running..." : label}</div>
            <div style={{ fontSize: 12, color: "var(--color-text-muted)", marginTop: 2 }}>{description}</div>
          </button>
        ))}
      </div>
      {toolState === "suggestion" && suggestion && (
        <AISuggestion label={suggestion.label} original={null} suggestion={suggestion.text}
          onAccept={suggestion.onAccept} onReject={() => { setToolState("idle"); setSuggestion(null); }} />
      )}
    </section>
  );
}
