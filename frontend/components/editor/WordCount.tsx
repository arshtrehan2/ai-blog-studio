interface Props {
  content: string;
}

export default function WordCount({ content }: Props) {
  const words = content.trim() ? content.trim().split(/\s+/).length : 0;
  const chars = content.length;
  const readingTime = Math.max(1, Math.round(words / 200));

  return (
    <div className="flex items-center gap-4 text-xs text-gray-400 px-4 py-2 border-t border-gray-100">
      <span>{words.toLocaleString()} words</span>
      <span>{chars.toLocaleString()} chars</span>
      <span>{readingTime} min read</span>
    </div>
  );
}
