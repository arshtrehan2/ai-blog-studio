"use client";
import { useMemo } from "react";

interface Props {
  content: string;
}

export function WordCount({ content }: Props) {
  const stats = useMemo(() => {
    const words = content.trim() ? content.trim().split(/\s+/).length : 0;
    const chars = content.length;
    return { words, chars };
  }, [content]);

  return (
    <span className="text-xs text-slate-400">
      {stats.words} words &middot; {stats.chars} chars
    </span>
  );
}
