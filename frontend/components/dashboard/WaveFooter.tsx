'use client';

export function WaveFooter() {
  return (
    <footer className="fixed bottom-0 left-0 right-0 p-4 pointer-events-none z-0">
      <div className="max-w-7xl mx-auto flex justify-center opacity-20 dark:opacity-10">
        <svg
          className="w-full h-32"
          preserveAspectRatio="none"
          viewBox="0 0 1440 320"
        >
          <path
            d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,224C672,245,768,267,864,261.3C960,256,1056,224,1152,197.3C1248,171,1344,149,1392,138.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            fill="#6366f1"
            fillOpacity="1"
          />
        </svg>
      </div>
    </footer>
  );
}
