import { postsAPI, PostListResponse } from "@/lib/api";
import BlogFeed from "@/components/blog/BlogFeed";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI Blog Studio — Latest Posts",
  description: "Read the latest posts from AI Blog Studio authors.",
};

export default async function BlogFeedPage({ searchParams }: { searchParams: { page?: string; tag?: string } }) {
  const page = Number(searchParams.page) || 1;
  const tag = searchParams.tag;
  let data: PostListResponse | null = null;
  let error: string | null = null;
  try {
    data = await postsAPI.list({ page, page_size: 10, tag });
  } catch {
    error = "Failed to load posts. Please try again later.";
  }
  return <BlogFeed data={data} error={error} currentPage={page} currentTag={tag} />;
}
