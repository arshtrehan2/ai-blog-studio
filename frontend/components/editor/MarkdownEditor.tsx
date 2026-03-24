"use client";
import { useState } from "react";
import ReactMarkdown from "react-markdown";

export default function MarkdownEditor({ content, onChange }: { content: string; onChange: (v: string) => void }) {
  const [activeTab, setActiveTab] = useState<"edit" | "preview">("edit");
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
      <div style={{ display: "flex", borderBottom: "1px solid var(--color-border)", padding: "0 24px", background: "var(--color-bg-secondary)" }}>
        {(["edit", "preview"] as const).map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            style={{ padding: "10px 16px", border: "none", borderBottom: activeTab === tab ? "2px solid var(--color-primary)" : "2px solid transparent", background: "transparent", fontSize: 14, fontWeight: activeTab === tab ? 600 : 400, color: activeTab === tab ? "var(--color-primary)" : "var(--color-text-muted)", cursor: "pointer", marginBottom: -1 }}>
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>
      {activeTab === "edit" ? (
        <textarea value={content} onChange={e => onChange(e.target.value)} placeholder="Start writing in Markdown..."
          style={{ flex: 1, padding: 24, border: "none", outline: "none", resize: "none", fontSize: 16, lineHeight: 1.8, fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", background: "white", overflowY: "auto" }} />
      ) : (
        <div style={{ flex: 1, padding: 24, overflowY: "auto", fontSize: 17, lineHeight: 1.8 }}>
          {content ? <ReactMarkdown>{content}</ReactMarkdown> : <p style={{ color: "var(--color-text-muted)", fontStyle: "italic" }}>Nothing to preview yet.</p>}
        </div>
      )}
    </div>
  );
}
