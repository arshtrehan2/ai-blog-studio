import Link from 'next/link';
import { PostListItem } from '@/lib/api';

interface Props {
  post: PostListItem;
}

export default function BlogCard({ post }: Props) {
  const date = new Date(post.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  return (
    <article className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow">
      {/* Tags */}
      {post.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {post.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full font-medium"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}

      {/* Title */}
      <Link href={`/blog/${post.slug}`}>
        <h2 className="text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors mb-2">
          {post.title}
        </h2>
      </Link>

      {/* Summary */}
      {post.summary && (
        <p className="text-gray-600 text-sm leading-relaxed mb-4 line-clamp-3">
          {post.summary}
        </p>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-400">
        <span className="font-medium text-gray-600">{post.author.display_name}</span>
        <time dateTime={post.created_at}>{date}</time>
      </div>
    </article>
  );
}
