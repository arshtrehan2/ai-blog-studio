"use client";

import Link from "next/link";
import { PostListItem } from "@/lib/api";

interface PostCardProps {
  post: PostListItem;
}

export default function PostCard({ post }: PostCardProps) {
  return (
    <article className="post-card">
      <h2>
        <Link href={`/blog/${post.slug}`}>{post.title}</Link>
      </h2>
      {post.summary && <p className="post-summary">{post.summary}</p>}
      <div className="post-meta">
        <span className="post-author">By {post.author.display_name}</span>
        <span className="post-date">
          {new Date(post.created_at).toLocaleDateString()}
        </span>
      </div>
      {post.tags.length > 0 && (
        <div className="post-tags">
          {post.tags.map((tag) => (
            <Link key={tag} href={`/?tag=${tag}`} className="tag">
              {tag}
            </Link>
          ))}
        </div>
      )}
    </article>
  );
}
