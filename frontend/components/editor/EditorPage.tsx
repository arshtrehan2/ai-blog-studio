"use client";
import { useReducer } from "react";
import { Post, CreatePostRequest, UpdatePostRequest } from "@/lib/api";
import MarkdownEditor from "./MarkdownEditor";
import EditorSidebar from "./EditorSidebar";
import WordCount from "./WordCount";

interface EditorState {
  title: string; content: string; tags: string[]; summary: string;
  seoTitle: string; seoDescription: string; isDirty: boolean; isSaving: boolean; error: string | null;
}

type EditorAction =
  | { type: "SET_TITLE"; value: string } | { type: "SET_CONTENT"; value: string }
  | { type: "SET_TAGS"; value: string[] } | { type: "SET_SUMMARY"; value: string }
  | { type: "SET_SEO_TITLE"; value: string } | { type: "SET_SEO_DESCRIPTION"; value: string }
  | { type: "SAVING" } | { type: "SAVED" } | { type: "ERROR"; message: string };

function editorReducer(state: EditorState, action: EditorAction): EditorState {
  switch (action.type) {
    case "SET_TITLE": return { ...state, title: action.value, isDirty: true };
    case "SET_CONTENT": return { ...state, content: action.value, isDirty: true };
    case "SET_TAGS": return { ...state, tags: action.value, isDirty: true };
    case "SET_SUMMARY": return { ...state, summary: action.value, isDirty: true };
    case "SET_SEO_TITLE": return { ...state, seoTitle: action.value, isDirty: true };
    case "SET_SEO_DESCRIPTION": return { ...state, seoDescription: action.value, isDirty: true };
    case "SAVING": return { ...state, isSaving: true, error: null };
    case "SAVED": return { ...state, isSaving: false, isDirty: false };
    case "ERROR": return { ...state, isSaving: false, error: action.message };
    default: return state;
  }
}

interface Props {
  mode: "create" | "edit";
  initialPost?: Post;
  onSave: (data: CreatePostRequest | UpdatePostRequest) => Promise<void>;
  onPublish?: () => Promise<void>;
}

export default function EditorPage({ mode, initialPost, onSave, onPublish }: Props) {
  const [state, dispatch] = useReducer(editorReducer, {
    title: initialPost?.title || "",
    content: initialPost?.content || "",
    tags: initialPost?.tags || [],
    summary: initialPost?.summary || "",
    seoTitle: initialPost?.seo_title || "",
    seoDescription: initialPost?.seo_description || "",
    isDirty: false, isSaving: false, error: null,
  });

  async function handleSave() {
    dispatch({ type: "SAVING" });
    try {
      await onSave({ title: state.title, content: state.content, tags: state.tags,
        summary: state.summary || null, seo_title: state.seoTitle || null, seo_description: state.seoDescription || null,
        ...(mode === "create" ? { status: "draft" as const } : {}) });
      dispatch({ type: "SAVED" });
    } catch { dispatch({ type: "ERROR", message: "Failed to save. Please try again." }); }
  }

  async function handlePublish() {
    if (!onPublish) return;
    dispatch({ type: "SAVING" });
    try { await onPublish(); dispatch({ type: "SAVED" }); }
    catch { dispatch({ type: "ERROR", message: "Failed to publish. Please try again." }); }
  }

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden", flexDirection: "column" }}>
      <div style={{ padding: "12px 24px", borderBottom: "1px solid var(--color-border)", display: "flex", alignItems: "center", gap: 16, background: "white", flexShrink: 0 }}>
        <input type="text" value={state.title} onChange={e => dispatch({ type: "SET_TITLE", value: e.target.value })}
          placeholder="Post title..." style={{ flex: 1, fontSize: 22, fontWeight: 700, border: "none", outline: "none", padding: "4px 0" }} />
        <WordCount content={state.content} />
        <button onClick={handleSave} disabled={state.isSaving || !state.isDirty}
          style={{ padding: "8px 16px", border: "1px solid var(--color-border)", borderRadius: 6, background: "white", fontSize: 14, fontWeight: 500, opacity: state.isSaving || !state.isDirty ? 0.5 : 1 }}>
          {state.isSaving ? "Saving..." : "Save Draft"}
        </button>
        {mode === "edit" && onPublish && (
          <button onClick={handlePublish} disabled={state.isSaving}
            style={{ padding: "8px 16px", background: "var(--color-primary)", color: "white", border: "none", borderRadius: 6, fontSize: 14, fontWeight: 600, opacity: state.isSaving ? 0.5 : 1 }}>
            Publish
          </button>
        )}
      </div>
      {state.error && <div role="alert" style={{ padding: "10px 24px", background: "#fef2f2", color: "var(--color-error)", borderBottom: "1px solid #fca5a5", fontSize: 14 }}>{state.error}</div>}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <MarkdownEditor content={state.content} onChange={v => dispatch({ type: "SET_CONTENT", value: v })} />
        <EditorSidebar content={state.content} title={state.title} tags={state.tags}
          summary={state.summary} seoTitle={state.seoTitle} seoDescription={state.seoDescription}
          onTagsChange={v => dispatch({ type: "SET_TAGS", value: v })}
          onSummaryChange={v => dispatch({ type: "SET_SUMMARY", value: v })}
          onSeoTitleChange={v => dispatch({ type: "SET_SEO_TITLE", value: v })}
          onSeoDescriptionChange={v => dispatch({ type: "SET_SEO_DESCRIPTION", value: v })} />
      </div>
    </div>
  );
}
