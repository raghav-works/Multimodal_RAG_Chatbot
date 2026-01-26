"use client";

type TopBarProps = {
  username: string;
  onLogout: () => void;
};

export default function TopBar({ username, onLogout }: TopBarProps) {
  return (
    <header className="flex items-center justify-between border-b border-white/60 bg-white/70 px-6 py-4 backdrop-blur">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
          Multimodal RAG Dashboard
        </h1>
        <p className="text-xs text-slate-500">ChatGPT-style workspace</p>
      </div>
      <details className="group relative">
        <summary className="flex cursor-pointer list-none items-center gap-2 rounded-full bg-white/70 px-3 py-1.5 text-sm text-slate-600 shadow-sm transition hover:bg-white/90">
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-600/10 text-brand-600">
            {username.slice(0, 1).toUpperCase()}
          </span>
          <span className="text-sm text-slate-700">{username}</span>
          <span className="text-slate-400">▾</span>
        </summary>
        <div className="absolute right-0 mt-2 w-40 rounded-2xl border border-white/80 bg-white/90 p-2 text-sm text-slate-600 shadow-soft backdrop-blur">
          <button
            onClick={onLogout}
            className="w-full rounded-xl px-3 py-2 text-left transition hover:bg-slate-100/80"
          >
            Logout
          </button>
        </div>
      </details>
    </header>
  );
}
