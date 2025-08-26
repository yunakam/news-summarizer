"use client";
import { useEffect, useState } from "react";

export default function Home() {

    // ===== 状態管理 =====
    const [text, setText] = useState<string>(""); 
    // ↑ ユーザーが直接入力した本文

    const [url, setUrl] = useState<string>(""); 
    // ↑ ユーザーが入力した記事URL

    const [summaries, setSummaries] = useState<
        { id: number; content: string}[]
    >([]); 
    // ↑ 要約結果を複数保持（削除・コピー機能のため配列にしている）

    const [mode, setMode] = useState<"short" | "medium" | "long">("medium");
    // ↑ 要約の長さモード（短め/普通/長め）

    const [loading, setLoading] = useState(false); 
    // ↑ ボタンに「要約中...」と表示するためのフラグ

    const [error, setError] = useState<string>(""); 
    // ↑ エラーメッセージ表示用


    // ===== ページ初期化時に localStorage からモードを復元 =====
    useEffect(() => {
        const savedMode = localStorage.getItem("summaryMode");
        if (savedMode === "short" || savedMode === "medium" || savedMode === "long") {
            setMode(savedMode);
        }
    }, []);

    // モードが変わるたび localStorage に保存
    useEffect(() => {
        localStorage.setItem("summaryMode", mode);
    }, [mode]);


    // ===== フォーム送信処理（要約ボタン押下時） =====
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        if (!text && !url) {
            setError("本文または記事URLを入力してください");
            setLoading(false);
            return;
            }

        try {
            let textToSummarize = text; // 最終的に要約APIに渡す本文

            // --- URL入力がある場合は、URLから本文抽出APIを呼ぶ ---
            if (url.startsWith("http://") || url.startsWith("https://")) {
                const resExtract = await fetch("/api/extract_article", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ url }), // DjangoにURLを渡す
                });

                if (!resExtract.ok) {
                    throw new Error("記事本文を取得できませんでした");
                }
                const dataExtract = await resExtract.json();
                textToSummarize = dataExtract.article || "";
            }

            if (!textToSummarize) {
                alert("本文が入力されていないか、記事本文を取得できませんでした");
                return;
            }

            // --- 要約APIを呼び出す ---
            const resSummary = await fetch("/api/summarize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: textToSummarize, mode }),
            });

            if (!resSummary.ok) {
                const msg = await resSummary.text();
                throw new Error(msg || "Server Error occurred.");
            }

            const dataSummary = await resSummary.json();

            // --- 要約結果をリストに追加 ---
            setSummaries((prev) => [
                ...prev,
                { id: Date.now(), content: dataSummary.summary },
            ]);

        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown Error");
        } finally {
            setLoading(false);
        }
    };


    // ===== コピー処理 =====
    const [copiedId, setCopiedId] = useState<number | null>(null);

    const handleCopy = (id: number, content: string) => {
        navigator.clipboard.writeText(content);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    // ===== 削除処理 =====
    const handleDelete = (id: number) => {
        setSummaries((prev) => prev.filter((s) => s.id !== id));
    };



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
                    placeholder="記事本文を入力"
                />

                {/* URL入力欄 */}
                <div className="mt-4 w-4/5 max-w-3xl">
                    <label className="block mb-2 font-semibold">
                        または記事のURLを貼り付け：
                    </label>
                    <input
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        className="border p-2 w-full"
                        placeholder="https://example.com/news/123"
                    />
                </div>                

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