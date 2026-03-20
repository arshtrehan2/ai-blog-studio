'use client';

import { useState } from 'react';
import Link from 'next/link';
import MarkdownEditor from './MarkdownEditor';
import PostMeta from './PostMeta';
import PublishControls from './PublishControls';
import AIToolsPanel from '../ai-tools/AIToolsPanel';
import { Post } from '@/lib/api';

interface SaveData {
  title: string;
  content: string;
  tags: string[];
  summary?: string;
  seo_title?: string;
  seo_description?: string;
  status: 'draft' | 'published';
}

interface Props {
  initialPost?: Post;
  onSave: (data: SaveData) => Promise<void>;
}

export default function EditorPage({ initialPost, onSave }: Props) {
  const [title, setTitle] = useState(initialPost?.title ?? '');
  const [content, setContent] = useState(initialPost?.content ?? '');
  const [tags, setTags] = useState<string[]>(initialPost?.tags ?? []);
  const [summary, setSummary] = useState(initialPost?.summary ?? '');
  const [seoTitle, setSeoTitle] = useState(initialPost?.seo_title ?? '');
  const [seoDescription, setSeoDescription] = useState(
    initialPost?.seo_description ?? '',
  );
  const [saving, setSaving] = useState(false);

  async function save(status: 'draft' | 'published') {
    if (!title.trim()) {
      alert('Please add a title before saving.');
      return;
    }
    setSaving(true);
    try {
      await onSave({
        title,
        content,
        tags,
        summary: summary || undefined,
        seo_title: seoTitle || undefined,
        seo_description: seoDescription || undefined,
        status,
      });
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Topbar */}
      <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between sticky top-0 z-10">
        <Link href="/" className="text-sm text-gray-500 hover:text-gray-900">
          ← Back
        </Link>
        <h1 className="text-sm font-semibold text-gray-700">
          {initialPost ? 'Edit Post' : 'New Post'}
        </h1>
        <div className="w-20" />
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6">
        {/* Left — Title + Editor */}
        <div className="flex flex-col gap-4">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Post title…"
            className="w-full text-3xl font-bold text-gray-900 border-none outline-none bg-transparent placeholder-gray-300"
          />
          <MarkdownEditor value={content} onChange={setContent} />
        </div>

        {/* Right — Sidebar */}
        <aside className="space-y-6">
          {/* Publish controls */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <PublishControls
              isSaving={saving}
              onSaveDraft={() => save('draft')}
              onPublish={() => save('published')}
            />
          </div>

          {/* Post meta */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-4">
              Post Settings
            </p>
            <PostMeta
              tags={tags}
              onTagsChange={setTags}
              summary={summary}
              onSummaryChange={setSummary}
              seoTitle={seoTitle}
              onSeoTitleChange={setSeoTitle}
              seoDescription={seoDescription}
              onSeoDescriptionChange={setSeoDescription}
            />
          </div>

          {/* AI tools */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <AIToolsPanel
              title={title}
              content={content}
              onContentChange={setContent}
              onSummaryChange={setSummary}
              onTagsChange={setTags}
              onSeoTitleChange={setSeoTitle}
              onSeoDescriptionChange={setSeoDescription}
            />
          </div>
        </aside>
      </div>
    </div>
  );
}
