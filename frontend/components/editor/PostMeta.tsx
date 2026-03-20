'use client';

interface Props {
  tags: string[];
  onTagsChange: (tags: string[]) => void;
  summary: string;
  onSummaryChange: (v: string) => void;
  seoTitle: string;
  onSeoTitleChange: (v: string) => void;
  seoDescription: string;
  onSeoDescriptionChange: (v: string) => void;
}

export default function PostMeta({
  tags,
  onTagsChange,
  summary,
  onSummaryChange,
  seoTitle,
  onSeoTitleChange,
  seoDescription,
  onSeoDescriptionChange,
}: Props) {
  function handleTagInput(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const val = (e.target as HTMLInputElement).value.trim().toLowerCase();
      if (val && !tags.includes(val)) {
        onTagsChange([...tags, val]);
      }
      (e.target as HTMLInputElement).value = '';
    }
  }

  return (
    <div className="space-y-4">
      {/* Tags */}
      <div>
        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
          Tags
        </label>
        <div className="flex flex-wrap gap-1.5 mb-2">
          {tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-1 bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded-full"
            >
              #{tag}
              <button
                onClick={() => onTagsChange(tags.filter((t) => t !== tag))}
                className="hover:text-red-500 font-bold"
              >
                ×
              </button>
            </span>
          ))}
        </div>
        <input
          type="text"
          onKeyDown={handleTagInput}
          placeholder="Type a tag and press Enter"
          className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Summary */}
      <div>
        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
          Summary
        </label>
        <textarea
          value={summary}
          onChange={(e) => onSummaryChange(e.target.value)}
          rows={3}
          placeholder="A brief description of your post…"
          className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* SEO Title */}
      <div>
        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
          SEO Title
          <span className="normal-case font-normal text-gray-400 ml-1">(max 60 chars)</span>
        </label>
        <input
          type="text"
          value={seoTitle}
          maxLength={60}
          onChange={(e) => onSeoTitleChange(e.target.value)}
          placeholder="SEO-optimised title"
          className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p className="text-right text-xs text-gray-400 mt-0.5">
          {seoTitle.length}/60
        </p>
      </div>

      {/* SEO Description */}
      <div>
        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
          Meta Description
          <span className="normal-case font-normal text-gray-400 ml-1">(max 155 chars)</span>
        </label>
        <textarea
          value={seoDescription}
          maxLength={155}
          onChange={(e) => onSeoDescriptionChange(e.target.value)}
          rows={3}
          placeholder="Appears in search engine results…"
          className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p className="text-right text-xs text-gray-400 mt-0.5">
          {seoDescription.length}/155
        </p>
      </div>
    </div>
  );
}
