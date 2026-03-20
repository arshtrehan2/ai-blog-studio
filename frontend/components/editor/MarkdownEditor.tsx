'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import WordCount from './WordCount';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export default function MarkdownEditor({ value, onChange }: Props) {
  const [tab, setTab] = useState<'write' | 'preview'>('write');

  return (
    <div className="flex flex-col h-full bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-100 bg-gray-50">
        <div className="flex gap-1">
          <button
            onClick={() => setTab('write')}
            className={`px-3 py-1 text-sm rounded-md font-medium transition-colors ${
              tab === 'write'
                ? 'bg-white shadow-sm text-gray-900 border border-gray-200'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Write
          </button>
          <button
            onClick={() => setTab('preview')}
            className={`px-3 py-1 text-sm rounded-md font-medium transition-colors ${
              tab === 'preview'
                ? 'bg-white shadow-sm text-gray-900 border border-gray-200'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Preview
          </button>
        </div>
        <span className="text-xs text-gray-400">Markdown supported</span>
      </div>

      {/* Editor / Preview */}
      <div className="flex-1 overflow-auto">
        {tab === 'write' ? (
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="w-full h-full min-h-[500px] p-5 text-sm font-mono text-gray-800 resize-none focus:outline-none leading-relaxed"
            placeholder="Start writing your post in Markdown…\n\n# My Awesome Post\n\nWrite something great here."
            spellCheck={false}
          />
        ) : (
          <div className="p-5 markdown-body min-h-[500px]">
            {value ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{value}</ReactMarkdown>
            ) : (
              <p className="text-gray-400 italic">Nothing to preview yet.</p>
            )}
          </div>
        )}
      </div>

      {/* Word count */}
      <WordCount content={value} />
    </div>
  );
}
