"use client";

import { useState } from "react";
import AIToolsPanel from "@/components/ai-tools/AIToolsPanel";

interface Props {
  content: string;
  title: string;
  tags: string[];
  summary: string;
  seoTitle: string;
  seoDescription: string;
  onTagsChange: (tags: string[]) => void;
  onSummaryChange: (v: string) => void;
  onSeoTitleChange: (v: string) => void;
  onSeoDescriptionChange: (v: string) => void;
  onContentChange: (v: string) => void;
}

export default function EditorSidebar({
  content,
  title,
  tags,
  summary,
  seoTitle,
  seoDescription,
  onTagsChange,
  onSummaryChange,
  onSeoTitleChange,
  onSeoDescriptionChange,
  onContentChange,
}: Props) {
  const [tagInput, setTagInput] = useState("");

  function addTag(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      const t = tagInput.trim().toLowerCase().replace(/\s+/g, "-");
      if (t && !tags.includes(t)) {
        onTagsChange([...tags, t]);
      }
      setTagInput("");
    }
  }

  function removeTag(tag: string) {
    onTagsChange(tags.filter((t) => t !== tag));
  }

  return (
    <aside className="w-80 border-l border-slate-200 bg-white flex flex-col overflow-y-auto">
      {/* Post Metadata */}
      <div className="p-4 border-b border-slate-100">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
          Post Meta
        </h2>

        {/* Tags */}
        <div className="mb-4">
          <label className="block text-xs font-medium text-slate-700 mb-1">
            Tags
          </label>
          <div className="flex flex-wrap gap-1 mb-1">
            {tags.map((t) => (
              <span
                key={t}
                className="inline-flex items-center gap-1 bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded-full"
              >
                {t}
                <button
                  type="button"
                  onClick={() => removeTag(t)}
                  className="text-blue-400 hover:text-blue-700 text-xs leading-none"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={addTag}
            placeholder="Add tag, press Enter"
            className="w-full text-xs border border-slate-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        {/* Summary */}
        <div className="mb-4">
          <label className="block text-xs font-medium text-slate-700 mb-1">
            Summary
          </label>
          <textarea
            value={summary}
            onChange={(e) => onSummaryChange(e.target.value)}
            placeholder="Brief post summary…"
            rows={3}
            className="w-full text-xs border border-slate-200 rounded-lg px-2 py-1.5 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        {/* SEO */}
        <div className="mb-2">
          <label className="block text-xs font-medium text-slate-700 mb-1">
            SEO Title{" "}
            <span className="text-slate-400">(max 60 chars)</span>
          </label>
          <input
            type="text"
            value={seoTitle}
            onChange={(e) => onSeoTitleChange(e.target.value)}
            maxLength={60}
            placeholder="SEO-optimized title"
            className="w-full text-xs border border-slate-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <p className="text-right text-xs text-slate-400 mt-0.5">
            {seoTitle.length}/60
          </p>
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">
            Meta Description{" "}
            <span className="text-slate-400">(max 155 chars)</span>
          </label>
          <textarea
            value={seoDescription}
            onChange={(e) => onSeoDescriptionChange(e.target.value)}
            maxLength={155}
            placeholder="Meta description for search engines"
            rows={2}
            className="w-full text-xs border border-slate-200 rounded-lg px-2 py-1.5 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <p className="text-right text-xs text-slate-400 mt-0.5">
            {seoDescription.length}/155
          </p>
        </div>
      </div>

      {/* AI Tools */}
      <div className="p-4 flex-1">
        <AIToolsPanel
          content={content}
          title={title}
          onImprovedContent={onContentChange}
          onSummary={onSummaryChange}
          onTags={(newTags) => onTagsChange(newTags)}
          onSeoTitle={(t, d) => {
            onSeoTitleChange(t);
            onSeoDescriptionChange(d);
          }}
        />
      </div>
    </aside>
  );
}
