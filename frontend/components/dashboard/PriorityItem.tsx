'use client';

export interface PriorityItemData {
  id: string;
  type: 'event' | 'email' | 'news' | 'task';
  title: string;
  subtitle: string;
}

interface PriorityItemProps {
  item: PriorityItemData;
  onClick?: () => void;
}

const iconConfig = {
  event: {
    icon: 'event',
    bgColor: 'bg-orange-100 dark:bg-orange-900/30',
    textColor: 'text-orange-600 dark:text-orange-400',
  },
  email: {
    icon: 'mail',
    bgColor: 'bg-blue-100 dark:bg-blue-900/30',
    textColor: 'text-blue-600 dark:text-blue-400',
  },
  news: {
    icon: 'article',
    bgColor: 'bg-green-100 dark:bg-green-900/30',
    textColor: 'text-green-600 dark:text-green-400',
  },
  task: {
    icon: 'task_alt',
    bgColor: 'bg-purple-100 dark:bg-purple-900/30',
    textColor: 'text-purple-600 dark:text-purple-400',
  },
};

export function PriorityItem({ item, onClick }: PriorityItemProps) {
  const config = iconConfig[item.type];

  return (
    <div
      onClick={onClick}
      className="group relative bg-zinc-100 dark:bg-zinc-900 hover:bg-white dark:hover:bg-zinc-800 p-4 rounded-xl transition-all cursor-pointer border border-transparent hover:border-zinc-200 dark:hover:border-zinc-700 hover:shadow-md"
    >
      <div className="flex items-start gap-4">
        <div
          className={`h-10 w-10 rounded-full ${config.bgColor} flex items-center justify-center flex-shrink-0 ${config.textColor}`}
        >
          <span className="material-symbols-outlined text-xl">{config.icon}</span>
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-zinc-900 dark:text-white truncate">
            {item.title}
          </p>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5 truncate">
            {item.subtitle}
          </p>
        </div>
      </div>
    </div>
  );
}
