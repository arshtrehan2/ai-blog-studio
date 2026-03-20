'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { aiAPI } from '@/lib/api';
import AISuggestion from './AISuggestion';

type Tool = 'improve' | 'summary' | 'tags' | 'seo-title' | 'tldr' | null;

interface Suggestion {
  tool: Tool;
  label: string;
  value: string;
}

interface Props {
  title: string;
  content: string;
  onContentChange: (v: string) => void;
  onSummaryChange: (v: string) => void;
  onTagsChange: (tags: string[]) => void;
  onSeoTitleChange: (v: string) => void;
  onSeoDescriptionChange: (v: string) => void;
}

const TOOLS: { id: Tool; label: string; emoji: string; description: string }[] = [
  { id: 'improve', label: 'Improve Writing', emoji: '✍️', description: 'Rewrite for clarity & engagement' },
  { id: 'summary', label: 'Generate Summary', emoji: '📝', description: 'Create a concise summary' },
  { id: 'tags', label: 'Suggest Tags', emoji: '🏷️', description: 'Auto-generate relevant tags' },
  { id: 'seo-title', label: 'SEO Title', emoji: '🔎', description: 'Optimise title & meta description' },
  { id: 'tldr', label: 'TLDR', emoji: '⚡', description: '1-2 sentence summary' },
];

export default function AIToolsPanel({
  title,
  content,
  onContentChange,
  onSummaryChange,
  onTagsChange,
  onSeoTitleChange,
  onSeoDescriptionChange,
}: Props) {
  const [loading, setLoading] = useState<Tool>(null);
  const [suggestion, setSuggestion] = useState<Suggestion | null>(null);

  async function runTool(toolId: Tool) {
    if (!content.trim()) {
      toast.error('Write some content first!');
      return;
    }
    setLoading(toolId);
    setSuggestion(null);
    try {
      switch (toolId) {
        case 'improve': {
          const res = await aiAPI.improve(content);
          setSuggestion({ tool: toolId, label: 'Improved Content', value: res.improved_content });
          break;
        }
        case 'summary': {
          const res = await aiAPI.summary(content);
          setSuggestion({ tool: toolId, label: 'Summary', value: res.summary });
          break;
        }
        case 'tags': {
          const res = await aiAPI.tags(content, title);
          setSuggestion({
            tool: toolId,
            label: 'Suggested Tags',
            value: res.tags.join(', '),
          });
          break;
        }
        case 'seo-title': {
          const res = await aiAPI.seoTitle(content, title);
          setSuggestion({
            tool: toolId,
            label: 'SEO Suggestion',
            value: `Title: ${res.seo_title}\n\nDescription: ${res.seo_description}`,
          });
          break;
        }
        case 'tldr': {
          const res = await aiAPI.tldr(content);
          setSuggestion({ tool: toolId, label: 'TLDR', value: res.tldr });
          break;
        }
      }
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 429) {
        toast.error('Rate limit reached. Try again in an hour.');
      } else if (status === 401) {
        toast.error('Please sign in to use AI tools.');
      } else {
        toast.error('AI request failed. Please try again.');
      }
    } finally {
      setLoading(null);
    }
  }

  function handleAccept(value: string) {
    if (!suggestion) return;
    switch (suggestion.tool) {
      case 'improve':
        onContentChange(value);
        toast.success('Content updated!');
        break;
      case 'summary':
        onSummaryChange(value);
        toast.success('Summary applied!');
        break;
      case 'tags': {
        const parsed = value.split(',').map((t) => t.trim()).filter(Boolean);
        onTagsChange(parsed);
        toast.success('Tags applied!');
        break;
      }
      case 'seo-title': {
        const lines = value.split('\n');
        const titleLine = lines.find((l) => l.startsWith('Title:'));
        const descLine = lines.find((l) => l.startsWith('Description:'));
        if (titleLine) onSeoTitleChange(titleLine.replace('Title:', '').trim());
        if (descLine) onSeoDescriptionChange(descLine.replace('Description:', '').trim());
        toast.success('SEO fields updated!');
        break;
      }
      case 'tldr':
        onSummaryChange(value);
        toast.success('TLDR applied as summary!');
        break;
    }
    setSuggestion(null);
  }

  return (
    <div>
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
        AI Tools
      </p>
      <div className="space-y-2">
        {TOOLS.map((tool) => (
          <button
            key={tool.id}
            onClick={() => runTool(tool.id)}
            disabled={loading !== null}
            className="w-full flex items-start gap-3 p-3 bg-white border border-gray-200 rounded-xl hover:border-blue-300 hover:bg-blue-50 disabled:opacity-50 transition-all text-left"
          >
            <span className="text-lg leading-none mt-0.5">{tool.emoji}</span>
            <div>
              <p className="text-sm font-medium text-gray-800">
                {loading === tool.id ? 'Generating…' : tool.label}
              </p>
              <p className="text-xs text-gray-400">{tool.description}</p>
            </div>
            {loading === tool.id && (
              <div className="ml-auto mt-1">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
              </div>
            )}
          </button>
        ))}
      </div>

      {suggestion && (
        <AISuggestion
          label={suggestion.label}
          suggestion={suggestion.value}
          onAccept={handleAccept}
          onReject={() => setSuggestion(null)}
        />
      )}
    </div>
  );
}
