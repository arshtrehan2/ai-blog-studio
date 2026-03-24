import { Metadata } from "next";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { serverFetch } from "@/lib/api";
import type { Post } from "@/lib/types";

interface Props {
  params: { slug: string };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  try {
    const post = await serverFetch<Post>(`/posts/${params.slug}`);
    return {
      title: post.seo_title ?? post.title,
      description: post.seo_description ?? post.summary ?? "",
      openGraph: {
        title: post.seo_title ?? post.title,
        description: post.seo_description ?? post.summary ?? "",
        type: "article",
        publishedTime: post.published_at ?? undefined,
      },
    };
  } catch {
    return { title: "Post not found" };
  }
}

export default async function BlogPostPage({ params }: Props) {
  let post: Post;
  try {
    post = await serverFetch<Post>(`/posts/${params.slug}`);
  } catch {
    notFound();
  }

  return (
    <article className="max-w-3xl mx-auto px-4 py-12">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 leading-tight">{post.title}</h1>
        <div className="mt-4 flex items-center gap-3 text-sm text-slate-500">
          <span>{post.author?.display_name}</span>
          <span>&middot;</span>
          <time dateTime={post.published_at ?? post.created_at}>
            {new Date(post.published_at ?? post.created_at).toLocaleDateString("en-US", {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </time>
        </div>
        {post.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {post.tags.map((tag) => (
              <span
                key={tag}
                className="bg-indigo-50 text-indigo-700 text-xs px-2 py-1 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </header>

      <div className="prose prose-slate max-w-none">
        <ReactMarkdown>{post.content}</ReactMarkdown>
      </div>
    </article>
  );
}
