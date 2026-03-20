import { Metadata } from 'next';
import Link from 'next/link';
import { PostListResponse } from '@/lib/api';
import BlogCard from '@/components/blog/BlogCard';

export const metadata: Metadata = {
  title: 'Blog | AI Blog Studio',
  description: 'Read the latest articles from AI Blog Studio authors.',
};

async function getPosts(page = 1): Promise<PostListResponse> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
  const res = await fetch(
    `${apiUrl}/posts?page=${page}&page_size=20`,
    { next: { revalidate: 60 } },
  );
  if (!res.ok) return { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 };
  return res.json();
}

export default async function BlogFeedPage({
  searchParams,
}: {
  searchParams: { page?: string };
}) {
  const page = Number(searchParams?.page ?? 1);
  const data = await getPosts(page);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Nav */}
      <nav className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-gray-900">
          ✨ AI Blog Studio
        </Link>
        <div className="flex gap-4">
          <Link
            href="/login"
            className="text-sm text-gray-600 hover:text-gray-900 font-medium"
          >
            Sign in
          </Link>
          <Link
            href="/new"
            className="text-sm bg-blue-600 text-white px-4 py-1.5 rounded-lg hover:bg-blue-700 font-medium"
          >
            Write
          </Link>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Latest Posts</h1>
        <p className="text-gray-500 mb-10">
          {data.total} article{data.total !== 1 ? 's' : ''} published
        </p>

        {data.items.length === 0 ? (
          <div className="text-center py-20 text-gray-400">
            <p className="text-5xl mb-4">📝</p>
            <p className="text-lg">No posts yet. Be the first to write!</p>
            <Link
              href="/new"
              className="mt-4 inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Write a post
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            {data.items.map((post) => (
              <BlogCard key={post.id} post={post} />
            ))}
          </div>
        )}

        {/* Pagination */}
        {data.total_pages > 1 && (
          <div className="mt-12 flex justify-center gap-2">
            {Array.from({ length: data.total_pages }, (_, i) => i + 1).map((p) => (
              <Link
                key={p}
                href={`/?page=${p}`}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  p === page
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                {p}
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
