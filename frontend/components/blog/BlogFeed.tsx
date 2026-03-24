"use client";
import Link from "next/link";
import { PostListResponse } from "@/lib/api";
import PostCard from "./PostCard";

interface Props { data: PostListResponse | null; error: string | null; currentPage: number; currentTag?: string; }

export default function BlogFeed({ data, error, currentPage, currentTag }: Props) {
  if (error) return <div style={{ maxWidth: 760, margin: "48px auto", padding: "0 24px", textAlign: "center" }}><p style={{ color: "var(--color-error)" }}>{error}</p></div>;
  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "48px 24px" }}>
      <header style={{ marginBottom: 40, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: 32, fontWeight: 800 }}>AI Blog Studio</h1>
          {currentTag && <p style={{ color: "var(--color-text-muted)", marginTop: 4 }}>Posts tagged: <strong>{currentTag}</strong> <Link href="/" style={{ fontSize: 13 }}>clear</Link></p>}
        </div>
        <Link href="/new" style={{ padding: "10px 20px", background: "var(--color-primary)", color: "white", borderRadius: 6, fontWeight: 600, fontSize: 14 }}>New Post</Link>
      </header>
      {!data || data.items.length === 0 ? (
        <div style={{ textAlign: "center", padding: "80px 0", color: "var(--color-text-muted)" }}>
          <p style={{ fontSize: 18 }}>No posts yet.</p>
          <p style={{ marginTop: 8 }}><Link href="/new">Write the first one!</Link></p>
        </div>
      ) : (
        <>
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            {data.items.map(post => <PostCard key={post.id} post={post} />)}
          </div>
          {data.total_pages > 1 && (
            <nav style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 48 }} aria-label="Pagination">
              {currentPage > 1 && <Link href={`/?page=${currentPage - 1}${currentTag ? `&tag=${currentTag}` : ""}`} style={{ padding: "8px 16px", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 14 }}>Previous</Link>}
              <span style={{ padding: "8px 16px", color: "var(--color-text-muted)", fontSize: 14 }}>Page {currentPage} of {data.total_pages}</span>
              {currentPage < data.total_pages && <Link href={`/?page=${currentPage + 1}${currentTag ? `&tag=${currentTag}` : ""}`} style={{ padding: "8px 16px", border: "1px solid var(--color-border)", borderRadius: 6, fontSize: 14 }}>Next</Link>}
            </nav>
          )}
        </>
      )}
    </div>
  );
}
