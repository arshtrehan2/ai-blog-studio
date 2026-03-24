import { postsAPI } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import type { Metadata } from "next";
import { notFound } from "next/navigation";

interface Props { params: { slug: string }; }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  try {
    const post = await postsAPI.get(params.slug);
    return {
      title: post.seo_title || post.title,
      description: post.seo_description || post.summary || undefined,
      openGraph: {
        title: post.seo_title || post.title,
        description: post.seo_description || post.summary || undefined,
        type: "article",
        publishedTime: post.published_at || undefined,
        authors: post.author ? [post.author.display_name] : undefined,
      },
    };
  } catch {
    return { title: "Post Not Found" };
  }
}

export default async function PostPage({ params }: Props) {
  let post;
  try { post = await postsAPI.get(params.slug); }
  catch { notFound(); }
  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: "48px 24px" }}>
      <article>
        <header style={{ marginBottom: 40 }}>
          <h1 style={{ fontSize: 36, fontWeight: 800, lineHeight: 1.2, marginBottom: 16 }}>{post.title}</h1>
          <div style={{ display: "flex", gap: 12, alignItems: "center", color: "var(--color-text-muted)", fontSize: 14 }}>
            {post.author && <span>By <strong>{post.author.display_name}</strong></span>}
            {post.published_at && <span>{new Date(post.published_at).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}</span>}
          </div>
          {post.tags.length > 0 && (
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 16 }}>
              {post.tags.map(tag => (
                <a key={tag} href={`/?tag=${encodeURIComponent(tag)}`}
                  style={{ padding: "4px 10px", background: "var(--color-bg-secondary)", border: "1px solid var(--color-border)", borderRadius: 20, fontSize: 13, color: "var(--color-text-muted)" }}>
                  {tag}
                </a>
              ))}
            </div>
          )}
          {post.summary && (
            <p style={{ marginTop: 20, padding: 16, background: "var(--color-bg-secondary)", borderLeft: "4px solid var(--color-primary)", borderRadius: "0 6px 6px 0", color: "var(--color-text-muted)", fontStyle: "italic" }}>
              {post.summary}
            </p>
          )}
        </header>
        <div style={{ lineHeight: 1.8, fontSize: 17 }}>
          <ReactMarkdown>{post.content}</ReactMarkdown>
        </div>
      </article>
    </div>
  );
}
