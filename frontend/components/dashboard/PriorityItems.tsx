'use client';

import { PriorityItem, PriorityItemData } from './PriorityItem';

interface PriorityItemsProps {
  items: PriorityItemData[];
  urgentCount?: number;
  onItemClick?: (item: PriorityItemData) => void;
}

export function PriorityItems({ items, urgentCount = 0, onItemClick }: PriorityItemsProps) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between px-1">
        <h3 className="text-sm font-semibold text-zinc-500 dark:text-zinc-400">
          Priority Items
        </h3>
        {urgentCount > 0 && (
          <span className="text-xs bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 px-2 py-0.5 rounded-full font-medium">
            {urgentCount} urgent
          </span>
        )}
      </div>
      <div className="flex flex-col gap-2">
        {items.map((item) => (
          <PriorityItem
            key={item.id}
            item={item}
            onClick={onItemClick ? () => onItemClick(item) : undefined}
          />
        ))}
      </div>
    </div>
  );
}
