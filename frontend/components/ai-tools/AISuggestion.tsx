"use client";
interface Props { label: string; original: string | null; suggestion: string; onAccept: () => void; onReject: () => void; }
export default function AISuggestion({ label, suggestion, onAccept, onReject }: Props) {
  return (
    <div style={{ marginTop: 12, border: "1px solid var(--color-border)", borderRadius: 8, overflow: "hidden", fontSize: 13 }}>
      <div style={{ padding: "8px 12px", background: "var(--color-bg-secondary)", borderBottom: "1px solid var(--color-border)", fontWeight: 600, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span>{label}</span>
        <span style={{ fontSize: 11, background: "#dbeafe", color: "#1d4ed8", padding: "2px 6px", borderRadius: 12, fontWeight: 500 }}>AI Suggestion</span>
      </div>
      <div style={{ padding: 12, background: "white", maxHeight: 200, overflowY: "auto", lineHeight: 1.6, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>{suggestion}</div>
      <div style={{ padding: "8px 12px", borderTop: "1px solid var(--color-border)", display: "flex", gap: 8, background: "var(--color-bg-secondary)" }}>
        <button onClick={onAccept} style={{ flex: 1, padding: "6px 12px", background: "var(--color-primary)", color: "white", border: "none", borderRadius: 5, fontSize: 12, fontWeight: 600, cursor: "pointer" }}>Accept</button>
        <button onClick={onReject} style={{ flex: 1, padding: "6px 12px", background: "white", color: "var(--color-text-muted)", border: "1px solid var(--color-border)", borderRadius: 5, fontSize: 12, cursor: "pointer" }}>Reject</button>
      </div>
    </div>
  );
}
