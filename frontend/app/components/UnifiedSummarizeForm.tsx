"use client";
import { useEffect, useState } from "react";

/**
 * 入出力とAPI呼び分けを行うフォーム。
 * - 入力：text / url / targetLang / length
 * - 出力：onNewSummary(summaryText) で親に結果を渡す
 * - ルーティング：
 *   - targetLang が ja/en 以外 → /summarizer/summarize/ を1発（翻訳含む）
 *   - targetLang が ja/en → 既存フロー（/api/extract_article → /api/summarize, または /api/summarize）
 * 注：/api/* は Next.js 側の既存ルート（あなたの現在の実装）を尊重している。
 */
export default function UnifiedSummarizeForm({
  onNewSummary,
}: {
  onNewSummary: (summary: string) => void;
}) {
  // ---- 入力状態 ----
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");

  const [targetLang, setTargetLang] = useState("ja"); // 出力言語
  const [length, setLength] = useState<"short" | "medium" | "long">("medium");

  // ---- 表示状態 ----
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  // モードを localStorage に保存/復元（従来の挙動を踏襲）
  useEffect(() => {
    const saved = localStorage.getItem("summaryMode");
    if (saved === "short" || saved === "medium" || saved === "long") {
      setLength(saved);
    }
  }, []);
  useEffect(() => {
    localStorage.setItem("summaryMode", length);
  }, [length]);

  // ja/en 以外なら v2 を使う（簡易ルール）
  const shouldUseV2 = true;

  // 送信
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!text.trim() && !url.trim()) {
      setError("本文または記事URLを入力すべきである。");
      return;
    }

    setLoading(true);
    try {
      if (shouldUseV2) {
        // ---- 多言語（翻訳が絡む）→ v2 を直接叩く ----
        const payload: any = { target_lang: targetLang, length };
        if (text.trim()) payload.text = text.trim();
        if (url.trim()) payload.url = url.trim();

        const res = await fetch("http://localhost:8000/summarizer/summarize/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error(`サーバーエラー: ${res.status}`);
        const data = await res.json();
        onNewSummary(data.summary ?? "");
        return;
      }

      // ---- 英/日 → 既存の v1 フローを維持 ----
      // 1) URLがあれば /api/extract_article で抽出
      let sourceText = text.trim();
      const isUrl = url.startsWith("http://") || url.startsWith("https://");
      if (!sourceText && isUrl) {
        const r1 = await fetch("/api/extract_article", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url }),
        });
        if (!r1.ok) throw new Error("記事本文を取得できなかった。");
        const d1 = await r1.json();
        sourceText = (d1.article || "").trim();
        if (!sourceText) throw new Error("抽出結果が空である。");
      }

      // 2) /api/summarize で要約
      const r2 = await fetch("/api/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: sourceText, mode: length }),
      });
      if (!r2.ok) {
        const msg = await r2.text();
        throw new Error(msg || "Server Error occurred.");
      }
      const d2 = await r2.json();
      onNewSummary(d2.summary ?? "");
    } catch (err: any) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col items-center w-full space-y-4">

        {/* 原文入力テキストエリア */}
        <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={6}
            className="border p-3 w-4/5 max-w-3xl"
            placeholder="記事本文を入力（URLとどちらか一方でよい）"
        />

        {/* URL入力（ラベルと横並び） */}
        <div className="flex items-center w-4/5 max-w-3xl space-x-2">
            <label className="font-semibold whitespace-nowrap">記事URL：</label>
            <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="border p-2 flex-grow"
            placeholder="https://example.com/news/123"
            />
        </div>

        {/* 出力言語・出力長さ・要約ボタン */}
        <div className="flex items-center w-4/5 max-w-3xl space-x-6">

            {/* 出力言語 */}
            <div className="flex items-center space-x-2">
            <label className="font-semibold whitespace-nowrap">出力言語：</label>
            <select
                value={targetLang}
                onChange={(e) => setTargetLang(e.target.value)}
                className="border p-2"
            >
                <option value="ja">日本語</option>
                <option value="en">英語</option>
                <option value="fr">フランス語</option>
                <option value="es">スペイン語</option>
                <option value="zh">中国語</option>
            </select>
            </div>

            {/* 出力の長さ */}
            <div className="flex items-center space-x-4">
                <span className="font-semibold whitespace-nowrap">出力の長さ：</span>
                <label className="flex items-center gap-1 cursor-pointer">
                <input
                    type="radio"
                    name="mode"
                    value="short"
                    checked={length === "short"}
                    onChange={() => setLength("short")}
                />
                <span>短め</span>
                </label>
                <label className="flex items-center gap-1 cursor-pointer">
                <input
                    type="radio"
                    name="mode"
                    value="medium"
                    checked={length === "medium"}
                    onChange={() => setLength("medium")}
                />
                <span>普通</span>
                </label>
                <label className="flex items-center gap-1 cursor-pointer">
                <input
                    type="radio"
                    name="mode"
                    value="long"
                    checked={length === "long"}
                    onChange={() => setLength("long")}
                />
                <span>長め</span>
                </label>
            </div>

            {/* 要約ボタン */}
            <button
            type="submit"
            disabled={loading}
            className="mx-auto bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
            >
            {loading ? "要約中..." : "要約"}
            </button>

        </div>

        {/* エラー表示 */}
        {error && <div className="mt-2 text-red-600 w-4/5 max-w-3xl">{error}</div>}
    </form>

  );
}
