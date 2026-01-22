'use client';

interface PermissionCardProps {
  id: string;
  icon: string;
  iconBg: string;
  iconColor: string;
  title: string;
  description: string;
  statusText: string;
  statusColor: string;
}

export function PermissionCard({
  icon,
  iconBg,
  iconColor,
  title,
  description,
  statusText,
  statusColor,
}: PermissionCardProps) {
  return (
    <div className="bg-white dark:bg-zinc-900/50 backdrop-blur-xl border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 transition-all hover:border-zinc-300 dark:hover:border-zinc-700 hover:shadow-lg">
      {/* Icon */}
      <div className={`w-12 h-12 rounded-xl ${iconBg} flex items-center justify-center mb-4`}>
        <span className={`material-symbols-outlined text-2xl ${iconColor}`}>
          {icon}
        </span>
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-white mb-2">
        {title}
      </h3>

      {/* Description */}
      <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4 leading-relaxed">
        {description}
      </p>

      {/* Status */}
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${statusColor}`}></div>
        <span className="text-xs text-zinc-500 dark:text-zinc-500">
          {statusText}
        </span>
      </div>
    </div>
  );
}
