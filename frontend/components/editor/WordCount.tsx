"use client";
export default function WordCount({ content }: { content: string }) {
  const words = content.trim() ? content.trim().split(/\s+/).length : 0;
  return (
    <span style={{ fontSize: 13, color: "var(--color-text-muted)", whiteSpace: "nowrap" }}>
      {words} words · {content.length} chars
    </span>
  );
}
