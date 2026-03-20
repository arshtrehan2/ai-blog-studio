'use client';

interface Props {
  label: string;
  suggestion: string;
  onAccept: (suggestion: string) => void;
  onReject: () => void;
}

export default function AISuggestion({ label, suggestion, onAccept, onReject }: Props) {
  return (
    <div className="bg-green-50 border border-green-200 rounded-xl p-4 mt-3">
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs font-semibold text-green-700 uppercase tracking-wide">
          ✨ {label}
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => onAccept(suggestion)}
            className="text-xs bg-green-600 text-white px-3 py-1 rounded-md hover:bg-green-700 font-medium"
          >
            Accept
          </button>
          <button
            onClick={onReject}
            className="text-xs bg-white text-gray-600 border border-gray-300 px-3 py-1 rounded-md hover:bg-gray-50 font-medium"
          >
            Reject
          </button>
        </div>
      </div>
      <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap line-clamp-6">
        {suggestion}
      </p>
    </div>
  );
}
