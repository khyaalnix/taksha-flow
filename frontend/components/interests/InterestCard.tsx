'use client';

interface InterestCardProps {
  id: string;
  name: string;
  icon: string;
  description: string;
  selected: boolean;
  onToggle: (id: string) => void;
}

export function InterestCard({
  id,
  name,
  icon,
  description,
  selected,
  onToggle,
}: InterestCardProps) {
  return (
    <button
      onClick={() => onToggle(id)}
      className={`p-6 rounded-2xl border-2 transition-all duration-300 text-left ${
        selected
          ? 'border-primary bg-primary/5 dark:bg-primary/10'
          : 'border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/50 hover:border-zinc-300 dark:hover:border-zinc-700'
      }`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="text-3xl">{icon}</div>
        {selected && (
          <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center">
            <span className="material-symbols-outlined text-white text-sm">check</span>
          </div>
        )}
      </div>
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-white mb-2">{name}</h3>
      <p className="text-sm text-zinc-600 dark:text-zinc-400">{description}</p>
    </button>
  );
}
