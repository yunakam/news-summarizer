# ニュース要約デモ

## 要約処理の流れ

1. **page.tsx → route.ts**

   * `page.tsx` 内で `fetch("/api/summarize", { method: "POST", body: JSON.stringify({ text }) })` が呼ばれる。
   * このリクエストは Next.js アプリ内部で `app/api/summarize/route.ts` にルーティングされる。

2. **route.ts → Django**

   * `route.ts` の `POST` 関数で `req.json()` から `text` を取得。
   * それを `http://localhost:8000/summarizer/summarize/` へ転送する（Django 側の API エンドポイント）。
   * この時 `Content-Type: application/json` ヘッダーを付与しているので、Django 側では `views.summarize` が JSON として解釈できる。

3. **Django → route.ts**

   * `views.py` の `summarize` 関数が `run_summary(text)` を実行し、`JsonResponse({"summary": summary})` を返す。

4. **route.ts → page.tsx**

   * Django から返ってきた JSON をそのまま `NextResponse.json({ summary: data.summary })` でフロントへ返す。

5. **page.tsx → UI へ表示**

   * `page.tsx` 側で `setSummary(data.summary)` を実行し、画面に要約が表示される。

---

### まとめると

* **page.tsx** → `/api/summarize` に POST
* **route.ts** → Django API (`http://localhost:8000/summarizer/summarize/`) に中継
* **views.py** → `run_summary` で要約 → JSON 返却
* **route.ts** → JSON を UI に返却
* **page.tsx** → `summary` を state に格納 → 画面に表示

---

