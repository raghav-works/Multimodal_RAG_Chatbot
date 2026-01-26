"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { login, signup } from "../../lib/api";
import { getToken, setToken } from "../../lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (getToken()) {
      router.replace("/chat");
    }
  }, [router]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signup({ username, email, password });
      const response = await login({ username, password });
      setToken(response.data.access_token);
      router.push("/chat");
    } catch (err) {
      setError("Unable to sign up. Please check your details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-[#f5f3ff] via-[#eef2ff] to-[#fde8f0] px-4">
      <div className="glass-panel w-full max-w-md rounded-3xl p-8">
        <h1 className="text-3xl font-semibold text-slate-900">
          Create account
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Start building your knowledge assistant.
        </p>
        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="text-sm font-medium text-slate-600">
              Username
            </label>
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="mt-2 w-full rounded-full border border-slate-200 bg-white/90 px-4 py-2 text-sm focus:border-brand-500 focus:outline-none"
              placeholder="Choose a username"
              required
            />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-600">Email</label>
            <input
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              className="mt-2 w-full rounded-full border border-slate-200 bg-white/90 px-4 py-2 text-sm focus:border-brand-500 focus:outline-none"
              placeholder="you@email.com"
              required
            />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-600">
              Password
            </label>
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              className="mt-2 w-full rounded-full border border-slate-200 bg-white/90 px-4 py-2 text-sm focus:border-brand-500 focus:outline-none"
              placeholder="Create a password"
              required
            />
          </div>
          {error && (
            <div className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">
              {error}
            </div>
          )}
          <button
            disabled={loading}
            className="w-full rounded-full bg-brand-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-brand-500 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {loading ? "Creating..." : "Sign up"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-slate-500">
          Already have an account?{" "}
          <button
            onClick={() => router.push("/login")}
            className="font-semibold text-brand-600"
          >
            Log in
          </button>
        </p>
      </div>
    </div>
  );
}
