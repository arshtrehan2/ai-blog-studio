import { Metadata } from "next";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { Post } from "@/lib/api";

interface PageProps {
  params: Promise<{ slug: string }>;
}

async function getPost(slug: string): Promise<Post | null> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${apiUrl}/posts/${slug}`, {
    next: { revalidate: 300 },
  });
  if (res.status === 404) return null;
  if (!res.ok) return null;
  return res.json();
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPost(slug);
  if (!post) {
    return { title: "Post Not Found | AI Blog Studio" };
  }

  const title = post.seo_title || post.title;
  const description = post.seo_description || post.summary || "";

  return {
    title: `${title} | AI Blog Studio`,
    description,
    openGraph: {
      title,
      description,
      type: "article",
      publishedTime: post.published_at || undefined,
      authors: post.author ? [post.author.display_name] : [],
    },
  };
}

export default async function PostPage({ params }: PageProps) {
  const { slug } = await params;
  const post = await getPost(slug);

  if (!post) {
    notFound();
  }

  return (
    <article className="post-detail">
      <header className="post-header">
        <h1>{post.title}</h1>
        <div className="post-meta">
          {post.author && (
            <span className="post-author">By {post.author.display_name}</span>
          )}
          {post.published_at && (
            <time dateTime={post.published_at}>
              {new Date(post.published_at).toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </time>
          )}
        </div>
        {post.tags.length > 0 && (
          <div className="post-tags">
            {post.tags.map((tag) => (
              <a key={tag} href={`/?tag=${tag}`} className="tag">
                {tag}
              </a>
            ))}
          </div>
        )}
      </header>

      {post.summary && (
        <div className="post-summary-box">
          <strong>Summary:</strong> {post.summary}
        </div>
      )}

      <div className="post-content">
        <ReactMarkdown>{post.content}</ReactMarkdown>
      </div>
    </article>
  );
}
