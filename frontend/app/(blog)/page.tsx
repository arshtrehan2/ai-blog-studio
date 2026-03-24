import { Metadata } from "next";
import PostCard from "@/components/blog/PostCard";
import { PaginatedPosts } from "@/lib/api";

export const metadata: Metadata = {
  title: "Blog Feed | AI Blog Studio",
  description: "Browse the latest blog posts",
};

async function getPosts(searchParams: { page?: string; tag?: string }): Promise<PaginatedPosts> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const params = new URLSearchParams();
  if (searchParams.page) params.set("page", searchParams.page);
  if (searchParams.tag) params.set("tag", searchParams.tag);

  const res = await fetch(`${apiUrl}/posts?${params.toString()}`, {
    next: { revalidate: 60 },
  });

  if (!res.ok) {
    return { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 };
  }
  return res.json();
}

interface PageProps {
  searchParams: Promise<{ page?: string; tag?: string }>;
}

export default async function BlogFeedPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const data = await getPosts(params);

  return (
    <div className="blog-feed">
      <div className="feed-header">
        <h1>Latest Posts</h1>
        {params.tag && (
          <p className="tag-filter">
            Filtered by: <strong>{params.tag}</strong>{" "}
            <a href="/">Clear filter</a>
          </p>
        )}
      </div>

      {data.items.length === 0 ? (
        <p className="no-posts">No posts yet. Be the first to write!</p>
      ) : (
        <div className="posts-grid">
          {data.items.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}

      {data.total_pages > 1 && (
        <div className="pagination">
          {data.page > 1 && (
            <a href={`?page=${data.page - 1}${params.tag ? `&tag=${params.tag}` : ""}`}>
              ← Previous
            </a>
          )}
          <span>
            Page {data.page} of {data.total_pages}
          </span>
          {data.page < data.total_pages && (
            <a href={`?page=${data.page + 1}${params.tag ? `&tag=${params.tag}` : ""}`}>
              Next →
            </a>
          )}
        </div>
      )}
    </div>
  );
}
