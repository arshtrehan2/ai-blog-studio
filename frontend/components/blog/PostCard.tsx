import { type PostListItem } from "@/lib/api";
import Link from "next/link";

interface Props {
  post: PostListItem;
}

export default function PostCard({ post }: Props) {
  const date = new Date(post.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <article className="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-md transition-shadow flex flex-col">
      {/* Tags */}
      {post.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {post.tags.slice(0, 3).map((t) => (
            <Link
              key={t}
              href={`/?tag=${t}`}
              className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full hover:bg-blue-100 transition-colors"
            >
              #{t}
            </Link>
          ))}
        </div>
      )}

      {/* Title */}
      <Link href={`/${post.slug}`} className="group flex-1">
        <h2 className="font-bold text-slate-900 text-base mb-2 group-hover:text-blue-600 transition-colors line-clamp-2">
          {post.title}
        </h2>
        {post.summary && (
          <p className="text-sm text-slate-500 line-clamp-3">{post.summary}</p>
        )}
      </Link>

      {/* Footer */}
      <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-100">
        <span className="text-xs text-slate-400">{post.author.display_name}</span>
        <span className="text-xs text-slate-400">{date}</span>
      </div>
    </article>
  );
}
