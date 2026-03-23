import { postsApi } from "@/lib/api";
import BlogFeed from "@/components/blog/BlogFeed";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Blog",
  description: "Read the latest posts from AI Blog Studio.",
};

export const revalidate = 60; // ISR: revalidate every 60s

export default async function BlogPage({
  searchParams,
}: {
  searchParams: { page?: string; tag?: string };
}) {
  const page = Number(searchParams.page ?? 1);
  const tag = searchParams.tag;

  let data;
  try {
    data = await postsApi.list({ page, page_size: 12, tag });
  } catch {
    data = { items: [], total: 0, page: 1, page_size: 12, total_pages: 1 };
  }

  return (
    <main className="max-w-5xl mx-auto px-4 py-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">AI Blog Studio</h1>
          <p className="text-slate-500 mt-1 text-sm">
            {data.total} post{data.total !== 1 ? "s" : ""} published
            {tag && (
              <span className="ml-2 text-blue-600 font-medium">#{tag}</span>
            )}
          </p>
        </div>
        <Link
          href="/new"
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
        >
          + New Post
        </Link>
      </div>

      {/* Feed */}
      <BlogFeed
        posts={data.items}
        currentPage={data.page}
        totalPages={data.total_pages}
        tag={tag}
      />
    </main>
  );
}
