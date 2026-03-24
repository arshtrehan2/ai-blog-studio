"use client";

interface PostMetaProps {
  title: string;
  tags: string[];
  seoTitle: string;
  seoDescription: string;
  summary: string;
  onTitleChange: (v: string) => void;
  onTagsChange: (tags: string[]) => void;
  onSeoTitleChange: (v: string) => void;
  onSeoDescriptionChange: (v: string) => void;
  onSummaryChange: (v: string) => void;
}

export default function PostMeta({
  title,
  tags,
  seoTitle,
  seoDescription,
  summary,
  onTitleChange,
  onTagsChange,
  onSeoTitleChange,
  onSeoDescriptionChange,
  onSummaryChange,
}: PostMetaProps) {
  const tagString = tags.join(", ");

  const handleTagsInput = (value: string) => {
    const parsed = value
      .split(",")
      .map((t) => t.trim().toLowerCase())
      .filter(Boolean);
    onTagsChange(parsed);
  };

  return (
    <div className="post-meta-panel">
      <div className="form-group">
        <label htmlFor="post-title">Title *</label>
        <input
          id="post-title"
          type="text"
          value={title}
          onChange={(e) => onTitleChange(e.target.value)}
          placeholder="Post title..."
          maxLength={255}
          required
        />
        <span className="char-count">{title.length}/255</span>
      </div>

      <div className="form-group">
        <label htmlFor="post-tags">Tags</label>
        <input
          id="post-tags"
          type="text"
          defaultValue={tagString}
          onBlur={(e) => handleTagsInput(e.target.value)}
          placeholder="python, fastapi, web (comma separated)"
        />
      </div>

      <div className="form-group">
        <label htmlFor="post-summary">Summary</label>
        <textarea
          id="post-summary"
          value={summary}
          onChange={(e) => onSummaryChange(e.target.value)}
          placeholder="Short summary for the post feed..."
          rows={3}
        />
      </div>

      <details className="seo-section">
        <summary>SEO Settings</summary>
        <div className="form-group">
          <label htmlFor="seo-title">SEO Title</label>
          <input
            id="seo-title"
            type="text"
            value={seoTitle}
            onChange={(e) => onSeoTitleChange(e.target.value)}
            placeholder="SEO-optimized title (max 60 chars)"
            maxLength={60}
          />
          <span className="char-count">{seoTitle.length}/60</span>
        </div>
        <div className="form-group">
          <label htmlFor="seo-description">Meta Description</label>
          <textarea
            id="seo-description"
            value={seoDescription}
            onChange={(e) => onSeoDescriptionChange(e.target.value)}
            placeholder="Meta description (max 155 chars)"
            maxLength={155}
            rows={3}
          />
          <span className="char-count">{seoDescription.length}/155</span>
        </div>
      </details>
    </div>
  );
}
