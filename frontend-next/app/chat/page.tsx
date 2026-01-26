"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "../../components/Sidebar";
import TopBar from "../../components/TopBar";
import ChatWindow from "../../components/ChatWindow";
import FileBadge from "../../components/FileBadge";
import { ChatProvider, useChatStore } from "../../store/chatStore";
import {
  deleteDocument,
  imageQuery,
  me,
  queryDocument,
  uploadDocument
} from "../../lib/api";
import { clearToken, getToken } from "../../lib/auth";

function ChatDashboard() {
  const router = useRouter();
  const {
    state,
    createChat,
    setActiveChat,
    deleteChat,
    addMessage,
    setDocument,
    clearDocument,
    setImage,
    clearImage,
    renameChat,
    setStorageKey
  } = useChatStore();
  const [username, setUsername] = useState("User");
  const [messageInput, setMessageInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [warning, setWarning] = useState("");
  const [uploading, setUploading] = useState(false);
  const documentInputRef = useRef<HTMLInputElement | null>(null);
  const imageInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    me()
      .then((response) => {
        setUsername(response.data.username);
        setStorageKey(response.data.username);
      })
      .catch(() => {
        clearToken();
        router.replace("/login");
      });
  }, [router]);

  useEffect(() => {
    if (state.chats.length === 0) {
      createChat();
    }
  }, [state.chats.length, createChat]);

  const activeChat = useMemo(
    () => state.chats.find((chat) => chat.chat_id === state.activeChatId),
    [state.chats, state.activeChatId]
  );

  const handleNewChat = () => {
    createChat();
  };

  const handleDeleteChat = async (chatId: string) => {
    const chat = state.chats.find((item) => item.chat_id === chatId);
    if (chat?.document_id) {
      await deleteDocument({ document_id: chat.document_id });
    }
    deleteChat(chatId);
  };

  const handleSend = async () => {
    if (!activeChat || !messageInput.trim()) return;
    if (!activeChat.imageFile && !activeChat.document_id) {
      setWarning("Please upload a document first");
      return;
    }
    setWarning("");
    const question = messageInput.trim();
    setMessageInput("");
    addMessage(activeChat.chat_id, { role: "user", content: question });
    setIsTyping(true);

    try {
      if (activeChat.imageFile) {
        const response = await imageQuery(activeChat.imageFile, question);
        addMessage(activeChat.chat_id, {
          role: "assistant",
          content: response.data.answer
        });
        clearImage(activeChat.chat_id);
      } else if (activeChat.document_id) {
        const response = await queryDocument({
          document_id: activeChat.document_id,
          question
        });
        addMessage(activeChat.chat_id, {
          role: "assistant",
          content: response.data.answer
        });
      }
    } catch (error) {
      addMessage(activeChat.chat_id, {
        role: "assistant",
        content: "Something went wrong. Please try again."
      });
    } finally {
      setIsTyping(false);
    }
  };

  const handleDocumentUpload = async (file: File) => {
    if (!activeChat) return;
    setUploading(true);
    try {
      const response = await uploadDocument(file);
      setDocument(activeChat.chat_id, response.data.document_id, file.name);
      setWarning("");
    } finally {
      setUploading(false);
    }
  };

  const handleImageUpload = (file: File) => {
    if (!activeChat) return;
    setImage(activeChat.chat_id, file);
    setWarning("");
  };

  const handleRemoveDocument = async () => {
    if (!activeChat?.document_id) return;
    try {
      await deleteDocument({ document_id: activeChat.document_id });
    } catch {
      // Ignore delete errors to keep UI responsive.
    }
    clearDocument(activeChat.chat_id);
  };

  const handleRemoveImage = () => {
    if (!activeChat) return;
    clearImage(activeChat.chat_id);
  };

  return (
    <div className="flex h-screen gap-6 p-6">
      <div className="w-72 shrink-0 overflow-hidden rounded-3xl">
        <Sidebar
          chats={state.chats}
          activeChatId={state.activeChatId}
          onNewChat={handleNewChat}
          onSelect={setActiveChat}
          onDelete={handleDeleteChat}
          onRename={renameChat}
        />
      </div>
      <div className="flex flex-1 flex-col gap-4">
        <TopBar
          username={username}
          onLogout={() => {
            clearToken();
            router.replace("/login");
          }}
        />
        <main className="flex flex-1 flex-col overflow-hidden rounded-3xl border border-white/70 bg-white/60 shadow-soft backdrop-blur">
          <div className="flex items-center justify-between border-b border-white/60 bg-white/70 px-6 py-3">
            <div className="flex items-center gap-3">
              {activeChat?.filename && (
                <FileBadge
                  filename={activeChat.filename}
                  onRemove={handleRemoveDocument}
                />
              )}
              {activeChat?.imageFilename && (
                <FileBadge
                  filename={activeChat.imageFilename}
                  onRemove={handleRemoveImage}
                  icon="🖼️"
                />
              )}
            </div>
            {uploading && (
              <span className="text-xs text-slate-500">Uploading...</span>
            )}
          </div>
          <div className="flex-1 overflow-hidden">
            <ChatWindow
              messages={activeChat?.messages ?? []}
              username={username}
              isTyping={isTyping}
            />
          </div>
          <div className="border-t border-white/60 bg-white/70 px-6 py-4">
            {warning && (
              <div className="mb-3 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-600">
                {warning}
              </div>
            )}
            <div className="flex items-center gap-3">
              <input
                ref={documentInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                className="hidden"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) {
                    handleDocumentUpload(file);
                    event.target.value = "";
                  }
                }}
              />
              <input
                ref={imageInputRef}
                type="file"
                accept=".png,.jpg,.jpeg"
                className="hidden"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) {
                    handleImageUpload(file);
                    event.target.value = "";
                  }
                }}
              />
              <button
                onClick={() => documentInputRef.current?.click()}
                className="rounded-full border border-slate-200 bg-white/80 px-4 py-2 text-sm text-slate-600 shadow-sm transition hover:bg-white"
              >
                Upload Doc
              </button>
              <button
                onClick={() => imageInputRef.current?.click()}
                className="rounded-full border border-slate-200 bg-white/80 px-4 py-2 text-sm text-slate-600 shadow-sm transition hover:bg-white"
              >
                Upload Image
              </button>
              <input
                value={messageInput}
                onChange={(event) => setMessageInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Type your message..."
                className="flex-1 rounded-full border border-slate-200 bg-white/90 px-4 py-3 text-sm shadow-sm focus:border-brand-500 focus:outline-none"
              />
              <button
                onClick={handleSend}
                className="rounded-full bg-brand-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-500"
              >
                Send
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <ChatProvider>
      <ChatDashboard />
    </ChatProvider>
  );
}
