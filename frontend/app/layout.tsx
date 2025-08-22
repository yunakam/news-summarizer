import type { Metadata } from "next";
import "./styles/global.css";

export const metadata: Metadata = {
  title: "News Summarizer",
  description: "Summarize news articles using Django backend",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
