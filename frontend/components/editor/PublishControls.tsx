"use client";

interface PublishControlsProps {
  isSaving: boolean;
  isPublishing: boolean;
  status: "draft" | "published";
  onSaveDraft: () => void;
  onPublish: () => void;
}

export default function PublishControls({
  isSaving,
  isPublishing,
  status,
  onSaveDraft,
  onPublish,
}: PublishControlsProps) {
  return (
    <div className="publish-controls">
      <button
        onClick={onSaveDraft}
        disabled={isSaving || isPublishing}
        className="btn-draft"
        aria-busy={isSaving}
      >
        {isSaving ? "Saving..." : "Save Draft"}
      </button>
      {status !== "published" && (
        <button
          onClick={onPublish}
          disabled={isSaving || isPublishing}
          className="btn-publish"
          aria-busy={isPublishing}
        >
          {isPublishing ? "Publishing..." : "Publish"}
        </button>
      )}
      {status === "published" && (
        <span className="published-badge">✅ Published</span>
      )}
    </div>
  );
}
