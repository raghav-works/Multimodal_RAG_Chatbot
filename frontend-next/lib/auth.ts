const TOKEN_KEY = "rag_chat_token";

export const isBrowser = () => typeof window !== "undefined";

export const getToken = () => {
  if (!isBrowser()) return null;
  return window.localStorage.getItem(TOKEN_KEY);
};

export const setToken = (token: string) => {
  if (!isBrowser()) return;
  window.localStorage.setItem(TOKEN_KEY, token);
};

export const clearToken = () => {
  if (!isBrowser()) return;
  window.localStorage.removeItem(TOKEN_KEY);
};
