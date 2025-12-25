import Link from 'next/link';

interface FeatureCardProps {
  emoji: string;
  title: string;
  description: string;
  ctaText: string;
  ctaHref?: string;
}

export function FeatureCard({
  emoji,
  title,
  description,
  ctaText,
  ctaHref = '/login',
}: FeatureCardProps) {
  return (
    <div className="p-8 rounded-3xl border border-zinc-100 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/50 hover:border-zinc-300 dark:hover:border-zinc-700 transition-all duration-300">
      <div className="w-12 h-12 bg-white dark:bg-zinc-800 rounded-2xl flex items-center justify-center mb-6 shadow-sm text-2xl">
        {emoji}
      </div>
      <h3 className="text-xl font-bold mb-3 text-zinc-900 dark:text-white">{title}</h3>
      <p className="text-zinc-600 dark:text-zinc-400 text-sm leading-relaxed mb-6">
        {description}
      </p>
      <Link
        href={ctaHref}
        className="inline-flex items-center text-sm font-bold bg-black text-white px-4 py-2 rounded-full hover:bg-zinc-800 transition-colors"
      >
        {ctaText}
      </Link>
    </div>
  );
}
