"use client";

import { Message } from "../store/chatStore";
import MessageBubble from "./MessageBubble";

type ChatWindowProps = {
  messages: Message[];
  username: string;
  isTyping: boolean;
};

export default function ChatWindow({
  messages,
  username,
  isTyping
}: ChatWindowProps) {
  return (
    <div className="flex h-full flex-col gap-4 overflow-y-auto px-6 py-6 scrollbar-thin">
      {messages.length === 0 ? (
        <div className="rounded-3xl border border-slate-200 bg-white/80 p-10 text-center shadow-soft">
          <p className="text-lg font-semibold text-slate-800">
            Hi {username}, how can I assist you today?
          </p>
          <p className="mt-2 text-sm text-slate-500">
            Upload a document, ask a question, or try image-based queries.
          </p>
        </div>
      ) : (
        messages.map((message, index) => (
          <MessageBubble key={`${message.role}-${index}`} message={message} />
        ))
      )}
      {isTyping && (
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <span className="h-2 w-2 animate-bounce rounded-full bg-slate-300" />
          <span className="h-2 w-2 animate-bounce rounded-full bg-slate-300 [animation-delay:120ms]" />
          <span className="h-2 w-2 animate-bounce rounded-full bg-slate-300 [animation-delay:240ms]" />
          <span>Assistant is typing…</span>
        </div>
      )}
    </div>
  );
}
