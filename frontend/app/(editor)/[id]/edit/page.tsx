"use client";
import { useParams } from "next/navigation";
import EditorPage from "@/components/editor/EditorPage";

export default function EditPostPage() {
  const params = useParams<{ id: string }>();
  return <EditorPage postId={params.id} />;
}
