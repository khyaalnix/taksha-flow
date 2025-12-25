import Link from 'next/link';

export function CTASection() {
  return (
    <section className="py-24 bg-primary dark:bg-orange-900 relative overflow-hidden">
      <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-orange-400 dark:bg-orange-700 rounded-full blur-3xl opacity-30"></div>
      <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-80 h-80 bg-purple-400 dark:bg-purple-700 rounded-full blur-3xl opacity-30"></div>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
        <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
          Ready for your personalized companion?
        </h2>
        <p className="text-orange-100 text-lg mb-10 max-w-2xl mx-auto">
          Start your day with a briefing that knows you, adapts to you, and grows with you. Join thousands of users today.
        </p>
        <Link
          href="/login"
          className="inline-block bg-white text-primary dark:text-orange-900 px-10 py-4 rounded-full font-bold text-base hover:shadow-2xl hover:bg-zinc-50 transition-all transform hover:-translate-y-1"
        >
          Start listening
        </Link>
      </div>
    </section>
  );
}
