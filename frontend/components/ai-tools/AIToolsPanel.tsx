"use client";

import { useState } from "react";
import { api } from "@/lib/api";

type AITool = "improve" | "summary" | "tags" | "seo-title" | "tldr" | null;
type AIState = "idle" | "loading" | "suggestion" | "accepted" | "error";

interface AIToolsPanelProps {
  content: string;
  title?: string;
  onAcceptImprove?: (improved: string) => void;
  onAcceptSummary?: (summary: string) => void;
  onAcceptTags?: (tags: string[]) => void;
  onAcceptSeo?: (seoTitle: string, seoDescription: string) => void;
  onAcceptTldr?: (tldr: string) => void;
}

interface Suggestion {
  tool: AITool;
  data: Record<string, unknown>;
}

export default function AIToolsPanel({
  content,
  title,
  onAcceptImprove,
  onAcceptSummary,
  onAcceptTags,
  onAcceptSeo,
  onAcceptTldr,
}: AIToolsPanelProps) {
  const [state, setState] = useState<AIState>("idle");
  const [activeTool, setActiveTool] = useState<AITool>(null);
  const [suggestion, setSuggestion] = useState<Suggestion | null>(null);
  const [error, setError] = useState<string>("");

  const runTool = async (tool: AITool) => {
    if (!content.trim()) {
      setError("Please add some content before using AI tools.");
      return;
    }
    setActiveTool(tool);
    setState("loading");
    setError("");
    setSuggestion(null);

    try {
      let data: Record<string, unknown> = {};
      switch (tool) {
        case "improve":
          data = await api.improveContent(content);
          break;
        case "summary":
          data = await api.summarizeContent(content);
          break;
        case "tags":
          data = await api.suggestTags(content, title);
          break;
        case "seo-title":
          data = await api.generateSeoTitle(content, title);
          break;
        case "tldr":
          data = await api.generateTldr(content);
          break;
      }
      setSuggestion({ tool, data });
      setState("suggestion");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "AI request failed";
      setError(message);
      setState("error");
    }
  };

  const accept = () => {
    if (!suggestion) return;
    const { tool, data } = suggestion;
    switch (tool) {
      case "improve":
        onAcceptImprove?.(data.improved_content as string);
        break;
      case "summary":
        onAcceptSummary?.(data.summary as string);
        break;
      case "tags":
        onAcceptTags?.(data.tags as string[]);
        break;
      case "seo-title":
        onAcceptSeo?.(data.seo_title as string, data.seo_description as string);
        break;
      case "tldr":
        onAcceptTldr?.(data.tldr as string);
        break;
    }
    setState("accepted");
  };

  const reject = () => {
    setSuggestion(null);
    setState("idle");
    setActiveTool(null);
  };

  const tools: Array<{ id: AITool; label: string; description: string }> = [
    { id: "improve", label: "✨ Improve", description: "Rewrite for clarity and quality" },
    { id: "summary", label: "📝 Summary", description: "Generate a short summary" },
    { id: "tags", label: "🏷️ Tags", description: "Suggest relevant tags" },
    { id: "seo-title", label: "🔍 SEO", description: "Generate SEO title & description" },
    { id: "tldr", label: "⚡ TLDR", description: "One-line summary" },
  ];

  return (
    <div className="ai-tools-panel">
      <h3>AI Tools</h3>
      <div className="ai-tool-buttons">
        {tools.map((tool) => (
          <button
            key={tool.id}
            onClick={() => runTool(tool.id)}
            disabled={state === "loading"}
            title={tool.description}
            className={`ai-tool-btn ${activeTool === tool.id ? "active" : ""}`}
          >
            {activeTool === tool.id && state === "loading" ? "..." : tool.label}
          </button>
        ))}
      </div>

      {state === "error" && (
        <div className="ai-error" role="alert">
          {error}
        </div>
      )}

      {state === "suggestion" && suggestion && (
        <div className="ai-suggestion">
          <h4>AI Suggestion</h4>
          {suggestion.tool === "improve" && (
            <div className="suggestion-content">
              <pre>{suggestion.data.improved_content as string}</pre>
            </div>
          )}
          {suggestion.tool === "summary" && (
            <div className="suggestion-content">
              <p>{suggestion.data.summary as string}</p>
            </div>
          )}
          {suggestion.tool === "tags" && (
            <div className="suggestion-content">
              <div className="tag-list">
                {(suggestion.data.tags as string[]).map((tag) => (
                  <span key={tag} className="tag">{tag}</span>
                ))}
              </div>
            </div>
          )}
          {suggestion.tool === "seo-title" && (
            <div className="suggestion-content">
              <strong>{suggestion.data.seo_title as string}</strong>
              <p>{suggestion.data.seo_description as string}</p>
            </div>
          )}
          {suggestion.tool === "tldr" && (
            <div className="suggestion-content">
              <p>{suggestion.data.tldr as string}</p>
            </div>
          )}
          <div className="ai-suggestion-actions">
            <button onClick={accept} className="btn-accept">✅ Accept</button>
            <button onClick={reject} className="btn-reject">❌ Reject</button>
          </div>
        </div>
      )}

      {state === "accepted" && (
        <div className="ai-accepted" role="status">
          ✅ Changes applied
          <button onClick={() => setState("idle")} className="btn-dismiss">Dismiss</button>
        </div>
      )}
    </div>
  );
}
