"use client";
import { useState } from "react";
import UnifiedSummarizeForm from "./components/UnifiedSummarizeForm";
import SummaryList from "./components/SummaryList";

export default function Home() {
  // 要約結果（配列）
  const [summaries, setSummaries] = useState<{ id: number; content: string }[]>([]);

  // フォームから受け取るコールバック：結果をリストに追加
  const handleNewSummary = (content: string) => {
    setSummaries((prev) => [...prev, { id: Date.now(), content }]);
  };

  // リストからの削除
  const handleDelete = (id: number) => {
    setSummaries((prev) => prev.filter((s) => s.id !== id));
  };

  return (
    <div className="flex flex-col min-h-screen">   {/* ← 全体をflex縦並び */}

      {/* 上段：入力フォーム */}
      <main className="p-8 flex flex-col items-center">
        <h1 className="text-2xl font-bold mb-8 text-center">
          ニュース記事要約（統合フォーム）
        </h1>
        <UnifiedSummarizeForm onNewSummary={handleNewSummary} />
      </main>

      {/* 下段：結果表示エリア → 残り全体を覆う */}
      <section className="flex-grow w-full bg-gray-100 py-2 pb-6">
        <SummaryList summaries={summaries} onDelete={handleDelete} />
      </section>

    </div>
  );
}
