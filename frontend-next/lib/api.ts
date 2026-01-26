import axios from "axios";
import { getToken } from "./auth";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const signup = (payload: {
  username: string;
  email: string;
  password: string;
}) => api.post("/signup", payload);

export const login = (payload: { username: string; password: string }) =>
  api.post("/login", payload);

export const me = () => api.get("/me");

export const uploadDocument = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
};

export const queryDocument = (payload: {
  document_id: string;
  question: string;
}) => api.post("/query", payload);

export const imageQuery = (image: File, question: string) => {
  const formData = new FormData();
  formData.append("image", image);
  formData.append("question", question);
  return api.post("/image_query", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
};

export const deleteDocument = (payload: { document_id: string }) =>
  api.post("/delete_document", payload);

export default api;
