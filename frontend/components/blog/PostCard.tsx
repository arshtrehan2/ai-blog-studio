import Link from "next/link";
import { PostListItem } from "@/lib/api";

export default function PostCard({ post }: { post: PostListItem }) {
  return (
    <article style={{ padding: 24, border: "1px solid var(--color-border)", borderRadius: 8 }}>
      <Link href={`/${post.slug}`} style={{ color: "inherit", textDecoration: "none" }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8, lineHeight: 1.3 }}>{post.title}</h2>
      </Link>
      {post.summary && <p style={{ color: "var(--color-text-muted)", marginBottom: 12, lineHeight: 1.6 }}>{post.summary}</p>}
      <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        {post.author && <span style={{ fontSize: 13, color: "var(--color-text-muted)" }}>{post.author.display_name}</span>}
        {post.published_at && <span style={{ fontSize: 13, color: "var(--color-text-muted)" }}>{new Date(post.published_at).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" })}</span>}
        {post.tags.map(tag => (
          <Link key={tag} href={`/?tag=${encodeURIComponent(tag)}`}
            style={{ padding: "2px 8px", background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)", borderRadius: 12, fontSize: 12, color: "var(--color-text-muted)" }}>
            {tag}
          </Link>
        ))}
      </div>
    </article>
  );
}
