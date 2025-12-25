export function PhoneMockup() {
  return (
    <div className="relative max-w-sm mx-auto mt-12 group">
      <div className="absolute -inset-4 bg-gradient-to-r from-purple-400 to-pink-400 opacity-20 blur-3xl rounded-full dark:opacity-30"></div>
      <div className="relative transition-transform duration-500 hover:scale-105">
        <div className="relative bg-black rounded-[3rem] p-3 shadow-2xl border-4 border-zinc-800">
          <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-1/3 h-6 bg-black rounded-b-2xl z-20"></div>
          <div className="overflow-hidden rounded-[2.5rem] bg-zinc-900 aspect-[9/19.5] relative">
            <div className="absolute inset-0 bg-gradient-to-br from-orange-400 to-pink-500"></div>
            <div className="relative z-10 p-6 flex flex-col h-full text-white">
              <div className="mt-8">
                <p className="text-xs uppercase tracking-wider opacity-70">Daily Brief • Today</p>
                <h3 className="text-3xl font-serif mt-2 leading-tight">Good Morning</h3>
              </div>
              <div className="mt-8 space-y-3">
                <BriefingItem icon="calendar_today" text="4 Events Today" />
                <BriefingItem icon="mail" text="8 New Emails" />
              </div>
              <div className="mt-auto mb-6 bg-white/20 backdrop-blur-xl p-1 rounded-full flex items-center justify-between pl-4 pr-1">
                <span className="text-sm font-medium flex items-center gap-2">
                  <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span> Listening...
                </span>
                <div className="bg-white text-black p-2 rounded-full">
                  <span className="material-symbols-outlined">graphic_eq</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function BriefingItem({ icon, text }: { icon: string; text: string }) {
  return (
    <div className="bg-white/10 backdrop-blur-md p-3 rounded-2xl flex items-center gap-3">
      <div className="bg-white/20 p-2 rounded-lg">
        <span className="material-symbols-outlined text-sm">{icon}</span>
      </div>
      <div className="text-sm font-medium">{text}</div>
    </div>
  );
}
