"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import dynamic from "next/dynamic";
import EditorSidebar from "@/components/editor/EditorSidebar";
import WordCount from "@/components/editor/WordCount";
import { postsApi, type Post } from "@/lib/api";
import Link from "next/link";

const MarkdownEditor = dynamic(
  () => import("@/components/editor/MarkdownEditor"),
  { ssr: false }
);

export default function EditPostPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const postId = params.id;

  const [post, setPost] = useState<Post | null>(null);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [summary, setSummary] = useState("");
  const [seoTitle, setSeoTitle] = useState("");
  const [seoDescription, setSeoDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    postsApi
      .get(postId)
      .then((p) => {
        setPost(p);
        setTitle(p.title);
        setContent(p.content);
        setTags(p.tags);
        setSummary(p.summary ?? "");
        setSeoTitle(p.seo_title ?? "");
        setSeoDescription(p.seo_description ?? "");
      })
      .catch(() => router.push("/"))
      .finally(() => setLoading(false));
  }, [postId, router]);

  async function handleSave() {
    setSaving(true);
    setError("");
    try {
      await postsApi.update(postId, {
        title,
        content,
        tags,
        summary,
        seo_title: seoTitle,
        seo_description: seoDescription,
      });
    } catch (err: unknown) {
      const e = err as { detail?: string };
      setError(e?.detail ?? "Failed to save.");
    } finally {
      setSaving(false);
    }
  }

  async function handlePublish() {
    setSaving(true);
    setError("");
    try {
      await handleSave();
      const result = await postsApi.publish(postId);
      router.push(`/${result.slug}`);
    } catch (err: unknown) {
      const e = err as { detail?: string };
      setError(e?.detail ?? "Failed to publish.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-slate-400">Loading…</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-20 bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
        <Link href="/" className="text-sm text-slate-500 hover:text-slate-700">
          ← Blog
        </Link>
        <div className="flex items-center gap-2">
          <span
            className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              post?.status === "published"
                ? "bg-green-100 text-green-700"
                : "bg-amber-100 text-amber-700"
            }`}
          >
            {post?.status ?? "draft"}
          </span>
        </div>
        <div className="flex gap-2">
          {error && (
            <span className="text-xs text-red-600 self-center">{error}</span>
          )}
          <button
            onClick={handleSave}
            disabled={saving}
            className="text-sm px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50 disabled:opacity-50 transition-colors"
          >
            {saving ? "Saving…" : "Save"}
          </button>
          {post?.status !== "published" && (
            <button
              onClick={handlePublish}
              disabled={saving}
              className="text-sm px-3 py-1.5 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              Publish
            </button>
          )}
        </div>
      </header>

      <div className="flex h-[calc(100vh-57px)]">
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
          <div className="px-8 pb-4">
            <WordCount content={content} />
          </div>
        </div>

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
