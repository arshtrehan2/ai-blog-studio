"use client";
import AIToolsPanel from "@/components/ai-tools/AIToolsPanel";

interface Props {
  content: string; title: string; tags: string[]; summary: string; seoTitle: string; seoDescription: string;
  onTagsChange: (tags: string[]) => void; onSummaryChange: (s: string) => void;
  onSeoTitleChange: (s: string) => void; onSeoDescriptionChange: (s: string) => void;
}

export default function EditorSidebar({ content, title, tags, summary, seoTitle, seoDescription, onTagsChange, onSummaryChange, onSeoTitleChange, onSeoDescriptionChange }: Props) {
  return (
    <div style={{ width: 320, borderLeft: "1px solid var(--color-border)", display: "flex", flexDirection: "column", overflow: "hidden", background: "var(--color-bg-secondary)" }}>
      <div style={{ flex: 1, overflowY: "auto", padding: 20 }}>
        <section style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: 13, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--color-text-muted)", marginBottom: 12 }}>Post Meta</h3>
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: "block", fontSize: 13, fontWeight: 500, marginBottom: 4 }}>Tags (comma-separated)</label>
            <input type="text" value={tags.join(", ")} onChange={e => onTagsChange(e.target.value.split(",").map(t => t.trim().toLowerCase()).filter(Boolean))}
              placeholder="python, fastapi, web"
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 13, background: "white" }} />
          </div>
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: "block", fontSize: 13, fontWeight: 500, marginBottom: 4 }}>Summary</label>
            <textarea value={summary} onChange={e => onSummaryChange(e.target.value)} placeholder="Brief summary..." rows={3}
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 13, resize: "vertical", background: "white" }} />
          </div>
          <div style={{ marginBottom: 8 }}>
            <label style={{ display: "block", fontSize: 13, fontWeight: 500, marginBottom: 4 }}>SEO Title</label>
            <input type="text" value={seoTitle} onChange={e => onSeoTitleChange(e.target.value)} placeholder="SEO title (max 60 chars)" maxLength={60}
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 13, background: "white" }} />
            <span style={{ fontSize: 11, color: "var(--color-text-muted)" }}>{seoTitle.length}/60 chars</span>
          </div>
          <div>
            <label style={{ display: "block", fontSize: 13, fontWeight: 500, marginBottom: 4 }}>SEO Description</label>
            <textarea value={seoDescription} onChange={e => onSeoDescriptionChange(e.target.value)} placeholder="Meta description (max 155 chars)" maxLength={155} rows={3}
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 13, resize: "vertical", background: "white" }} />
            <span style={{ fontSize: 11, color: "var(--color-text-muted)" }}>{seoDescription.length}/155 chars</span>
          </div>
        </section>
        <AIToolsPanel content={content} title={title} onSuggestTags={onTagsChange} onSuggestSummary={onSummaryChange}
          onSuggestSEO={(t, d) => { onSeoTitleChange(t); onSeoDescriptionChange(d); }} />
      </div>
    </div>
  );
}
