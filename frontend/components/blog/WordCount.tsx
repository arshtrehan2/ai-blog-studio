"use client";

interface WordCountProps {
  content: string;
}

export default function WordCount({ content }: WordCountProps) {
  const words = content.trim() ? content.trim().split(/\s+/).length : 0;
  const chars = content.length;
  const readingTime = Math.max(1, Math.ceil(words / 200));

  return (
    <div className="word-count" aria-live="polite">
      <span>{words} words</span>
      <span>{chars} chars</span>
      <span>{readingTime} min read</span>
    </div>
  );
}
