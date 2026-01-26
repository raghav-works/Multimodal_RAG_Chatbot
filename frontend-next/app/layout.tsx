import "./globals.css";

export const metadata = {
  title: "Multimodal RAG Chat",
  description: "ChatGPT-style dashboard for multimodal RAG"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-100 text-slate-900">
        {children}
      </body>
    </html>
  );
}
