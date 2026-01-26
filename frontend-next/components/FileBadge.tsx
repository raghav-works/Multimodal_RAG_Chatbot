"use client";

type FileBadgeProps = {
  filename: string;
  onRemove: () => void;
  icon?: string;
};

export default function FileBadge({
  filename,
  onRemove,
  icon = "📄"
}: FileBadgeProps) {
  return (
    <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-xs text-slate-600 shadow-sm">
      <span role="img" aria-label="file">
        {icon}
      </span>
      <span className="max-w-[180px] truncate">{filename}</span>
      <button
        onClick={onRemove}
        className="rounded-full px-1 text-slate-400 transition hover:text-slate-600"
      >
        ✖
      </button>
    </div>
  );
}
