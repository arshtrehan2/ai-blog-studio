import { Metadata } from "next";
import Link from "next/link";
import { serverFetch } from "@/lib/api";
import type { PaginatedPosts } from "@/lib/types";

export const metadata: Metadata = {
  title: "Blog Feed",
  description: "Read the latest posts from AI Blog Studio.",
};

export const revalidate = 60; // ISR: revalidate every 60s

export default async function BlogFeedPage({
  searchParams,
}: {
  searchParams: { page?: string; tag?: string };
}) {
  const page = Number(searchParams.page ?? 1);
  const tag = searchParams.tag ?? "";

  const params = new URLSearchParams({
    page: String(page),
    page_size: "20",
    ...(tag ? { tag } : {}),
  });

  const data = await serverFetch<PaginatedPosts>(`/posts?${params}`);

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <header className="mb-10">
        <h1 className="text-4xl font-bold text-slate-900">AI Blog Studio</h1>
        <p className="mt-2 text-slate-500">Beautifully written, AI-enhanced posts.</p>
      </header>

      {data.items.length === 0 ? (
        <p className="text-slate-400">No posts yet. Be the first to publish!</p>
      ) : (
        <ul className="space-y-8">
          {data.items.map((post) => (
            <li key={post.id} className="border-b border-slate-100 pb-8">
              <Link href={`/blog/${post.slug}`} className="group">
                <h2 className="text-xl font-semibold text-slate-800 group-hover:text-indigo-600 transition">
                  {post.title}
                </h2>
              </Link>
              {post.summary && (
                <p className="mt-2 text-slate-600 text-sm leading-relaxed">{post.summary}</p>
              )}
              <div className="mt-3 flex items-center gap-3 text-xs text-slate-400">
                <span>{post.author?.display_name}</span>
                <span>&middot;</span>
                <span>{new Date(post.published_at ?? post.created_at).toLocaleDateString()}</span>
                {post.tags.map((t) => (
                  <Link
                    key={t}
                    href={`/?tag=${t}`}
                    className="bg-slate-100 hover:bg-indigo-100 text-slate-600 hover:text-indigo-700 px-2 py-0.5 rounded-full transition"
                  >
                    {t}
                  </Link>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* Pagination */}
      {data.total_pages > 1 && (
        <nav className="mt-10 flex justify-center gap-4">
          {page > 1 && (
            <Link
              href={`/?page=${page - 1}${tag ? `&tag=${tag}` : ""}`}
              className="px-4 py-2 rounded bg-slate-200 hover:bg-slate-300 text-sm"
            >
              Previous
            </Link>
          )}
          <span className="px-4 py-2 text-sm text-slate-500">
            Page {page} of {data.total_pages}
          </span>
          {page < data.total_pages && (
            <Link
              href={`/?page=${page + 1}${tag ? `&tag=${tag}` : ""}`}
              className="px-4 py-2 rounded bg-indigo-600 hover:bg-indigo-700 text-white text-sm"
            >
              Next
            </Link>
          )}
        </nav>
      )}
    </div>
  );
}
