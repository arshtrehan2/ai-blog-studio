import { postsApi } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

export const revalidate = 60;

type Props = { params: { slug: string } };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  try {
    const post = await postsApi.get(params.slug);
    return {
      title: post.seo_title ?? post.title,
      description: post.seo_description ?? post.summary ?? undefined,
      openGraph: {
        title: post.seo_title ?? post.title,
        description: post.seo_description ?? post.summary ?? undefined,
        type: "article",
        publishedTime: post.published_at,
        authors: [post.author.display_name],
      },
    };
  } catch {
    return { title: "Post not found" };
  }
}

export default async function PostPage({ params }: Props) {
  let post;
  try {
    post = await postsApi.get(params.slug);
  } catch (err: unknown) {
    const e = err as { status?: number };
    if (e?.status === 404 || e?.status === 403) notFound();
    throw err;
  }

  return (
    <main className="max-w-3xl mx-auto px-4 py-10">
      {/* Back link */}
      <Link
        href="/"
        className="text-sm text-blue-600 hover:underline mb-6 inline-block"
      >
        ← Back to blog
      </Link>

      {/* Header */}
      <article>
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-3">
            {post.title}
          </h1>
          <div className="flex flex-wrap items-center gap-3 text-sm text-slate-500">
            <span>By {post.author.display_name}</span>
            {post.published_at && (
              <span>
                ·{" "}
                {new Date(post.published_at).toLocaleDateString("en-US", {
                  month: "long",
                  day: "numeric",
                  year: "numeric",
                })}
              </span>
            )}
          </div>
          {post.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-4">
              {post.tags.map((t) => (
                <Link
                  key={t}
                  href={`/?tag=${t}`}
                  className="inline-block bg-blue-50 text-blue-700 text-xs font-medium px-2.5 py-1 rounded-full hover:bg-blue-100 transition-colors"
                >
                  #{t}
                </Link>
              ))}
            </div>
          )}
          {post.summary && (
            <p className="mt-4 text-slate-600 italic border-l-4 border-blue-200 pl-4">
              {post.summary}
            </p>
          )}
        </header>

        {/* Content */}
        <div className="prose prose-slate max-w-none">
          <ReactMarkdown>{post.content}</ReactMarkdown>
        </div>
      </article>
    </main>
  );
}
