"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import EditorPage from "@/components/editor/EditorPage";
import { postsAPI, Post, UpdatePostRequest } from "@/lib/api";
import { getToken } from "@/lib/auth";

export default function EditPostPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [post, setPost] = useState<Post | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) { router.push("/login"); return; }
    postsAPI.get(params.id, token).then(setPost).catch(() => setError("Failed to load post.")).finally(() => setLoading(false));
  }, [params.id, router]);

  async function handleSave(data: UpdatePostRequest) {
    const token = getToken();
    if (!token) { router.push("/login"); return; }
    await postsAPI.update(params.id, data, token);
  }

  async function handlePublish() {
    const token = getToken();
    if (!token) return;
    const result = await postsAPI.publish(params.id, token);
    router.push(`/${result.slug}`);
  }

  if (loading) return <div style={{ padding: 48, textAlign: "center" }}>Loading...</div>;
  if (error) return <div style={{ padding: 48, textAlign: "center", color: "red" }}>{error}</div>;
  if (!post) return null;
  return <EditorPage mode="edit" initialPost={post} onSave={handleSave} onPublish={handlePublish} />;
}
