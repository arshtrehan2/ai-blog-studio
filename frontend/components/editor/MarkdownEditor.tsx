"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";

interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export default function MarkdownEditor({
  value,
  onChange,
  placeholder = "Write your content in Markdown...",
}: MarkdownEditorProps) {
  const [mode, setMode] = useState<"edit" | "preview" | "split">("split");

  return (
    <div className="markdown-editor">
      <div className="editor-toolbar">
        <button
          onClick={() => setMode("edit")}
          className={mode === "edit" ? "active" : ""}
          aria-pressed={mode === "edit"}
        >
          Edit
        </button>
        <button
          onClick={() => setMode("split")}
          className={mode === "split" ? "active" : ""}
          aria-pressed={mode === "split"}
        >
          Split
        </button>
        <button
          onClick={() => setMode("preview")}
          className={mode === "preview" ? "active" : ""}
          aria-pressed={mode === "preview"}
        >
          Preview
        </button>
      </div>

      <div className={`editor-panes mode-${mode}`}>
        {(mode === "edit" || mode === "split") && (
          <textarea
            className="edit-pane"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            aria-label="Markdown content"
          />
        )}
        {(mode === "preview" || mode === "split") && (
          <div className="preview-pane" aria-label="Preview">
            <ReactMarkdown>{value || "*Preview will appear here*"}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
