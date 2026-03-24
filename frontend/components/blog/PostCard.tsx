import Link from "next/link";
import type { PostListItem } from "@/lib/types";

interface Props {
  post: PostListItem;
}

export function PostCard({ post }: Props) {
  return (
    <article className="border-b border-slate-100 pb-6">
      <Link href={`/blog/${post.slug}`} className="group">
        <h2 className="text-lg font-semibold text-slate-800 group-hover:text-indigo-600 transition">
          {post.title}
        </h2>
      </Link>
      {post.summary && (
        <p className="mt-1 text-sm text-slate-600 leading-relaxed">{post.summary}</p>
      )}
      <div className="mt-2 flex items-center gap-2 text-xs text-slate-400 flex-wrap">
        {post.author && <span>{post.author.display_name}</span>}
        {post.published_at && (
          <>
            <span>&middot;</span>
            <time dateTime={post.published_at}>
              {new Date(post.published_at).toLocaleDateString()}
            </time>
          </>
        )}
        {post.tags.map((tag) => (
          <Link
            key={tag}
            href={`/?tag=${tag}`}
            className="bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 px-2 py-0.5 rounded-full"
          >
            {tag}
          </Link>
        ))}
      </div>
    </article>
  );
}
