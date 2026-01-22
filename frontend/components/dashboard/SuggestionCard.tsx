'use client';

interface SuggestionCardProps {
  suggestion: string;
}

export function SuggestionCard({ suggestion }: SuggestionCardProps) {
  return (
    <div className="glass-panel p-4 rounded-xl border-l-4 border-indigo-500">
      <p className="text-xs font-semibold text-indigo-500 uppercase mb-1">
        Suggestion
      </p>
      <p className="text-sm text-zinc-900 dark:text-white">{suggestion}</p>
    </div>
  );
}
