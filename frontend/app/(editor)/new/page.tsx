'use client';

import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { postsAPI } from '@/lib/api';
import { isAuthenticated } from '@/lib/auth';
import { useEffect } from 'react';
import EditorPage from '@/components/editor/EditorPage';

export default function NewPostPage() {
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      toast.error('Please sign in to write a post');
      router.replace('/login');
    }
  }, [router]);

  async function handleSave(data: {
    title: string;
    content: string;
    tags: string[];
    summary?: string;
    seo_title?: string;
    seo_description?: string;
    status: 'draft' | 'published';
  }) {
    const post = await postsAPI.create(data);
    toast.success(
      data.status === 'published' ? 'Post published! 🎉' : 'Draft saved!',
    );
    router.push(data.status === 'published' ? `/blog/${post.slug}` : `/`);
  }

  return <EditorPage onSave={handleSave} />;
}
