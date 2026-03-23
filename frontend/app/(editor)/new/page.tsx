"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import EditorSidebar from "@/components/editor/EditorSidebar";
import WordCount from "@/components/editor/WordCount";
import { postsApi } from "@/lib/api";
import Link from "next/link";

const MarkdownEditor = dynamic(
  () => import("@/components/editor/MarkdownEditor"),
  { ssr: false }
);

export default function NewPostPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [summary, setSummary] = useState("");
  const [seoTitle, setSeoTitle] = useState("");
  const [seoDescription, setSeoDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function handleSaveDraft() {
    if (!title.trim() || !content.trim()) {
      setError("Title and content are required.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const post = await postsApi.create({
        title,
        content,
        tags,
        summary,
        seo_title: seoTitle,
        seo_description: seoDescription,
        status: "draft",
      });
      router.push(`/${post.id}/edit`);
    } catch (err: unknown) {
      const e = err as { detail?: string };
      setError(e?.detail ?? "Failed to save draft.");
    } finally {
      setSaving(false);
    }
  }

  async function handlePublish() {
    if (!title.trim() || !content.trim()) {
      setError("Title and content are required.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const post = await postsApi.create({
        title,
        content,
        tags,
        summary,
        seo_title: seoTitle,
        seo_description: seoDescription,
        status: "draft",
      });
      const published = await postsApi.publish(post.id);
      router.push(`/${published.slug}`);
    } catch (err: unknown) {
      const e = err as { detail?: string };
      setError(e?.detail ?? "Failed to publish.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top bar */}
      <header className="sticky top-0 z-20 bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
        <Link href="/" className="text-sm text-slate-500 hover:text-slate-700">
          ← Blog
        </Link>
        <h1 className="font-semibold text-slate-800">New Post</h1>
        <div className="flex gap-2 items-center">
          {error && <span className="text-xs text-red-600">{error}</span>}
          <button
            onClick={handleSaveDraft}
            disabled={saving}
            className="text-sm px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50 disabled:opacity-50 transition-colors"
          >
            Save Draft
          </button>
          <button
            onClick={handlePublish}
            disabled={saving}
            className="text-sm px-3 py-1.5 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            Publish
          </button>
        </div>
      </header>

      <div className="flex h-[calc(100vh-57px)]">
        {/* Main editor area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <input
            type="text"
            placeholder="Post title…"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full text-2xl font-bold px-8 pt-8 pb-4 bg-transparent border-none outline-none placeholder-slate-300"
          />
          <div className="flex-1 px-8 overflow-auto">
            <MarkdownEditor value={content} onChange={setContent} />
          </div>
          <div className="px-8 pb-4 border-t border-slate-100 pt-2">
            <WordCount content={content} />
          </div>
        </div>

        {/* Sidebar */}
        <EditorSidebar
          content={content}
          title={title}
          tags={tags}
          summary={summary}
          seoTitle={seoTitle}
          seoDescription={seoDescription}
          onTagsChange={setTags}
          onSummaryChange={setSummary}
          onSeoTitleChange={setSeoTitle}
          onSeoDescriptionChange={setSeoDescription}
          onContentChange={setContent}
        />
      </div>
    </div>
  );
}
