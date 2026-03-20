'use client';

interface Props {
  isSaving: boolean;
  onSaveDraft: () => void;
  onPublish: () => void;
}

export default function PublishControls({ isSaving, onSaveDraft, onPublish }: Props) {
  return (
    <div className="flex flex-col gap-2 pt-4 border-t border-gray-200">
      <button
        onClick={onPublish}
        disabled={isSaving}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors"
      >
        {isSaving ? 'Publishing…' : '🚀 Publish'}
      </button>
      <button
        onClick={onSaveDraft}
        disabled={isSaving}
        className="w-full bg-gray-100 hover:bg-gray-200 disabled:opacity-60 text-gray-700 font-semibold py-2.5 rounded-lg text-sm transition-colors"
      >
        {isSaving ? 'Saving…' : 'Save Draft'}
      </button>
    </div>
  );
}
