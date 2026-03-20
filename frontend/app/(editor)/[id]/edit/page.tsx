'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { postsAPI, Post } from '@/lib/api';
import { isAuthenticated } from '@/lib/auth';
import EditorPage from '@/components/editor/EditorPage';

export default function EditPostPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [post, setPost] = useState<Post | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      toast.error('Please sign in');
      router.replace('/login');
      return;
    }
    postsAPI
      .get(params.id)
      .then(setPost)
      .catch(() => {
        toast.error('Post not found');
        router.push('/');
      })
      .finally(() => setLoading(false));
  }, [params.id, router]);

  async function handleSave(data: {
    title: string;
    content: string;
    tags: string[];
    summary?: string;
    seo_title?: string;
    seo_description?: string;
    status: 'draft' | 'published';
  }) {
    await postsAPI.update(params.id, data);
    toast.success(
      data.status === 'published' ? 'Post published! 🎉' : 'Draft saved!',
    );
    router.push('/');
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
      </div>
    );
  }

  return <EditorPage initialPost={post ?? undefined} onSave={handleSave} />;
}
