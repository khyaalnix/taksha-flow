'use client';

interface IntegrationCardProps {
  icon: string;
  iconBg: string;
  iconColor: string;
  title: string;
  description: string;
  status: 'available' | 'connected' | 'coming-soon';
  statusText: string;
  statusColor: string;
  onConnect?: () => void;
  customIcon?: React.ReactNode;
}

export function IntegrationCard({
  icon,
  iconBg,
  iconColor,
  title,
  description,
  status,
  statusText,
  statusColor,
  onConnect,
  customIcon,
}: IntegrationCardProps) {
  const isComingSoon = status === 'coming-soon';
  const isConnected = status === 'connected';
  const isAvailable = status === 'available';

  return (
    <div
      className={`group relative rounded-2xl p-6 transition-all duration-300 flex flex-col justify-between h-full ${
        isComingSoon
          ? 'bg-zinc-50 dark:bg-zinc-900/50 border border-dashed border-zinc-300 dark:border-zinc-700 opacity-75 hover:opacity-100'
          : 'bg-white dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 hover:shadow-xl dark:hover:shadow-[0_0_40px_-10px_rgba(234,88,12,0.2)]'
      }`}
    >
      {isConnected && (
        <div className="absolute top-4 right-4">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
            Connected
          </span>
        </div>
      )}

      {isComingSoon && (
        <div className="absolute top-4 right-4">
          <span className="text-[10px] font-bold uppercase tracking-wider bg-zinc-200 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 px-2 py-1 rounded">
            Soon
          </span>
        </div>
      )}

      <div>
        <div
          className={`w-12 h-12 ${iconBg} rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}
        >
          {customIcon || (
            <span className={`material-symbols-outlined ${iconColor} text-2xl`}>{icon}</span>
          )}
        </div>
        <h3 className="text-xl font-semibold text-zinc-900 dark:text-white mb-2">{title}</h3>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed mb-6">
          {description}
        </p>
      </div>

      <div>
        <div className="flex items-center gap-2 mb-4">
          <span className={`flex h-2 w-2 rounded-full ${statusColor}`}></span>
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">{statusText}</span>
        </div>

        {isAvailable && (
          <button
            onClick={onConnect}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 border border-zinc-300 dark:border-zinc-600 rounded-lg text-sm font-medium text-zinc-700 dark:text-zinc-200 hover:bg-zinc-50 dark:hover:bg-zinc-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors"
          >
            Connect {title}
          </button>
        )}

        {isConnected && (
          <button
            onClick={onConnect}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-zinc-100 dark:bg-zinc-800 border border-transparent rounded-lg text-sm font-medium text-zinc-500 dark:text-zinc-400 hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
          >
            Disconnect
          </button>
        )}

        {isComingSoon && (
          <button
            disabled
            className="w-full py-2.5 px-4 border border-transparent rounded-lg text-sm font-medium text-zinc-400 dark:text-zinc-600 cursor-not-allowed"
          >
            Coming Soon
          </button>
        )}
      </div>
    </div>
  );
}
