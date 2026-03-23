"use client";

interface Props {
  content: string;
}

export default function WordCount({ content }: Props) {
  const words = content.trim() ? content.trim().split(/\s+/).length : 0;
  const chars = content.length;
  const readingTime = Math.max(1, Math.ceil(words / 200));

  return (
    <div className="flex gap-4 text-xs text-slate-400">
      <span>
        <strong className="text-slate-600">{words.toLocaleString()}</strong> words
      </span>
      <span>
        <strong className="text-slate-600">{chars.toLocaleString()}</strong> characters
      </span>
      <span>
        <strong className="text-slate-600">{readingTime}</strong> min read
      </span>
    </div>
  );
}
