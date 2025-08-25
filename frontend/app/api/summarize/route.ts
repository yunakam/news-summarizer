import { NextResponse } from "next/server";   // `NextResponse`はNext.jsのレスポンスオブジェクト

export async function POST(req: Request) {    // このAPIルートに対するPOSTメソッドの処理関数を定義

  const bodyText = await req.text();
    // await:req.text()の処理を待ってから、Promise関数を返す（awaitがないと結果が入らない空のオブジェクトが返される）
    // req: リクエストボディ。フロントからfetchで送信したJSONデータ(`body: JSON.stringify({ text, mode })`)

  if (!bodyText) {
    return NextResponse.json({ error: "empty body" }, { status: 400 });
  }

  let parsed;   // tryブロックの外でも parsed を使えるようにまず空で宣言
  try {
    parsed = JSON.parse(bodyText);
      // フロントからもらったリクエストボディ：{"text":"記事本文...","mode":"medium"}
      //  →　JavaScriptのオブジェクトに変換： { text: "記事本文...", mode: "medium" }
  } catch (e) {
    return NextResponse.json({ error: "invalid JSON" }, { status: 400 });
  }

  const { text, mode } = parsed;

  try {
    const res = await fetch("http://localhost:8000/summarizer/summarize/", {  // Djangoバックエンドのsummarize APIにリクエストを送る
      method: "POST",   // fetchはデフォルトでGETリクエストになるので、"POST"明示は必須
      headers: { "Content-Type": "application/json" },  // サーバーに送信するデータがJSON形式であることをヘッダで指定
      body: JSON.stringify({ text, mode }),                   // `text`, `mode` をJSON文字列に変換してリクエスト本文にセット
        // HTTPリクエストbodyはテキストやバイナリであり、JSON文字列に変換しないでサーバーに送るとエラー（JSONDecodeError等）が発生
    });

    if (!res.ok) {
      const errorText = await res.text(); // HTMLエラーの中身を見る
      return NextResponse.json({ error: errorText }, { status: res.status });
    }

    const data = await res.json();    // Django側から返ってきた JSONレスポンスを読み取り、 `data`に格納
    return NextResponse.json({ summary: data.summary });  // 要約結果 summary を JSONとしてフロントに返す
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 });  // 例外発生時にはエラーメッセージを JSON で返し、ステータスコード 500 を設定

    /*
    ここで行われている変換
    バックエンドの応答（HTTP Response）--`res.json()`-→ JSオブジェクト --`NextResponse.json()`-→ フロント向けの新しいHTTP Response
    
    これにより、以下が可能に：
    1. 形の正規化（最小限に整形）
    2．フロント側都合の制御（キャッシュ/ステータスコード/クッキー等）
    3. フロントとバックを分離 → 安全面・運用面の向上
    */

  }
}
