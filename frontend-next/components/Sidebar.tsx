"use client";

import React from "react";
import { ChatSession } from "../store/chatStore";

type SidebarProps = {
  chats: ChatSession[];
  activeChatId: string | null;
  onNewChat: () => void;
  onSelect: (chatId: string) => void;
  onDelete: (chatId: string) => void;
  onRename: (chatId: string, title: string) => void;
};

export default function Sidebar({
  chats,
  activeChatId,
  onNewChat,
  onSelect,
  onDelete,
  onRename
}: SidebarProps) {
  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [draftTitle, setDraftTitle] = React.useState("");

  const startEditing = (chatId: string, currentTitle: string) => {
    setEditingId(chatId);
    setDraftTitle(currentTitle);
  };

  const stopEditing = () => {
    setEditingId(null);
    setDraftTitle("");
  };

  const commitTitle = (chatId: string) => {
    const trimmed = draftTitle.trim();
    if (trimmed) {
      onRename(chatId, trimmed);
    }
    stopEditing();
  };

  return (
    <aside className="flex h-full w-full flex-col border-r border-white/50 bg-white/60 p-4 shadow-soft backdrop-blur">
      <button
        onClick={onNewChat}
        className="rounded-2xl bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-500"
      >
        New Chat
      </button>
      <div className="mt-4 flex-1 overflow-y-auto pr-1 scrollbar-thin">
        {chats.length === 0 ? (
          <p className="text-sm text-slate-500">No chats yet.</p>
        ) : (
          <ul className="space-y-2">
            {chats.map((chat) => {
              const isActive = chat.chat_id === activeChatId;
              const isEditing = editingId === chat.chat_id;
              return (
                <li
                  key={chat.chat_id}
                  className={`group flex items-center justify-between gap-2 rounded-2xl border px-3 py-2 text-sm transition ${
                    isActive
                      ? "border-brand-500/40 bg-white/80 text-brand-700 shadow-sm"
                      : "border-transparent hover:bg-white/80"
                  }`}
                >
                  {isEditing ? (
                    <input
                      value={draftTitle}
                      onChange={(event) => setDraftTitle(event.target.value)}
                      onBlur={() => commitTitle(chat.chat_id)}
                      onKeyDown={(event) => {
                        if (event.key === "Enter") {
                          commitTitle(chat.chat_id);
                        }
                        if (event.key === "Escape") {
                          stopEditing();
                        }
                      }}
                      className="flex-1 rounded-lg border border-slate-200 bg-white/90 px-2 py-1 text-sm text-slate-700 focus:border-brand-500 focus:outline-none"
                      autoFocus
                    />
                  ) : (
                    <button
                      onClick={() => onSelect(chat.chat_id)}
                      className="flex-1 truncate text-left"
                    >
                      {chat.title || "New Chat"}
                    </button>
                  )}
                  <button
                    onClick={() => startEditing(chat.chat_id, chat.title || "")}
                    className="rounded-full p-1 text-slate-400 transition hover:bg-white hover:text-slate-600"
                    aria-label="Rename chat"
                    title="Rename chat"
                  >
                    ✎
                  </button>
                  <button
                    onClick={() => onDelete(chat.chat_id)}
                    className="rounded-full p-1 text-slate-400 transition hover:bg-white hover:text-slate-600"
                    aria-label="Delete chat"
                    title="Delete chat"
                  >
                    ✖
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
      <p className="mt-4 text-xs text-slate-400">Multimodal RAG Chat</p>
    </aside>
  );
}
