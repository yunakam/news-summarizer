"use client";
import { useState } from "react";

/**
 * 入出力とAPI呼び分けを行うフォーム。
    何をする：結果リストの表示とコピー/削除のみ担当する（ロジック分離）。
    親（page.tsx）から summaries とハンドラを受け取る。
 */

export default function SummaryList({
  summaries,
  onDelete,
}: {
  summaries: { id: number; content: string }[];
  onDelete: (id: number) => void;
}) {
  const [copiedId, setCopiedId] = useState<number | null>(null);

  const handleCopy = (id: number, content: string) => {
    navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <section className="w-full bg-gray-100 py-4">
      <div className="flex flex-col items-center">
        {summaries.map((s) => (
          <div
            key={s.id}
            className="relative mt-6 p-4 border-2 rounded bg-white w-4/5 max-w-3xl"
          >
            {/* 右外のボタン群 */}
            <div className="absolute top-2 -right-8 flex flex-col gap-2">
              <button
                onClick={() => onDelete(s.id)}
                className="text-gray-500 hover:text-red-500"
                aria-label="削除"
              >
                ✕
              </button>
              <button
                onClick={() => handleCopy(s.id, s.content)}
                className="text-blue-600 hover:text-blue-800 text-sm"
                aria-label="コピー"
              >
                📋
                {copiedId === s.id && (
                  <span className="absolute left-full ml-2 text-xs text-pink-600 whitespace-nowrap">
                    Copied!
                  </span>
                )}
              </button>
            </div>

            <p className="whitespace-pre-wrap">{s.content}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
