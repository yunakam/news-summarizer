"use client";
import { useEffect, useState } from "react";

export default function Home() {

    // 入力テキストの状態
    const [text, setText] = useState<string>("");
    // 要約結果の状態（複数保持）
    const [summaries, setSummaries] = useState<
        { id: number; content: string}[]
    >([]);

    // モードの状態（短め=short / 普通=medium / 長め=long）※デフォルトはMedium
    const [mode, setMode] = useState<"short" | "medium" | "long">("medium");

    useEffect(() => {
        // ページ初期表示時に localStorage を確認
        const savedMode = localStorage.getItem("summaryMode");
        if (savedMode === "short" || savedMode === "medium" || savedMode === "long") {
            setMode(savedMode);
        }
    }, []);

    // mode が変わったら localStorage に保存
    useEffect(() => {
        localStorage.setItem("summaryMode", mode);
    }, [mode]);

    // 送信中フラグ（任意）
    const [loading, setLoading] = useState(false);
    // エラーメッセージ（任意）
    const [error, setError] = useState<string>("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try{
        // フォーム送信時に呼び出され、/api/summarize/route.tsにPOSTされる
        const res = await fetch("/api/summarize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, mode }),
        });
        
            if (!res.ok) {
                const msg = await res.text();
                throw new Error(msg || "Server Error occurred.");
            }
            const data = await res.json();

            // 新しい要約をリストに追加
            setSummaries((prev) => [
                ...prev,
                { id: Date.now(), content: data.summary },
            ]);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown Error");
        } finally {
            setLoading(false);
        }
    };

    // アウトプットをクリップボードにコピー

    const [copiedId, setCopiedId] = useState<number |null>(null);

    const handleCopy = (id: number, content: string) => {
        navigator.clipboard.writeText(content);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000)
    };

    // アウトプットを削除
    const handleDelete = (id: number) => {
        setSummaries((prev) => prev.filter((s) => s.id !== id));
    }

    return (
        <>
        <main className="p-8 flex flex-col items-center">
                
            {/* タイトル */}
            <h1 className="text-2xl font-bold mb-8 text-center">ニュース記事翻訳デモ</h1>

            {/* 入力フォーム */}
            <form onSubmit={handleSubmit} className="flex flex-col items-center w-full">

                {/* 原文入力テキストエリア */}
                <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    rows={10}
                    className="border p-3 w-4/5 max-w-3xl"
                    required
                    placeholder="ここに記事本文を入力"
                />

                {/* モード選択ラジオボタン */}
                <fieldset className="max-w-3xl mt-4">
                <div className="flex gap-6">
                    <label className="flex items-center gap-2 cursor-pointer">
                    <input
                        type="radio"
                        name="mode"
                        value="short"
                        checked={mode === "short"}
                        onChange={() => setMode("short")}
                    />
                    <span>短め</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                    <input
                        type="radio"
                        name="mode"
                        value="medium"
                        checked={mode === "medium"}
                        onChange={() => setMode("medium")}
                    />
                    <span>普通</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                    <input
                        type="radio"
                        name="mode"
                        value="long"
                        checked={mode === "long"}
                        onChange={() => setMode("long")}
                    />
                    <span>長め</span>
                    </label>
                </div>
                </fieldset>

                {/* 送信ボタン */}
                <button 
                    type="submit" 
                    className="bg-blue-500 text-white px-6 py-2 rounded mt-4 hover:bg-blue-600 w-32"
                >
                    {loading ? "要約中..." : "要約"}
                </button>
            </form>

            {/* エラー表示 */}
            {error && <div className="mt-4 text-red-600 w-4/5 max-w-3xl">{error}</div>}

        </main>

        {/* アウトプット表示エリア */}
        <section className="w-full bg-gray-100 min-h-screen py-8">
            <div className="flex flex-col items-center">

            {/* 結果表示 */}
            {summaries.map((s) => (
                <div
                    key={s.id}
                    className="relative mt-6 p-4 border-2 rounded bg-white w-4/5 max-w-3xl"
                >
                {/* ボタン群（枠の右外に縦列配置） */}
                <div className="absolute top-2 -right-8 flex flex-col gap-2">
                    <button
                        onClick={() => handleDelete(s.id)}
                        className="text-gray-500 hover:text-red-500"
                    >
                        ✕
                    </button>
                    <button
                        onClick={() => handleCopy(s.id, s.content)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                    📋
                    {/* コピーアイコンクリック時メッセージ */}
                    {copiedId === s.id && (
                    <span className="absolute left-full ml-2 text-xs text-pink-600 whitespace-nowrap">
                        Copied!
                    </span>
                    )}
                    </button>
                </div>

                {/* 要約本文 */}
                <p>{s.content}</p>
                </div>
            ))}

            </div>
        </section>
        </>

    );
}