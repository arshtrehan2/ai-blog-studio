"use client";
import { useRouter } from "next/navigation";
import EditorPage from "@/components/editor/EditorPage";
import { postsAPI, CreatePostRequest } from "@/lib/api";
import { getToken } from "@/lib/auth";

export default function NewPostPage() {
  const router = useRouter();
  async function handleSave(data: CreatePostRequest) {
    const token = getToken();
    if (!token) { router.push("/login"); return; }
    const post = await postsAPI.create(data, token);
    router.push(`/${post.id}/edit`);
  }
  return <EditorPage mode="create" onSave={handleSave} />;
}
