"use client";
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";
import { AIToolsPanel } from "@/components/ai-tools/AIToolsPanel";
import { WordCount } from "@/components/editor/WordCount";
import type { Post } from "@/lib/types";

const MarkdownEditor = dynamic(() => import("@/components/editor/MarkdownEditor"), {
  ssr: false,
});

interface Props {
  postId?: string;
}

export default function EditorPage({ postId }: Props) {
  const router = useRouter();
  const isEditing = Boolean(postId);

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState("");
  const [summary, setSummary] = useState("");
  const [seoTitle, setSeoTitle] = useState("");
  const [seoDescription, setSeoDescription] = useState("");
  const [status, setStatus] = useState<"draft" | "published">("draft");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (postId) {
      api.get<Post>(`/posts/${postId}/detail`).then((p) => {
        setTitle(p.title);
        setContent(p.content);
        setTags(p.tags);
        setSummary(p.summary ?? "");
        setSeoTitle(p.seo_title ?? "");
        setSeoDescription(p.seo_description ?? "");
        setStatus(p.status);
      });
    }
  }, [postId]);

  const handleSave = useCallback(
    async (publish = false) => {
      setSaving(true);
      setError(null);
      try {
        const payload = {
          title,
          content,
          tags,
          summary: summary || undefined,
          seo_title: seoTitle || undefined,
          seo_description: seoDescription || undefined,
          status: publish ? "published" : status,
        };
        if (isEditing && postId) {
          await api.put(`/posts/${postId}`, payload);
          if (publish && status !== "published") {
            await api.patch(`/posts/${postId}/publish`);
          }
        } else {
          const created = await api.post<Post>("/posts", payload);
          if (publish) {
            await api.patch(`/posts/${created.id}/publish`);
          }
          router.push(`/${created.id}/edit`);
        }
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Save failed");
      } finally {
        setSaving(false);
      }
    },
    [title, content, tags, summary, seoTitle, seoDescription, status, isEditing, postId, router]
  );

  const addTag = () => {
    const t = tagInput.trim().toLowerCase();
    if (t && !tags.includes(t)) setTags([...tags, t]);
    setTagInput("");
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Main editor area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Title bar */}
        <div className="bg-white border-b border-slate-200 px-6 py-4">
          <input
            type="text"
            placeholder="Post title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full text-2xl font-bold text-slate-900 placeholder-slate-300 outline-none"
          />
        </div>

        {/* Markdown editor */}
        <div className="flex-1 overflow-auto">
          <MarkdownEditor value={content} onChange={setContent} />
        </div>

        {/* Footer */}
        <div className="bg-white border-t border-slate-200 px-6 py-3 flex items-center justify-between">
          <WordCount content={content} />
          {error && <span className="text-red-500 text-sm">{error}</span>}
          <div className="flex gap-3">
            <button
              onClick={() => handleSave(false)}
              disabled={saving}
              className="px-4 py-2 text-sm rounded-lg border border-slate-300 hover:bg-slate-50 disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save Draft"}
            </button>
            <button
              onClick={() => handleSave(true)}
              disabled={saving || !title}
              className="px-4 py-2 text-sm rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              Publish
            </button>
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <aside className="w-80 bg-white border-l border-slate-200 overflow-y-auto flex flex-col">
        {/* Meta */}
        <div className="p-4 border-b border-slate-100">
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Post Settings</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-xs text-slate-600 mb-1">Tags</label>
              <div className="flex gap-1 flex-wrap mb-1">
                {tags.map((t) => (
                  <span
                    key={t}
                    className="inline-flex items-center gap-1 bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5 rounded-full"
                  >
                    {t}
                    <button onClick={() => setTags(tags.filter((x) => x !== t))}>×</button>
                  </span>
                ))}
              </div>
              <div className="flex gap-1">
                <input
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addTag())}
                  placeholder="Add tag..."
                  className="flex-1 text-xs border border-slate-300 rounded px-2 py-1 outline-none focus:ring-1 focus:ring-indigo-400"
                />
                <button
                  onClick={addTag}
                  className="text-xs px-2 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                >
                  Add
                </button>
              </div>
            </div>
            <div>
              <label className="block text-xs text-slate-600 mb-1">Summary</label>
              <textarea
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                rows={3}
                className="w-full text-xs border border-slate-300 rounded px-2 py-1 outline-none focus:ring-1 focus:ring-indigo-400 resize-none"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-600 mb-1">SEO Title</label>
              <input
                value={seoTitle}
                onChange={(e) => setSeoTitle(e.target.value)}
                className="w-full text-xs border border-slate-300 rounded px-2 py-1 outline-none focus:ring-1 focus:ring-indigo-400"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-600 mb-1">SEO Description</label>
              <textarea
                value={seoDescription}
                onChange={(e) => setSeoDescription(e.target.value)}
                rows={3}
                className="w-full text-xs border border-slate-300 rounded px-2 py-1 outline-none focus:ring-1 focus:ring-indigo-400 resize-none"
              />
            </div>
          </div>
        </div>

        {/* AI Tools */}
        <AIToolsPanel
          content={content}
          title={title}
          onImprove={setContent}
          onSummary={setSummary}
          onTags={setTags}
          onSeoTitle={(t, d) => { setSeoTitle(t); setSeoDescription(d); }}
          onTldr={setSummary}
        />
      </aside>
    </div>
  );
}
