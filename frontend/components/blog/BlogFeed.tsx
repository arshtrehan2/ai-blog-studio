"use client";

import { type PostListItem } from "@/lib/api";
import PostCard from "./PostCard";
import Link from "next/link";

interface Props {
  posts: PostListItem[];
  currentPage: number;
  totalPages: number;
  tag?: string;
}

export default function BlogFeed({
  posts,
  currentPage,
  totalPages,
  tag,
}: Props) {
  if (posts.length === 0) {
    return (
      <div className="text-center py-20">
        <p className="text-slate-400 text-lg mb-2">✍️ No posts yet</p>
        <p className="text-slate-400 text-sm">
          {tag ? `No posts tagged "${tag}".` : "Be the first to publish something!"}
        </p>
        <Link
          href="/new"
          className="inline-block mt-4 bg-blue-600 text-white text-sm font-semibold px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Write a Post
        </Link>
      </div>
    );
  }

  return (
    <div>
      {/* Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-3 mt-10">
          {currentPage > 1 && (
            <Link
              href={`/?page=${currentPage - 1}${tag ? `&tag=${tag}` : ""}`}
              className="text-sm px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-50 transition-colors"
            >
              ← Previous
            </Link>
          )}
          <span className="text-sm text-slate-500">
            Page {currentPage} of {totalPages}
          </span>
          {currentPage < totalPages && (
            <Link
              href={`/?page=${currentPage + 1}${tag ? `&tag=${tag}` : ""}`}
              className="text-sm px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-50 transition-colors"
            >
              Next →
            </Link>
          )}
        </div>
      )}
    </div>
  );
}
