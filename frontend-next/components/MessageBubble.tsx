"use client";

import { Message } from "../store/chatStore";

type MessageBubbleProps = {
  message: Message;
};

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[70%] rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 shadow-sm ${
          isUser ? "text-slate-800" : "text-slate-700"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}
