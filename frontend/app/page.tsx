"use client";
import { useState } from "react";

export default function Home() {
    const [text, setText] = useState(``);
    const [summary, setSummary] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const res = await fetch("/api/summarize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });

        const data = await res.json();
        setSummary(data.summary);
    };

    return (
        <main className="p-8 flex flex-col items-center">
        {/* タイトル */}
        <h1 className="text-2xl font-bold mb-8 text-center">ニュース記事翻訳デモ</h1>

        {/* 入力フォーム */}
        <form onSubmit={handleSubmit} className="flex flex-col items-center w-full">
            <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                rows={10}
                className="border p-3 w-4/5 max-w-3xl"
                required
                placeholder="ここに記事本文を入力"
            />
            <button 
                type="submit" 
                className="bg-blue-500 text-white px-6 py-2 rounded mt-4 hover:bg-blue-600 w-32"
            >
                要約
            </button>
        </form>


        {/* 結果表示 */}
        {summary && (
            <div className="mt-6 p-4 border rounded w-4/5 max-w-3xl">
            <h2 className="font-bold mb-2">要約結果</h2>
            <p>{summary}</p>
            </div>
        )}
        </main>
    );
}