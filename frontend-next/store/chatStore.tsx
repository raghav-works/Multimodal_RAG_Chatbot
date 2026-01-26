"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useReducer,
  useState
} from "react";

export type Role = "user" | "assistant";

export type Message = {
  role: Role;
  content: string;
};

export type ChatSession = {
  chat_id: string;
  title: string;
  document_id?: string | null;
  filename?: string | null;
  imageFile?: File | null;
  imageFilename?: string | null;
  messages: Message[];
};

type ChatState = {
  chats: ChatSession[];
  activeChatId: string | null;
};

type Action =
  | { type: "LOAD_STATE"; payload: ChatState }
  | { type: "CREATE_CHAT"; payload: { chat: ChatSession } }
  | { type: "DELETE_CHAT"; payload: { chatId: string } }
  | { type: "SET_ACTIVE"; payload: { chatId: string } }
  | {
      type: "ADD_MESSAGE";
      payload: { chatId: string; message: Message };
    }
  | {
      type: "RENAME_CHAT";
      payload: { chatId: string; title: string };
    }
  | {
      type: "SET_DOCUMENT";
      payload: { chatId: string; documentId: string; filename: string };
    }
  | { type: "CLEAR_DOCUMENT"; payload: { chatId: string } }
  | {
      type: "SET_IMAGE";
      payload: { chatId: string; image: File | null; filename: string | null };
    };

const initialState: ChatState = {
  chats: [],
  activeChatId: null
};

const createId = () => {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `chat_${Date.now()}_${Math.random().toString(16).slice(2)}`;
};

const reducer = (state: ChatState, action: Action): ChatState => {
  switch (action.type) {
    case "LOAD_STATE":
      return action.payload;
    case "CREATE_CHAT":
      return {
        chats: [action.payload.chat, ...state.chats],
        activeChatId: action.payload.chat.chat_id
      };
    case "DELETE_CHAT": {
      const remaining = state.chats.filter(
        (chat) => chat.chat_id !== action.payload.chatId
      );
      const activeChatId =
        state.activeChatId === action.payload.chatId
          ? remaining[0]?.chat_id ?? null
          : state.activeChatId;
      return { chats: remaining, activeChatId };
    }
    case "SET_ACTIVE":
      return { ...state, activeChatId: action.payload.chatId };
    case "ADD_MESSAGE":
      return {
        ...state,
        chats: state.chats.map((chat) => {
          if (chat.chat_id !== action.payload.chatId) return chat;
          const messages = [...chat.messages, action.payload.message];
          const title =
            chat.title === "New Chat" && action.payload.message.role === "user"
              ? action.payload.message.content.slice(0, 38)
              : chat.title;
          return { ...chat, messages, title };
        })
      };
    case "RENAME_CHAT":
      return {
        ...state,
        chats: state.chats.map((chat) =>
          chat.chat_id === action.payload.chatId
            ? { ...chat, title: action.payload.title }
            : chat
        )
      };
    case "SET_DOCUMENT":
      return {
        ...state,
        chats: state.chats.map((chat) =>
          chat.chat_id === action.payload.chatId
            ? {
                ...chat,
                document_id: action.payload.documentId,
                filename: action.payload.filename
              }
            : chat
        )
      };
    case "CLEAR_DOCUMENT":
      return {
        ...state,
        chats: state.chats.map((chat) =>
          chat.chat_id === action.payload.chatId
            ? { ...chat, document_id: null, filename: null }
            : chat
        )
      };
    case "SET_IMAGE":
      return {
        ...state,
        chats: state.chats.map((chat) =>
          chat.chat_id === action.payload.chatId
            ? {
                ...chat,
                imageFile: action.payload.image,
                imageFilename: action.payload.filename
              }
            : chat
        )
      };
    default:
      return state;
  }
};

type ChatContextValue = {
  state: ChatState;
  createChat: () => string;
  deleteChat: (chatId: string) => void;
  setActiveChat: (chatId: string) => void;
  addMessage: (chatId: string, message: Message) => void;
  renameChat: (chatId: string, title: string) => void;
  setDocument: (chatId: string, documentId: string, filename: string) => void;
  clearDocument: (chatId: string) => void;
  setImage: (chatId: string, image: File | null) => void;
  clearImage: (chatId: string) => void;
  setStorageKey: (username: string) => void;
};

const ChatContext = createContext<ChatContextValue | undefined>(undefined);

const isBrowser = () => typeof window !== "undefined";

const serializeState = (state: ChatState) => ({
  chats: state.chats.map((chat) => ({
    ...chat,
    imageFile: null
  })),
  activeChatId: state.activeChatId
});

export const ChatProvider = ({ children }: { children: React.ReactNode }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [storageKey, setStorageKeyState] = useState<string | null>(null);

  const createChat = () => {
    const newChat: ChatSession = {
      chat_id: createId(),
      title: "New Chat",
      messages: [],
      document_id: null,
      filename: null,
      imageFile: null,
      imageFilename: null
    };
    dispatch({ type: "CREATE_CHAT", payload: { chat: newChat } });
    return newChat.chat_id;
  };

  useEffect(() => {
    if (!storageKey || !isBrowser()) return;
    const raw = window.localStorage.getItem(storageKey);
    if (!raw) return;
    try {
      const parsed = JSON.parse(raw) as ChatState;
      if (parsed && Array.isArray(parsed.chats)) {
        dispatch({
          type: "LOAD_STATE",
          payload: {
            chats: parsed.chats.map((chat) => ({
              ...chat,
              imageFile: null
            })),
            activeChatId: parsed.activeChatId ?? null
          }
        });
      }
    } catch {
      // Ignore corrupted storage entries.
    }
  }, [storageKey]);

  useEffect(() => {
    if (!storageKey || !isBrowser()) return;
    const serialized = serializeState(state);
    window.localStorage.setItem(storageKey, JSON.stringify(serialized));
  }, [state, storageKey]);

  const value = useMemo(
    () => ({
      state,
      createChat,
      deleteChat: (chatId: string) =>
        dispatch({ type: "DELETE_CHAT", payload: { chatId } }),
      setActiveChat: (chatId: string) =>
        dispatch({ type: "SET_ACTIVE", payload: { chatId } }),
      addMessage: (chatId: string, message: Message) =>
        dispatch({ type: "ADD_MESSAGE", payload: { chatId, message } }),
      renameChat: (chatId: string, title: string) =>
        dispatch({ type: "RENAME_CHAT", payload: { chatId, title } }),
      setDocument: (chatId: string, documentId: string, filename: string) =>
        dispatch({
          type: "SET_DOCUMENT",
          payload: { chatId, documentId, filename }
        }),
      clearDocument: (chatId: string) =>
        dispatch({ type: "CLEAR_DOCUMENT", payload: { chatId } }),
      setImage: (chatId: string, image: File | null) =>
        dispatch({
          type: "SET_IMAGE",
          payload: { chatId, image, filename: image?.name ?? null }
        }),
      clearImage: (chatId: string) =>
        dispatch({
          type: "SET_IMAGE",
          payload: { chatId, image: null, filename: null }
        }),
      setStorageKey: (username: string) =>
        setStorageKeyState(`rag_chat_state_${username}`)
    }),
    [state]
  );

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChatStore = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChatStore must be used within ChatProvider");
  }
  return context;
};
